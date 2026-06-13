# A320 / CFM56-5B Engine Start & Failure Modes — Design Spec

**Date:** 2026-06-13
**Status:** Approved (brainstorming) — pending implementation plan

## 1. Purpose

Add a transient **engine start sequence** and **start failure modes** to the
existing CFM56-5B simulator, modelled the way the real A320 runs it: the FADEC
drives an automatic start through the cockpit controls (ENG MODE, ENG MASTER,
APU bleed), and the ECAM ENGINE page animates through the sequence.

Two goals, jointly: a defensible (thesis-grade) transient model **and** an
interactive animated demo in the Streamlit app.

The four required failure modes (Hungarian terms from the assignment):

| Failure | Meaning | Gauge signature |
|---|---|---|
| **Hidegfennakadás** (hung / cold hang) | Lights off but N2 stagnates *below* idle (insufficient torque margin / low bleed). | N2 flatlines sub-idle, EGT stable but elevated, never reaches idle. |
| **Melegfennakadás** (hot start) | Excess fuel / too little airflow at light-off → EGT spikes past the start redline. | EGT shoots up past ~725 °C; exceedance flagged. |
| **Nincs üzemanyagbetáplálás** (no fuel) | Starter motors N2 but no light-off (fuel valve fault). | N2 rises then plateaus at motoring speed, EGT ambient, FF = 0. |
| **Nincs gyújtás** (no ignition) | Fuel flows but no spark — no light-off, fuel pools (wet-start risk). | N2 motoring, FF present, EGT ambient; wet-start flag. |

## 2. Context & key constraint

- The existing model (`engine/cfm56.py`, `engine/simulation.py`) is a **steady-state**
  pyCycle/OpenMDAO solver. "Throttle" is a T4 override (1000 K idle → 1700 K TOGA).
- The deployed Streamlit app does **not** run pyCycle — it reads a precomputed
  `data/lookup.pkl` keyed by `(phase, throttle)` → `EngineResults`.
- Engine start happens **below idle**, outside the steady-state model's valid
  envelope, and is inherently time-domain (rotor inertia). It cannot be produced
  by "running the cycle over time."

**Consequence:** the start subsystem is new, pure-Python, and runs **live** in
the deployed app. Its only link to pyCycle is the **idle end-state**, which is
already present in `lookup.pkl` (the throttle-0 point for the selected phase).

## 3. Architecture — three layers (controller / plant split)

### Layer 1 — Plant: `engine/start_transient.py`
Pure transient physics. Knows nothing about cockpit or FADEC.

**Hybrid model: HP-spool inertia ODE + empirical EGT/fuel correlations.**

Single HP-spool dynamics, integrated with RK4:

```
I · dω/dt = Q_starter(N2) + Q_turbine(N2, FF, lit) − Q_drag(N2)
```

- **Q_starter(N2)** — pneumatic air-turbine-starter torque schedule; high at low
  N2, decays, cut to zero at starter-cutout N2 (~50%). Scaled by available bleed.
- **Q_turbine(N2, FF, lit)** — zero until light-off (`lit`); afterwards scales
  with burned fuel energy and N2.
- **Q_drag(N2)** — compressor + parasitic drag, ~N2².
- Normal equilibrium lands at the **idle N2 taken from the lookup table**.

Empirical overlays, calibrated to representative CFM56-5B start data:
- **Fuel schedule** `FF(N2)` — FCU acceleration schedule; opens at ~16–20% N2.
- **EGT correlation** — ambient before light-off; a light-off spike then decay
  toward steady start EGT as N2-driven airflow rises; driven by fuel/air ratio.
  Start redline ≈ **725 °C** used as the hot-start threshold.
- **N1(N2)** — LP spool follows HP; reuses the existing estimate style.

Interface (illustrative):
```python
def plant_step(state, controls, params, dt) -> state
# state:    N2, N1, EGT, FF, thrust, lit, t
# controls: start_valve_open: bool, fuel_cmd: bool, ignition_on: bool
# params:   inertia, torque coeffs, EGT coeffs, idle anchor, fault injections
```

### Layer 2 — Systems + FADEC: `engine/fadec.py`

**Cockpit / system state:**
- APU available + **APU BLEED** ON/OFF (bleed pressure availability)
- **ENG MODE** selector: `NORM` / `IGN_START` / `CRANK`
- **ENG MASTER 1 & 2**: ON/OFF
- start valve open/closed, **igniter A/B** energized

**FADEC state machine (detect-only — no auto-abort).** Sequence for **NORM**:
1. MASTER ON **and** bleed available → command **start valve open** (N2 rises).
2. At **N2 ≈ 16–20%** → command **fuel ON** + **igniters ON** → light-off.
3. At **N2 ≈ 50%** → **starter cutout**, start valve closes.
4. Spool to **idle (~60% N2 / ~19% N1)**, EGT settles → start complete; prompt
   MODE → NORM.

**CRANK** mode: command start valve only → **dry motoring** (no fuel, no
ignition). Used for ventilation / clearing after a failed start.

**Fault monitoring (flags + ECAM messages only; does NOT cut fuel):**
- **Hot start** — EGT > redline.
- **Hung start** — N2 stagnates sub-idle (dN2/dt ≈ 0 below idle for a window).
- **No light-off** — no EGT rise within a time window after fuel ON.
- **Wet start** — fuel commanded ON but no light-off (ignition failure).

The crew reacts (MASTER OFF / select CRANK to clear); the FADEC annunciates.

### Layer 3 — Driver: `simulate_start(...)`

Time loop: FADEC reads system + plant state → issues control commands → plant
integrates one `dt` → repeat until idle, fault-stable, or `t_max`.

Output — new dataclass `StartTransient` in `engine/results.py`:
- Time-series arrays: `t, N1, N2, EGT, FF, thrust`
- Per-frame system states: `start_valve, igniter_a, igniter_b, eng_mode, master`
- **Event / fault log**: ordered `(t, label)` entries —
  `STARTER ON, IGNITION ON, LIGHT-OFF, STARTER CUTOUT, IDLE` and fault labels
  `HUNG START, EGT EXCEEDANCE, NO LIGHT-OFF, WET START`.

## 4. Failure modes = injected root causes

Scenarios inject a **root cause** into plant/system params; gauges then show the
real symptom and the FADEC flags it. `StartScenario` enum:
`NORMAL, HUNG, HOT, NO_FUEL, NO_IGNITION`.

- **NO_FUEL** → fuel-valve fault: `fuel_cmd` honored but FF forced 0.
- **NO_IGNITION** → igniter fault: igniters never energize → `lit` stays False.
- **HUNG** → reduced bleed/starter torque (and/or raised drag) → equilibrium
  N2 < idle.
- **HOT** → restricted airflow / excess fuel-air ratio → EGT correlation exceeds
  redline.

## 5. App integration — cockpit + ECAM ENGINE page

New **"🔥 Engine Start"** mode in `app.py`:
- **Cockpit panel**: ENG MODE rotary (NORM / IGN-START / CRANK), ENG MASTER 1+2
  switches, APU BLEED toggle, and a **scenario injector** for the 4 faults.
- **ECAM ENGINE page**: dual-engine **N1 / N2 / EGT / FF** gauges plus
  **start-valve** and **igniter** indications — reuse/extend existing
  `ecam_html()`.
- **▶ Play**: time advances and gauges + system indications animate through the
  sequence; an event banner shows the current FADEC phase / fault.

Runs live (no pyCycle at runtime); idle anchor pulled from `lookup.pkl` for the
selected flight phase.

## 6. Testing (TDD)

**Plant**
- Normal start reaches idle N2 within a plausible time (~45–90 s).
- EGT peak below redline on a normal start.
- Time strictly increasing; no NaNs/Infs; torque balance sane.

**FADEC**
- Start valve opens only on MASTER ON + bleed available.
- Fuel commanded at the correct N2 threshold; starter cutout near 50%.
- CRANK yields no fuel and no ignition (dry motoring only).
- Each fault flag is raised at the correct condition.

**Failure scenarios** (the four confirmed signatures)
- HUNG: final N2 < idle and stable.
- HOT: EGT exceeds redline + exceedance event logged.
- NO_FUEL: EGT stays ambient, N2 plateaus at motoring speed, FF = 0.
- NO_IGNITION: FF > 0 but EGT ambient + wet-start flag.

## 7. Out of scope (YAGNI)

- Manual start mode (crew-timed fuel) — not included (Auto + CRANK only).
- FADEC automatic abort/recovery — detect-only by design.
- Two-engine *independent* simulation — both ECAM columns reflect the started
  engine; no per-engine divergence beyond display.
- Real engine-map sub-idle aerodynamics — approximated by the reduced-order ODE.
