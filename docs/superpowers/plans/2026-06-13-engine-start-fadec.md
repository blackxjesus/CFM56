# A320 / CFM56-5B Engine Start & Failure Modes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a transient engine-start subsystem (FADEC-driven automatic start + CRANK dry-motoring + four failure modes) to the CFM56-5B simulator, surfaced as an animated A320 cockpit/ECAM sequence.

**Architecture:** Three pure-Python layers with a clean controller/plant split — a physics **plant** (`engine/start_transient.py`: HP-spool inertia ODE + empirical EGT/fuel correlations), a **FADEC + cockpit** controller (`engine/fadec.py`: state machine that issues control commands and detects faults, no auto-abort), and a **driver** (`simulate_start`) that loops them over time into a `StartTransient` time-series. The Streamlit app adds a cockpit panel + animated ECAM ENGINE page. Idle end-state is anchored to nominal defaults (optionally pulled from `lookup.pkl`).

**Tech Stack:** Python 3, dataclasses, `pytest`, Streamlit. No pyCycle/OpenMDAO at runtime — the start model is standalone.

---

## Physics & control reference (used by every task)

These are the agreed numeric constants and formulas. Use them verbatim.

**Plant constants (`PlantParams` defaults):**
```
inertia          = 25.0     # spool inertia scale (sets time constant)
k_drag           = 1.0      # linear drag coefficient
starter_torque   = 40.0     # starter torque scale at N2=0
starter_cutout   = 50.0     # % N2 where starter cuts out
lightoff_N2      = 18.0     # % N2 where FADEC introduces fuel
idle_N2          = 60.0     # % N2 at idle (turbine gain anchored to this)
idle_N1          = 19.0     # % N1 at idle
idle_EGT         = 450.0    # °C steady idle EGT
idle_FF          = 600.0    # kg/h idle fuel flow
idle_thrust      = 5.0      # kN idle thrust
ambient_EGT      = 15.0     # °C
egt_redline      = 725.0    # °C start limit
egt_bump         = 435.0    # °C light-off bump amplitude (normal)
bump_peak_N2     = 25.0     # % N2 where light-off EGT bump peaks
bump_width       = 9.0      # % N2 Gaussian width of bump
ff_min           = 0.35     # fuel fraction floor once lit
```
`turbine_gain` is DERIVED, not stored: `turbine_gain = k_drag * idle_N2` (= 60.0). This guarantees torque balance (and thus equilibrium) at idle.

**Fuel fraction schedule** `ff_frac(N2, ff_cap)` — fraction of idle fuel flow the FADEC schedules:
```
if N2 < lightoff_N2:  raw = 0.0
else:                 raw = ff_min + (1 - ff_min) * (N2 - lightoff_N2) / (0.9*idle_N2 - lightoff_N2)
return clamp(raw, 0.0, ff_cap)        # ff_cap = 1.0 normally, 0.7 for HUNG
```

**Torque / spool derivative** `dN2_dt(N2, lit, valve_open, p, ff_cap, bleed_factor)`:
```
Q_starter = starter_torque * bleed_factor * (1 - N2/starter_cutout)  if (valve_open and N2 < starter_cutout) else 0.0
Q_turbine = turbine_gain * ff_frac(N2, ff_cap)                        if lit else 0.0
Q_drag    = k_drag * N2
return (Q_starter + Q_turbine - Q_drag) / inertia
```

**EGT correlation** `egt(N2, lit, fuel_mult, p)`:
```
base = ambient_EGT + (idle_EGT - ambient_EGT) * clamp(N2/idle_N2, 0, 1)
if not lit:  return ambient_EGT
bump = egt_bump * fuel_mult * exp(-((N2 - bump_peak_N2)/bump_width)**2)
return base + bump
```

**Derived outputs:** `N1 = idle_N1 * clamp(N2/idle_N2, 0, 1)**1.5`; `thrust = idle_thrust * clamp(N2/idle_N2, 0, 1)**3`; `FF = ff_frac(N2, ff_cap) * idle_FF` if lit-or-fuel-flowing else `0`.

**Light-off rule:** engine becomes `lit` (and stays lit) the first timestep where `N2 >= lightoff_N2 AND fuel_cmd AND ignition_cmd AND fuel_valve_ok AND igniter_ok`.

**Scenario parameter injections** (`StartScenario`):
| Scenario | ff_cap | fuel_mult | fuel_valve_ok | igniter_ok | bleed_factor |
|---|---|---|---|---|---|
| NORMAL | 1.0 | 1.0 | True | True | 1.0 |
| HUNG | 0.7 | 1.0 | True | True | 1.0 |
| HOT | 1.0 | 1.8 | True | True | 1.0 |
| NO_FUEL | 1.0 | 1.0 | False | True | 1.0 |
| NO_IGNITION | 1.0 | 1.0 | True | False | 1.0 |

(`fuel_valve_ok=False` forces FF=0 and blocks light-off. `igniter_ok=False` blocks light-off but fuel still flows → FF>0, EGT ambient → wet start.)

**FADEC control law (per timestep), given CockpitConfig(mode, master_on, bleed_available):**
```
norm_start = mode in (NORM, IGN_START) and master_on and bleed_available
crank      = mode == CRANK and bleed_available
valve_open = (norm_start or crank) and N2 < starter_cutout
fuel_cmd   = norm_start and N2 >= lightoff_N2
ignition_cmd = norm_start and N2 >= lightoff_N2
```

**Fault detection (detect-only, raised once each):**
```
EGT EXCEEDANCE : EGT > egt_redline
HUNG START     : lit and N2 < 0.95*idle_N2 and |dN2_dt| < 0.05 sustained for 8 s
NO LIGHT-OFF   : fuel_cmd true for > 10 s and not lit and FF == 0
WET START      : fuel_cmd true for > 10 s and not lit and FF  > 0
```

**Driver:** `simulate_start(scenario, cockpit, idle_anchor=None, dt=0.5, t_max=180.0)` holds the cockpit config constant, integrates with RK4 (or forward Euler — Euler is acceptable here), records every timestep into a `StartTransient`, and stops early when `N2 >= 0.99*idle_N2` (normal complete) or a fault is stable.

---

## Task 1: `StartTransient` dataclass

**Files:**
- Modify: `engine/results.py`
- Test: `tests/test_start_results.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_start_results.py
import pytest
from engine.results import StartTransient


def test_start_transient_defaults_empty():
    st = StartTransient(scenario='NORMAL')
    assert st.scenario == 'NORMAL'
    assert st.t == []
    assert st.N2 == []
    assert st.events == []
    assert st.faults == []


def test_start_transient_append_frame():
    st = StartTransient(scenario='NORMAL')
    st.t.append(0.0)
    st.N2.append(0.0)
    st.EGT.append(15.0)
    assert st.N2[-1] == 0.0
    assert st.EGT[-1] == pytest.approx(15.0)


def test_start_transient_to_dataframe():
    st = StartTransient(scenario='NORMAL')
    st.t.extend([0.0, 0.5])
    st.N1.extend([0.0, 0.1]); st.N2.extend([0.0, 1.0])
    st.EGT.extend([15.0, 15.0]); st.FF.extend([0.0, 0.0])
    st.thrust.extend([0.0, 0.0])
    df = st.to_dataframe()
    assert len(df) == 2
    assert list(df.columns) == ['t', 'N1', 'N2', 'EGT', 'FF', 'thrust']
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_start_results.py -v`
Expected: FAIL with `ImportError: cannot import name 'StartTransient'`

- [ ] **Step 3: Add the dataclass**

Append to `engine/results.py`:
```python
from typing import List, Tuple


@dataclass
class StartTransient:
    scenario: str
    t: List[float] = field(default_factory=list)        # s
    N1: List[float] = field(default_factory=list)       # %
    N2: List[float] = field(default_factory=list)       # %
    EGT: List[float] = field(default_factory=list)      # °C
    FF: List[float] = field(default_factory=list)       # kg/h
    thrust: List[float] = field(default_factory=list)   # kN
    start_valve: List[bool] = field(default_factory=list)
    igniter: List[bool] = field(default_factory=list)
    eng_mode: List[str] = field(default_factory=list)
    master: List[bool] = field(default_factory=list)
    events: List[Tuple[float, str]] = field(default_factory=list)
    faults: List[str] = field(default_factory=list)

    def to_dataframe(self):
        import pandas as pd
        return pd.DataFrame({
            't': self.t, 'N1': self.N1, 'N2': self.N2,
            'EGT': self.EGT, 'FF': self.FF, 'thrust': self.thrust,
        })
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_start_results.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add engine/results.py tests/test_start_results.py
git commit -m "feat: add StartTransient dataclass for start time-series"
```

---

## Task 2: Plant params, scenario enum, and fuel schedule

**Files:**
- Create: `engine/start_transient.py`
- Test: `tests/test_start_plant.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_start_plant.py
import math
import pytest
from engine.start_transient import PlantParams, StartScenario, scenario_params, ff_frac


def test_plant_params_turbine_gain_anchored_to_idle():
    p = PlantParams()
    assert p.turbine_gain == pytest.approx(p.k_drag * p.idle_N2)


def test_scenario_params_normal():
    sp = scenario_params(StartScenario.NORMAL)
    assert sp == {'ff_cap': 1.0, 'fuel_mult': 1.0,
                  'fuel_valve_ok': True, 'igniter_ok': True, 'bleed_factor': 1.0}


def test_scenario_params_hung_caps_fuel():
    assert scenario_params(StartScenario.HUNG)['ff_cap'] == pytest.approx(0.7)


def test_scenario_params_no_fuel_blocks_valve():
    assert scenario_params(StartScenario.NO_FUEL)['fuel_valve_ok'] is False


def test_ff_frac_zero_below_lightoff():
    p = PlantParams()
    assert ff_frac(10.0, 1.0, p) == 0.0


def test_ff_frac_floor_at_lightoff():
    p = PlantParams()
    assert ff_frac(p.lightoff_N2, 1.0, p) == pytest.approx(p.ff_min)


def test_ff_frac_capped_for_hung():
    p = PlantParams()
    assert ff_frac(p.idle_N2, 0.7, p) == pytest.approx(0.7)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_start_plant.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'engine.start_transient'`

- [ ] **Step 3: Create the module**

```python
# engine/start_transient.py
"""
CFM56-5B transient engine-start plant model (pure Python, no pyCycle).

Reduced-order HP-spool inertia ODE + empirical EGT/fuel correlations.
See docs/superpowers/specs/2026-06-13-engine-start-fadec-design.md.
"""
import math
from dataclasses import dataclass
from enum import Enum


class StartScenario(Enum):
    NORMAL = 'NORMAL'
    HUNG = 'HUNG'
    HOT = 'HOT'
    NO_FUEL = 'NO_FUEL'
    NO_IGNITION = 'NO_IGNITION'


@dataclass
class PlantParams:
    inertia: float = 25.0
    k_drag: float = 1.0
    starter_torque: float = 40.0
    starter_cutout: float = 50.0
    lightoff_N2: float = 18.0
    idle_N2: float = 60.0
    idle_N1: float = 19.0
    idle_EGT: float = 450.0
    idle_FF: float = 600.0
    idle_thrust: float = 5.0
    ambient_EGT: float = 15.0
    egt_redline: float = 725.0
    egt_bump: float = 435.0
    bump_peak_N2: float = 25.0
    bump_width: float = 9.0
    ff_min: float = 0.35

    @property
    def turbine_gain(self) -> float:
        return self.k_drag * self.idle_N2


def scenario_params(scenario: StartScenario) -> dict:
    table = {
        StartScenario.NORMAL:      dict(ff_cap=1.0, fuel_mult=1.0, fuel_valve_ok=True,  igniter_ok=True,  bleed_factor=1.0),
        StartScenario.HUNG:        dict(ff_cap=0.7, fuel_mult=1.0, fuel_valve_ok=True,  igniter_ok=True,  bleed_factor=1.0),
        StartScenario.HOT:         dict(ff_cap=1.0, fuel_mult=1.8, fuel_valve_ok=True,  igniter_ok=True,  bleed_factor=1.0),
        StartScenario.NO_FUEL:     dict(ff_cap=1.0, fuel_mult=1.0, fuel_valve_ok=False, igniter_ok=True,  bleed_factor=1.0),
        StartScenario.NO_IGNITION: dict(ff_cap=1.0, fuel_mult=1.0, fuel_valve_ok=True,  igniter_ok=False, bleed_factor=1.0),
    }
    return table[scenario]


def _clamp(x, lo, hi):
    return max(lo, min(hi, x))


def ff_frac(N2: float, ff_cap: float, p: PlantParams) -> float:
    if N2 < p.lightoff_N2:
        return 0.0
    span = 0.9 * p.idle_N2 - p.lightoff_N2
    raw = p.ff_min + (1.0 - p.ff_min) * (N2 - p.lightoff_N2) / span
    return _clamp(raw, 0.0, ff_cap)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_start_plant.py -v`
Expected: PASS (7 passed)

- [ ] **Step 5: Commit**

```bash
git add engine/start_transient.py tests/test_start_plant.py
git commit -m "feat: add start plant params, scenario enum, fuel schedule"
```

---

## Task 3: Spool dynamics, EGT, and output correlations

**Files:**
- Modify: `engine/start_transient.py`
- Test: `tests/test_start_plant.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_start_plant.py`:
```python
from engine.start_transient import dN2_dt, egt, derived_outputs


def test_torque_balances_at_idle_when_lit():
    p = PlantParams()
    # at idle, valve closed (N2 >= cutout), lit, full fuel -> net torque ~ 0
    rate = dN2_dt(p.idle_N2, lit=True, valve_open=False, p=p, ff_cap=1.0, bleed_factor=1.0)
    assert abs(rate) < 1e-6


def test_accelerates_from_zero_with_starter():
    p = PlantParams()
    rate = dN2_dt(0.0, lit=False, valve_open=True, p=p, ff_cap=1.0, bleed_factor=1.0)
    assert rate > 0.0


def test_motoring_plateau_no_fuel():
    # with starter only (not lit), spool stalls where starter torque == drag
    p = PlantParams()
    rate_low = dN2_dt(10.0, lit=False, valve_open=True, p=p, ff_cap=1.0, bleed_factor=1.0)
    rate_high = dN2_dt(30.0, lit=False, valve_open=True, p=p, ff_cap=1.0, bleed_factor=1.0)
    assert rate_low > 0.0 and rate_high < 0.0   # plateau between 10% and 30%


def test_egt_ambient_when_not_lit():
    p = PlantParams()
    assert egt(20.0, lit=False, fuel_mult=1.0, p=p) == pytest.approx(p.ambient_EGT)


def test_egt_lightoff_bump_below_redline_normal():
    p = PlantParams()
    peak = egt(p.bump_peak_N2, lit=True, fuel_mult=1.0, p=p)
    assert 500.0 < peak < p.egt_redline


def test_egt_hot_start_exceeds_redline():
    p = PlantParams()
    peak = egt(p.bump_peak_N2, lit=True, fuel_mult=1.8, p=p)
    assert peak > p.egt_redline


def test_derived_outputs_at_idle():
    p = PlantParams()
    n1, thr, ff = derived_outputs(p.idle_N2, lit=True, fuel_flowing=True, ff_cap=1.0, p=p)
    assert n1 == pytest.approx(p.idle_N1, rel=0.05)
    assert ff == pytest.approx(p.idle_FF, rel=0.05)
    assert thr == pytest.approx(p.idle_thrust, rel=0.05)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_start_plant.py -v`
Expected: FAIL with `ImportError: cannot import name 'dN2_dt'`

- [ ] **Step 3: Add the functions**

Append to `engine/start_transient.py`:
```python
def dN2_dt(N2, lit, valve_open, p, ff_cap, bleed_factor):
    if valve_open and N2 < p.starter_cutout:
        q_starter = p.starter_torque * bleed_factor * (1.0 - N2 / p.starter_cutout)
    else:
        q_starter = 0.0
    q_turbine = p.turbine_gain * ff_frac(N2, ff_cap, p) if lit else 0.0
    q_drag = p.k_drag * N2
    return (q_starter + q_turbine - q_drag) / p.inertia


def egt(N2, lit, fuel_mult, p):
    if not lit:
        return p.ambient_EGT
    base = p.ambient_EGT + (p.idle_EGT - p.ambient_EGT) * _clamp(N2 / p.idle_N2, 0.0, 1.0)
    bump = p.egt_bump * fuel_mult * math.exp(-((N2 - p.bump_peak_N2) / p.bump_width) ** 2)
    return base + bump


def derived_outputs(N2, lit, fuel_flowing, ff_cap, p):
    frac = _clamp(N2 / p.idle_N2, 0.0, 1.0)
    n1 = p.idle_N1 * frac ** 1.5
    thrust = p.idle_thrust * frac ** 3
    ff = ff_frac(N2, ff_cap, p) * p.idle_FF if (lit or fuel_flowing) else 0.0
    return n1, thrust, ff
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_start_plant.py -v`
Expected: PASS (14 passed)

- [ ] **Step 5: Commit**

```bash
git add engine/start_transient.py tests/test_start_plant.py
git commit -m "feat: add spool dynamics, EGT correlation, output derivations"
```

---

## Task 4: FADEC cockpit config and control law

**Files:**
- Create: `engine/fadec.py`
- Test: `tests/test_fadec.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_fadec.py
import pytest
from engine.fadec import EngMode, CockpitConfig, fadec_commands
from engine.start_transient import PlantParams

P = PlantParams()


def test_valve_opens_on_norm_master_bleed():
    cfg = CockpitConfig(mode=EngMode.IGN_START, master_on=True, bleed_available=True)
    cmd = fadec_commands(N2=5.0, cfg=cfg, p=P)
    assert cmd['valve_open'] is True
    assert cmd['fuel_cmd'] is False        # below light-off N2


def test_no_valve_without_bleed():
    cfg = CockpitConfig(mode=EngMode.IGN_START, master_on=True, bleed_available=False)
    cmd = fadec_commands(N2=5.0, cfg=cfg, p=P)
    assert cmd['valve_open'] is False


def test_fuel_and_ignition_at_lightoff_n2():
    cfg = CockpitConfig(mode=EngMode.IGN_START, master_on=True, bleed_available=True)
    cmd = fadec_commands(N2=P.lightoff_N2, cfg=cfg, p=P)
    assert cmd['fuel_cmd'] is True
    assert cmd['ignition_cmd'] is True


def test_valve_closes_at_cutout():
    cfg = CockpitConfig(mode=EngMode.IGN_START, master_on=True, bleed_available=True)
    cmd = fadec_commands(N2=P.starter_cutout, cfg=cfg, p=P)
    assert cmd['valve_open'] is False


def test_crank_motors_without_fuel_or_ignition():
    cfg = CockpitConfig(mode=EngMode.CRANK, master_on=False, bleed_available=True)
    cmd = fadec_commands(N2=30.0, cfg=cfg, p=P)
    assert cmd['valve_open'] is True
    assert cmd['fuel_cmd'] is False
    assert cmd['ignition_cmd'] is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_fadec.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'engine.fadec'`

- [ ] **Step 3: Create the module**

```python
# engine/fadec.py
"""
A320 / CFM56-5B FADEC + cockpit control logic (detect-only, no auto-abort).

Holds the cockpit panel state and turns it (plus N2 feedback) into plant
control commands. See docs/superpowers/specs/2026-06-13-engine-start-fadec-design.md.
"""
from dataclasses import dataclass
from enum import Enum


class EngMode(Enum):
    NORM = 'NORM'
    IGN_START = 'IGN_START'
    CRANK = 'CRANK'


@dataclass
class CockpitConfig:
    mode: EngMode = EngMode.IGN_START
    master_on: bool = True
    bleed_available: bool = True


def fadec_commands(N2, cfg, p):
    norm_start = cfg.mode in (EngMode.NORM, EngMode.IGN_START) and cfg.master_on and cfg.bleed_available
    crank = cfg.mode == EngMode.CRANK and cfg.bleed_available
    valve_open = (norm_start or crank) and N2 < p.starter_cutout
    fuel_cmd = norm_start and N2 >= p.lightoff_N2
    ignition_cmd = norm_start and N2 >= p.lightoff_N2
    return {'valve_open': valve_open, 'fuel_cmd': fuel_cmd, 'ignition_cmd': ignition_cmd}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_fadec.py -v`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add engine/fadec.py tests/test_fadec.py
git commit -m "feat: add FADEC cockpit config and control law"
```

---

## Task 5: Driver `simulate_start` (normal start integration)

**Files:**
- Modify: `engine/start_transient.py`
- Test: `tests/test_simulate_start.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_simulate_start.py
import pytest
from engine.start_transient import simulate_start, StartScenario
from engine.fadec import EngMode, CockpitConfig

NORMAL_COCKPIT = CockpitConfig(mode=EngMode.IGN_START, master_on=True, bleed_available=True)


def test_normal_start_reaches_idle():
    st = simulate_start(StartScenario.NORMAL, NORMAL_COCKPIT)
    assert st.N2[-1] >= 0.99 * 60.0          # idle_N2
    assert st.N2[-1] <= 60.0 * 1.02


def test_normal_start_time_plausible():
    st = simulate_start(StartScenario.NORMAL, NORMAL_COCKPIT)
    assert 20.0 <= st.t[-1] <= 150.0         # seconds to idle


def test_normal_start_egt_peak_below_redline():
    st = simulate_start(StartScenario.NORMAL, NORMAL_COCKPIT)
    assert max(st.EGT) < 725.0


def test_time_monotonic_and_no_nans():
    import math
    st = simulate_start(StartScenario.NORMAL, NORMAL_COCKPIT)
    assert all(st.t[i] < st.t[i + 1] for i in range(len(st.t) - 1))
    assert all(not math.isnan(v) for v in st.N2 + st.EGT + st.FF)


def test_events_logged_in_order():
    st = simulate_start(StartScenario.NORMAL, NORMAL_COCKPIT)
    labels = [lbl for _, lbl in st.events]
    assert 'STARTER ON' in labels
    assert 'LIGHT-OFF' in labels
    assert 'IDLE' in labels
    assert labels.index('STARTER ON') < labels.index('LIGHT-OFF') < labels.index('IDLE')
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_simulate_start.py -v`
Expected: FAIL with `ImportError: cannot import name 'simulate_start'`

- [ ] **Step 3: Add the driver**

Append to `engine/start_transient.py` (add `from engine.results import StartTransient` and `from engine.fadec import fadec_commands` at top of file):
```python
def _idle_defaults(p):
    return {'idle_N2': p.idle_N2, 'idle_N1': p.idle_N1, 'idle_EGT': p.idle_EGT,
            'idle_FF': p.idle_FF, 'idle_thrust': p.idle_thrust}


def simulate_start(scenario, cockpit, idle_anchor=None, dt=0.5, t_max=180.0,
                   params=None):
    from engine.results import StartTransient
    from engine.fadec import fadec_commands

    p = params or PlantParams()
    if idle_anchor:
        for k, v in idle_anchor.items():
            setattr(p, k.replace('idle_', 'idle_'), v) if hasattr(p, k) else None
    sp = scenario_params(scenario)

    st = StartTransient(scenario=scenario.value)
    N2 = 0.0
    lit = False
    t = 0.0
    seen = set()
    hung_timer = 0.0
    nolight_timer = 0.0

    def log(label):
        if label not in seen:
            seen.add(label)
            st.events.append((round(t, 1), label))

    while t <= t_max:
        cmd = fadec_commands(N2, cockpit, p)
        valve, fuel_cmd, ign_cmd = cmd['valve_open'], cmd['fuel_cmd'], cmd['ignition_cmd']

        # light-off
        can_light = (N2 >= p.lightoff_N2 and fuel_cmd and ign_cmd
                     and sp['fuel_valve_ok'] and sp['igniter_ok'])
        if can_light and not lit:
            lit = True
            log('LIGHT-OFF')

        fuel_flowing = fuel_cmd and sp['fuel_valve_ok']  # fuel present even if not lit
        n1, thrust, ff = derived_outputs(N2, lit, fuel_flowing, sp['ff_cap'], p)
        if not sp['fuel_valve_ok']:
            ff = 0.0
        egt_v = egt(N2, lit, sp['fuel_mult'], p)

        # record frame
        st.t.append(round(t, 3)); st.N1.append(n1); st.N2.append(N2)
        st.EGT.append(egt_v); st.FF.append(ff); st.thrust.append(thrust)
        st.start_valve.append(valve); st.igniter.append(bool(ign_cmd))
        st.eng_mode.append(cockpit.mode.value); st.master.append(cockpit.master_on)

        # events
        if valve:
            log('STARTER ON')
        if ign_cmd:
            log('IGNITION ON')
        if 'STARTER ON' in seen and not valve and N2 >= p.lightoff_N2:
            log('STARTER CUTOUT')

        # faults (Task 6 fills logic; placeholder hooks kept minimal here)
        rate = dN2_dt(N2, lit, valve, p, sp['ff_cap'], sp['bleed_factor'])

        # completion
        if N2 >= 0.99 * p.idle_N2:
            log('IDLE')
            break

        N2 = max(0.0, N2 + rate * dt)
        t += dt

    return st
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_simulate_start.py -v`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add engine/start_transient.py tests/test_simulate_start.py
git commit -m "feat: add simulate_start driver for normal start"
```

---

## Task 6: Fault detection in the driver

**Files:**
- Modify: `engine/start_transient.py`
- Test: `tests/test_start_faults.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_start_faults.py
import pytest
from engine.start_transient import simulate_start, StartScenario
from engine.fadec import EngMode, CockpitConfig

COCKPIT = CockpitConfig(mode=EngMode.IGN_START, master_on=True, bleed_available=True)


def test_hung_start_stagnates_below_idle():
    st = simulate_start(StartScenario.HUNG, COCKPIT)
    assert st.N2[-1] < 0.95 * 60.0
    assert 'HUNG START' in st.faults


def test_hot_start_exceeds_redline():
    st = simulate_start(StartScenario.HOT, COCKPIT)
    assert max(st.EGT) > 725.0
    assert 'EGT EXCEEDANCE' in st.faults


def test_no_fuel_motors_with_ambient_egt():
    st = simulate_start(StartScenario.NO_FUEL, COCKPIT)
    assert st.N2[-1] < 30.0                  # motoring plateau
    assert max(st.EGT) <= 16.0               # ambient ~15 °C
    assert max(st.FF) == 0.0
    assert 'NO LIGHT-OFF' in st.faults


def test_no_ignition_wet_start():
    st = simulate_start(StartScenario.NO_IGNITION, COCKPIT)
    assert max(st.EGT) <= 16.0               # no combustion
    assert max(st.FF) > 0.0                  # fuel flowing
    assert 'WET START' in st.faults
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_start_faults.py -v`
Expected: FAIL (faults list empty; assertions on `'... ' in st.faults` fail)

- [ ] **Step 3: Add fault logic to the loop**

In `simulate_start`, replace the `# faults` comment block and the completion section with this fuller version (insert before `# completion`):
```python
        # --- fault detection (detect-only) ---
        if egt_v > p.egt_redline and 'EGT EXCEEDANCE' not in st.faults:
            st.faults.append('EGT EXCEEDANCE')
            log('EGT EXCEEDANCE')

        if lit and N2 < 0.95 * p.idle_N2 and abs(rate) < 0.05:
            hung_timer += dt
            if hung_timer >= 8.0 and 'HUNG START' not in st.faults:
                st.faults.append('HUNG START')
                log('HUNG START')
        else:
            hung_timer = 0.0

        if fuel_cmd and not lit:
            nolight_timer += dt
            if nolight_timer >= 10.0:
                if ff > 0.0 and 'WET START' not in st.faults:
                    st.faults.append('WET START')
                    log('WET START')
                elif ff == 0.0 and 'NO LIGHT-OFF' not in st.faults:
                    st.faults.append('NO LIGHT-OFF')
                    log('NO LIGHT-OFF')
        else:
            nolight_timer = 0.0

        # stop if a stable fault has been latched and spool is settled
        stuck = abs(rate) < 0.02 and N2 < 0.95 * p.idle_N2
        if st.faults and stuck and t > 20.0:
            break
```

Note: for HUNG, `fuel_cmd` is true and the engine *is* lit, so the no-light timers don't fire; only the HUNG branch latches. For NO_FUEL the engine never lights and `ff == 0` → NO LIGHT-OFF. For NO_IGNITION the engine never lights but `ff > 0` → WET START. Keep `t_max` high enough (180 s) that the timers elapse.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_start_faults.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Run the full suite**

Run: `pytest tests/ -v`
Expected: all start/fadec tests PASS (pre-existing pyCycle tests may skip/error if pyCycle absent — that is unrelated to this work; note but do not fix here).

- [ ] **Step 6: Commit**

```bash
git add engine/start_transient.py tests/test_start_faults.py
git commit -m "feat: add FADEC fault detection for the four start failure modes"
```

---

## Task 7: Optional idle anchor from lookup + package exports

**Files:**
- Modify: `engine/start_transient.py`
- Modify: `engine/__init__.py`
- Test: `tests/test_start_anchor.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_start_anchor.py
from engine.start_transient import idle_anchor_from_results


class _Stub:
    def __init__(self, thrust_kN, fuel_flow):
        self.thrust_kN = thrust_kN
        self.fuel_flow = fuel_flow   # kg/s


def test_idle_anchor_from_results_converts_units():
    r = _Stub(thrust_kN=4.2, fuel_flow=0.15)   # 0.15 kg/s -> 540 kg/h
    anchor = idle_anchor_from_results(r)
    assert anchor['idle_thrust'] == 4.2
    assert anchor['idle_FF'] == 540.0


def test_package_exports_start_symbols():
    import engine
    assert hasattr(engine, 'simulate_start')
    assert hasattr(engine, 'StartScenario')
    assert hasattr(engine, 'StartTransient')
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_start_anchor.py -v`
Expected: FAIL with `ImportError: cannot import name 'idle_anchor_from_results'`

- [ ] **Step 3: Add the helper and exports**

Append to `engine/start_transient.py`:
```python
def idle_anchor_from_results(result):
    """Build an idle-anchor dict from an EngineResults idle point.

    Only thrust and fuel flow are reliably transferable; N2/N1/EGT idle
    targets stay at PlantParams defaults unless explicitly provided.
    """
    return {'idle_thrust': float(result.thrust_kN),
            'idle_FF': float(result.fuel_flow) * 3600.0}
```

Append to `engine/__init__.py` (keep it pyCycle-free — these imports are pure Python):
```python
from engine.results import StartTransient
from engine.start_transient import (
    simulate_start, StartScenario, PlantParams, idle_anchor_from_results,
)
from engine.fadec import EngMode, CockpitConfig
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_start_anchor.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Verify the package still imports without pyCycle**

Run: `python -c "import engine; print(engine.simulate_start, engine.StartScenario)"`
Expected: prints the function and enum without raising (no openmdao/pycycle import error).

- [ ] **Step 6: Commit**

```bash
git add engine/start_transient.py engine/__init__.py tests/test_start_anchor.py
git commit -m "feat: add idle-anchor helper and pure-Python start exports"
```

---

## Task 8: Streamlit cockpit panel + animated ECAM ENGINE start page

**Files:**
- Modify: `app.py`
- (No automated test — Streamlit UI; verified manually.)

- [ ] **Step 1: Add an Engine Start mode toggle and cockpit panel**

Near the top of `app.py` after the existing imports add:
```python
from engine import simulate_start, StartScenario, CockpitConfig, EngMode
```

After the `st.title(...)` / `st.caption(...)` block, add a mode switch:
```python
app_mode = st.radio('Mode', ['Steady-State', '🔥 Engine Start'], horizontal=True)
```

Wrap the EXISTING control + ECAM + diagram code (everything from `col_ctrl, col_ecam = st.columns(...)` to the end) in:
```python
if app_mode == 'Steady-State':
    # ... existing code unchanged, indented one level ...
```

- [ ] **Step 2: Add the Engine Start branch**

After the steady-state block, append:
```python
else:  # 🔥 Engine Start
    st.subheader('A320 Engine Start — FADEC Sequence')

    cc1, cc2, cc3, cc4 = st.columns(4)
    with cc1:
        mode = st.selectbox('ENG MODE', ['IGN/START', 'NORM', 'CRANK'])
    with cc2:
        master = st.toggle('ENG MASTER 1', value=True)
    with cc3:
        bleed = st.toggle('APU BLEED', value=True)
    with cc4:
        scenario_name = st.selectbox(
            'Scenario',
            ['NORMAL', 'HUNG', 'HOT', 'NO_FUEL', 'NO_IGNITION'],
            help='Inject a start fault (root cause); the FADEC detects the symptom.',
        )

    mode_map = {'IGN/START': EngMode.IGN_START, 'NORM': EngMode.NORM, 'CRANK': EngMode.CRANK}
    cockpit = CockpitConfig(mode=mode_map[mode], master_on=master, bleed_available=bleed)
    scenario = StartScenario[scenario_name]

    st_data = simulate_start(scenario, cockpit)

    if not st_data.t:
        st.warning('No start sequence — check ENG MODE / MASTER / APU BLEED.')
    else:
        frame = st.slider('Time [s]', 0.0, float(st_data.t[-1]),
                          0.0, step=float(st_data.t[1] - st_data.t[0]))
        i = min(range(len(st_data.t)), key=lambda k: abs(st_data.t[k] - frame))

        g1, g2 = st.columns([1, 1])
        with g1:
            components.html(start_ecam_html(st_data, i), height=360)
        with g2:
            import pandas as pd
            df = st_data.to_dataframe().set_index('t')
            st.line_chart(df[['N1', 'N2']])
            st.line_chart(df[['EGT']])

        events_so_far = [f'{t:.1f}s — {lbl}' for t, lbl in st_data.events if t <= frame]
        st.write('  ·  '.join(events_so_far) or '— standby —')
        if st_data.faults:
            st.error('FADEC fault: ' + ', '.join(st_data.faults))
```

- [ ] **Step 3: Add the `start_ecam_html` renderer**

Add this function alongside the existing `ecam_html` in `app.py`:
```python
def start_ecam_html(st_data, i):
    n1 = st_data.N1[i]; n2 = st_data.N2[i]
    egt = st_data.EGT[i]; ff = st_data.FF[i]
    valve = st_data.start_valve[i]; ign = st_data.igniter[i]
    egt_col = '#ff3030' if egt > 700 else ('#ffaa00' if egt > 500 else '#00ff00')
    rows = [
        ('N1',  f'{n1:.1f}', '#00ff00', '%'),
        ('N2',  f'{n2:.1f}', '#00cc00', '%'),
        ('EGT', f'{egt:.0f}', egt_col, '°C'),
        ('FF',  f'{ff:.0f}', '#00e000', 'KG/H'),
    ]
    inner = ''
    for lbl, v, col, unit in rows:
        inner += f"""<div style="display:flex;justify-content:space-between;
            align-items:baseline;margin:6px 0;border-bottom:1px solid #1a1a1a;">
            <span style="color:#888;font-size:12px;width:46px;">{lbl}</span>
            <span style="font-size:26px;color:{col};font-weight:bold;">{v}</span>
            <span style="color:#555;font-size:10px;width:55px;text-align:right;">{unit}</span>
            </div>"""
    valve_txt = f'<span style="color:{"#00ff00" if valve else "#555"}">STARTER VALVE {"OPEN" if valve else "CLOSED"}</span>'
    ign_txt = f'<span style="color:{"#00ff00" if ign else "#555"}">IGN {"A/B" if ign else "OFF"}</span>'
    return f"""<div style="background:#050505;font-family:'Courier New',monospace;
        border:2px solid #444;border-radius:8px;padding:16px 20px;min-width:360px;">
        <div style="color:#00aaff;font-size:12px;letter-spacing:2px;
            border-bottom:1px solid #333;padding-bottom:8px;margin-bottom:10px;">
            ── ENGINE 1 · START ──</div>
        {inner}
        <div style="margin-top:12px;font-size:11px;display:flex;justify-content:space-between;">
            {valve_txt}{ign_txt}</div>
        </div>"""
```

- [ ] **Step 4: Verify the app runs and the sequence animates**

Run: `streamlit run app.py` (or `python -m streamlit run app.py`)
Manually verify:
- Toggle to **🔥 Engine Start**. With IGN/START + MASTER on + APU BLEED on, scrubbing the time slider shows N2 rising, light-off EGT bump, then idle.
- **CRANK** mode: N2 motors up, EGT stays ambient, no light-off.
- **HOT** scenario: EGT crosses into red and "EGT EXCEEDANCE" fault shows.
- **NO_FUEL** / **NO_IGNITION**: N2 plateaus low; correct fault banner.
- Turning **APU BLEED off**: warning shown, no start.

- [ ] **Step 5: Commit**

```bash
git add app.py
git commit -m "feat: add animated A320 engine-start cockpit + ECAM page to app"
```

---

## Task 9: Documentation

**Files:**
- Modify: `DOKUMENTACIO.md`

- [ ] **Step 1: Document the start subsystem**

Add a section to `DOKUMENTACIO.md` describing: the three-layer architecture (plant / FADEC / driver), the reduced-order spool ODE and EGT correlation, the four failure modes and their root-cause injections, the cockpit controls (ENG MODE / MASTER / APU BLEED), and how to run/animate it in the app. Keep it consistent with the Hungarian terminology from the spec (hidegfennakadás, melegfennakadás, nincs üzemanyagbetáplálás, nincs gyújtás).

- [ ] **Step 2: Commit**

```bash
git add DOKUMENTACIO.md
git commit -m "docs: document the engine-start subsystem and failure modes"
```

---

## Self-Review notes (addressed)

- **Spec coverage:** plant ODE (Task 3), empirical EGT/fuel (Tasks 2–3), FADEC sequence + CRANK (Task 4), driver + events (Task 5), all four faults with detect-only flags (Task 6), idle anchor from lookup (Task 7), cockpit panel + animated ECAM (Task 8), docs (Task 9). All spec sections map to a task.
- **Type consistency:** `PlantParams`, `StartScenario`, `ff_frac`, `dN2_dt`, `egt`, `derived_outputs`, `scenario_params`, `simulate_start`, `CockpitConfig`, `EngMode`, `fadec_commands`, `StartTransient`, `idle_anchor_from_results` — names used identically across all tasks.
- **Torque balance:** `turbine_gain = k_drag*idle_N2` and `ff_frac` saturating below idle guarantee a stable equilibrium at `idle_N2`; HUNG caps `ff_cap=0.7` → stagnation ~42% N2; motoring (no fuel) stalls ~22% N2. Verified by the unit tests in Tasks 3 and 6.
- **Deployment safety:** all new code is pure Python; `engine/__init__.py` additions import no pyCycle/OpenMDAO (Task 7 Step 5 verifies).
