# CFM56 Hajtőmű Termodinamikai Modell — Implementációs Terv

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A CFM56-5B kétáramú turbofan hajtőmű termodinamikai szimulációja Python/pyCycle alapon, design point és off-design analízissel, 2D/3D vizualizációval és Jupyter Notebookokkal.

**Architecture:** A NASA pyCycle könyvtár végzi a CEA-alapú termodinamikai számításokat OpenMDAO-n keresztül. Fölé egy `engine/` Python csomag kerül egyszerű wrapper függvényekkel (`run_design_point`, `run_off_design`), amelyek `EngineResults` objektumokat adnak vissza. A `visualization/` csomag Matplotlib és Plotly alapú diagramokat generál ebből.

**Tech Stack:** Python 3.10+, pyCycle (om-pycycle), OpenMDAO, NumPy, Matplotlib, Plotly, Jupyter, pandas

**Munkamappa:** `/Users/ziadmohamed/Documents/Uni/Szakdolgozat/Engine/Engine/`

---

## Fájlstruktúra

```
Engine/Engine/
├── engine/
│   ├── __init__.py               # Exportálja: run_design_point, run_off_design, EngineResults
│   ├── cfm56.py                  # CFM56-5B paraméterek + pyCycle modell builder
│   ├── simulation.py             # run_design_point(), run_off_design()
│   └── results.py                # EngineResults, StationData dataclass-ok
├── visualization/
│   ├── __init__.py               # Exportálja a plot függvényeket
│   ├── station_diagram.py        # plot_station_diagram(results) → matplotlib Figure
│   ├── ts_diagram.py             # plot_ts_diagram(results_list) → matplotlib Figure
│   └── model_3d.py               # plot_3d_model(results) → plotly Figure
├── notebooks/
│   ├── 01_design_point.ipynb
│   ├── 02_off_design.ipynb
│   └── 03_visualization.ipynb
├── scripts/
│   ├── run_design.py
│   └── run_off_design.py
├── tests/
│   ├── test_results.py
│   ├── test_cfm56.py
│   ├── test_simulation.py
│   └── test_visualization.py
├── requirements.txt
└── README.md
```

---

## Task 1: Projekt telepítés és requirements

**Files:**
- Create: `requirements.txt`
- Create: `README.md`

- [ ] **Step 1: Virtuális környezet létrehozása**

```bash
cd /Users/ziadmohamed/Documents/Uni/Szakdolgozat/Engine/Engine
python3 -m venv venv
source venv/bin/activate
```

- [ ] **Step 2: requirements.txt létrehozása**

```
om-pycycle
openmdao
numpy
matplotlib
plotly
jupyter
pandas
pytest
```

- [ ] **Step 3: Függőségek telepítése**

```bash
pip install -r requirements.txt
```

Elvárt kimenet: `Successfully installed om-pycycle-...`

- [ ] **Step 4: Telepítés ellenőrzése**

```bash
python -c "import pycycle; import openmdao; import matplotlib; import plotly; print('OK')"
```

Elvárt kimenet: `OK`

- [ ] **Step 5: README.md létrehozása**

```markdown
# CFM56-5B Termodinamikai Szimuláció

BSc szakdolgozat — Nyíregyházi Egyetem

## Telepítés
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Futtatás
```bash
python scripts/run_design.py
python scripts/run_off_design.py
jupyter notebook notebooks/
```

## Struktúra
- `engine/` — pyCycle wrapper, CFM56 modell
- `visualization/` — 2D/3D diagramok
- `notebooks/` — Jupyter analízis
- `scripts/` — parancssoros futtatás
```

- [ ] **Step 6: Könyvtárstruktúra létrehozása**

```bash
mkdir -p engine visualization notebooks scripts tests
touch engine/__init__.py visualization/__init__.py
touch tests/__init__.py
```

- [ ] **Step 7: Commit**

```bash
git init
git add requirements.txt README.md engine/__init__.py visualization/__init__.py tests/__init__.py
git commit -m "feat: project structure and dependencies"
```

---

## Task 2: EngineResults adatosztályok (TDD)

**Files:**
- Create: `engine/results.py`
- Create: `tests/test_results.py`

- [ ] **Step 1: Teszt fájl írása**

```python
# tests/test_results.py
import pytest
from engine.results import StationData, EngineResults

def test_station_data_stores_values():
    s = StationData(station='fan_inlet', T=288.15, P=101.325, h=0.0)
    assert s.station == 'fan_inlet'
    assert s.T == pytest.approx(288.15)
    assert s.P == pytest.approx(101.325)

def test_engine_results_default_empty_stations():
    r = EngineResults(flight_phase='takeoff', altitude_ft=0, mach=0.25)
    assert r.stations == {}
    assert r.thrust_kN == 0.0

def test_engine_results_to_dataframe():
    r = EngineResults(flight_phase='takeoff', altitude_ft=0, mach=0.25)
    r.stations['inlet'] = StationData(station='inlet', T=288.15, P=101.325, h=0.0)
    r.stations['fan_exit'] = StationData(station='fan_exit', T=330.0, P=170.7, h=41.9)
    df = r.to_dataframe()
    assert len(df) == 2
    assert list(df.columns) == ['station', 'T_K', 'P_kPa', 'h_kJkg']

def test_engine_results_summary_runs(capsys):
    r = EngineResults(flight_phase='takeoff', altitude_ft=0, mach=0.25,
                      thrust_kN=133.4, sfc=0.01098, opr=27.0)
    r.summary()
    out = capsys.readouterr().out
    assert 'takeoff' in out
    assert '133.4' in out
```

- [ ] **Step 2: Teszt futtatása — elvárt FAIL**

```bash
cd /Users/ziadmohamed/Documents/Uni/Szakdolgozat/Engine/Engine
source venv/bin/activate
pytest tests/test_results.py -v
```

Elvárt: `ModuleNotFoundError: No module named 'engine.results'`

- [ ] **Step 3: engine/results.py implementálása**

```python
# engine/results.py
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class StationData:
    station: str
    T: float      # K
    P: float      # kPa
    h: float      # kJ/kg


@dataclass
class EngineResults:
    flight_phase: str
    altitude_ft: float
    mach: float
    stations: Dict[str, StationData] = field(default_factory=dict)
    thrust_kN: float = 0.0
    sfc: float = 0.0        # kg/(kN·s)
    fan_eff: float = 0.0
    lpc_eff: float = 0.0
    hpc_eff: float = 0.0
    hpt_eff: float = 0.0
    lpt_eff: float = 0.0
    opr: float = 0.0
    bpr: float = 0.0
    fuel_flow: float = 0.0  # kg/s

    def to_dataframe(self):
        import pandas as pd
        rows = [
            {'station': name, 'T_K': s.T, 'P_kPa': s.P, 'h_kJkg': s.h}
            for name, s in self.stations.items()
        ]
        return pd.DataFrame(rows)

    def summary(self):
        print(f"=== {self.flight_phase} | Alt: {self.altitude_ft} ft | Mach: {self.mach} ===")
        print(f"  Tolóerő  : {self.thrust_kN:.1f} kN")
        print(f"  SFC      : {self.sfc:.5f} kg/(kN·s)")
        print(f"  OPR      : {self.opr:.2f}")
        print(f"  BPR      : {self.bpr:.2f}")
        print(f"  Tüzelőanyag: {self.fuel_flow:.2f} kg/s")
        print(f"  Állomások: {len(self.stations)}")
```

- [ ] **Step 4: Tesztek futtatása — elvárt PASS**

```bash
pytest tests/test_results.py -v
```

Elvárt: `4 passed`

- [ ] **Step 5: Commit**

```bash
git add engine/results.py tests/test_results.py
git commit -m "feat: add EngineResults and StationData dataclasses"
```

---

## Task 3: CFM56-5B paraméterek és pyCycle modell (TDD)

**Files:**
- Create: `engine/cfm56.py`
- Create: `tests/test_cfm56.py`

- [ ] **Step 1: Teszt fájl írása**

```python
# tests/test_cfm56.py
import pytest
from engine.cfm56 import CFM56_PARAMS, build_design_model, build_offdesign_model


def test_cfm56_params_physical_bounds():
    p = CFM56_PARAMS
    assert 5.0 < p['bpr'] < 7.0
    assert 20.0 < p['opr'] < 35.0
    assert 1500.0 < p['T4_design'] < 2000.0
    assert 100.0 < p['max_thrust_kN'] < 200.0

def test_cfm56_opr_matches_stage_prs():
    p = CFM56_PARAMS
    computed_opr = p['fan_PR'] * p['lpc_PR'] * p['hpc_PR']
    assert computed_opr == pytest.approx(p['opr'], rel=0.05)

def test_build_design_model_returns_problem():
    import openmdao.api as om
    prob = build_design_model()
    assert isinstance(prob, om.Problem)

def test_build_offdesign_model_returns_problem():
    import openmdao.api as om
    prob = build_offdesign_model()
    assert isinstance(prob, om.Problem)
```

- [ ] **Step 2: Teszt futtatása — elvárt FAIL**

```bash
pytest tests/test_cfm56.py -v
```

Elvárt: `ModuleNotFoundError: No module named 'engine.cfm56'`

- [ ] **Step 3: engine/cfm56.py implementálása**

```python
# engine/cfm56.py
import openmdao.api as om
import pycycle.api as pyc

CFM56_PARAMS = {
    'bpr': 5.5,
    'opr': 27.0,
    'T4_design': 1700.0,      # K — égőtér kilépő hőmérséklet
    'max_thrust_kN': 133.4,   # kN
    'mass_flow': 370.0,        # kg/s (felszállás)
    'fan_PR': 1.685,           # Fan nyomásarány
    'lpc_PR': 2.0,             # LPC nyomásarány
    'hpc_PR': 8.0,             # HPC nyomásarány (fan*lpc*hpc ≈ 27)
    'fan_eff': 0.89,
    'lpc_eff': 0.89,
    'hpc_eff': 0.87,
    'hpt_eff': 0.89,
    'lpt_eff': 0.90,
    'inlet_MN': 0.60,
    'fan_MN': 0.45,
    'hpc_MN': 0.20,
    'burner_dPqP': 0.03,       # Égőtér nyomásveszteség
    'core_nozz_Cv': 0.9999,
    'byp_nozz_Cv': 0.9975,
}


def build_design_model() -> om.Problem:
    """Összeépíti a CFM56-5B pyCycle design point modelljét."""
    p = CFM56_PARAMS
    prob = om.Problem()

    cycle = prob.model = pyc.Cycle()
    cycle.options['thermo_method'] = 'CEA'
    cycle.options['thermo_data'] = pyc.species_data.janaf
    cycle.options['design'] = True

    cycle.add_subsystem('fc',       pyc.FlightConditions())
    cycle.add_subsystem('inlet',    pyc.Inlet())
    cycle.add_subsystem('fan',      pyc.Compressor(map_data=pyc.AXI5,
                                                    design_params=['PR', 'eff']))
    cycle.add_subsystem('splitter', pyc.Splitter())
    cycle.add_subsystem('duct4',    pyc.Duct())
    cycle.add_subsystem('lpc',      pyc.Compressor(map_data=pyc.LPCMap,
                                                    design_params=['PR', 'eff']))
    cycle.add_subsystem('duct6',    pyc.Duct())
    cycle.add_subsystem('hpc',      pyc.Compressor(map_data=pyc.HPCMap,
                                                    design_params=['PR', 'eff']))
    cycle.add_subsystem('burner',   pyc.Combustor(fuel_type='Jet-A'))
    cycle.add_subsystem('hpt',      pyc.Turbine(map_data=pyc.HPTMap,
                                                 design_params=['eff']))
    cycle.add_subsystem('duct11',   pyc.Duct())
    cycle.add_subsystem('lpt',      pyc.Turbine(map_data=pyc.LPTMap,
                                                 design_params=['eff']))
    cycle.add_subsystem('duct13',   pyc.Duct())
    cycle.add_subsystem('core_nozz', pyc.Nozzle(nozzType='CV', lossCoef='Cv'))
    cycle.add_subsystem('byp_nozz', pyc.Nozzle(nozzType='CV', lossCoef='Cv'))
    cycle.add_subsystem('perf',     pyc.Performance(num_nozzles=2, num_burners=1))

    # Áramlási útvonalak összekötése
    cycle.pyc_connect_flow('fc.Fl_O',        'inlet.Fl_I')
    cycle.pyc_connect_flow('inlet.Fl_O',     'fan.Fl_I')
    cycle.pyc_connect_flow('fan.Fl_O',       'splitter.Fl_I')
    cycle.pyc_connect_flow('splitter.Fl_O1', 'duct4.Fl_I')
    cycle.pyc_connect_flow('duct4.Fl_O',     'lpc.Fl_I')
    cycle.pyc_connect_flow('lpc.Fl_O',       'duct6.Fl_I')
    cycle.pyc_connect_flow('duct6.Fl_O',     'hpc.Fl_I')
    cycle.pyc_connect_flow('hpc.Fl_O',       'burner.Fl_I')
    cycle.pyc_connect_flow('burner.Fl_O',    'hpt.Fl_I')
    cycle.pyc_connect_flow('hpt.Fl_O',       'duct11.Fl_I')
    cycle.pyc_connect_flow('duct11.Fl_O',    'lpt.Fl_I')
    cycle.pyc_connect_flow('lpt.Fl_O',       'duct13.Fl_I')
    cycle.pyc_connect_flow('duct13.Fl_O',    'core_nozz.Fl_I')
    cycle.pyc_connect_flow('splitter.Fl_O2', 'byp_nozz.Fl_I')

    # Teljesítmény összekötések
    prob.model.connect('core_nozz.Fg', 'perf.Fg_0')
    prob.model.connect('byp_nozz.Fg',  'perf.Fg_1')
    prob.model.connect('inlet.F_ram',  'perf.ram_drag')
    prob.model.connect('burner.Wfuel', 'perf.Wfuel_0')

    # HP tengely
    prob.model.connect('fan.trq',  'lpt.pwr_in', src_indices=[0])
    prob.model.connect('hpc.trq',  'hpt.pwr_in')

    prob.setup(check=False, force_alloc_complex=True)
    return prob


def build_offdesign_model() -> om.Problem:
    """Összeépíti a CFM56-5B pyCycle off-design modelljét."""
    prob = om.Problem()

    cycle = prob.model = pyc.Cycle()
    cycle.options['thermo_method'] = 'CEA'
    cycle.options['thermo_data'] = pyc.species_data.janaf
    cycle.options['design'] = False

    # Ugyanazok a komponensek, de design=False
    cycle.add_subsystem('fc',       pyc.FlightConditions())
    cycle.add_subsystem('inlet',    pyc.Inlet())
    cycle.add_subsystem('fan',      pyc.Compressor(map_data=pyc.AXI5))
    cycle.add_subsystem('splitter', pyc.Splitter())
    cycle.add_subsystem('duct4',    pyc.Duct())
    cycle.add_subsystem('lpc',      pyc.Compressor(map_data=pyc.LPCMap))
    cycle.add_subsystem('duct6',    pyc.Duct())
    cycle.add_subsystem('hpc',      pyc.Compressor(map_data=pyc.HPCMap))
    cycle.add_subsystem('burner',   pyc.Combustor(fuel_type='Jet-A'))
    cycle.add_subsystem('hpt',      pyc.Turbine(map_data=pyc.HPTMap))
    cycle.add_subsystem('duct11',   pyc.Duct())
    cycle.add_subsystem('lpt',      pyc.Turbine(map_data=pyc.LPTMap))
    cycle.add_subsystem('duct13',   pyc.Duct())
    cycle.add_subsystem('core_nozz', pyc.Nozzle(nozzType='CV', lossCoef='Cv'))
    cycle.add_subsystem('byp_nozz', pyc.Nozzle(nozzType='CV', lossCoef='Cv'))
    cycle.add_subsystem('perf',     pyc.Performance(num_nozzles=2, num_burners=1))

    cycle.pyc_connect_flow('fc.Fl_O',        'inlet.Fl_I')
    cycle.pyc_connect_flow('inlet.Fl_O',     'fan.Fl_I')
    cycle.pyc_connect_flow('fan.Fl_O',       'splitter.Fl_I')
    cycle.pyc_connect_flow('splitter.Fl_O1', 'duct4.Fl_I')
    cycle.pyc_connect_flow('duct4.Fl_O',     'lpc.Fl_I')
    cycle.pyc_connect_flow('lpc.Fl_O',       'duct6.Fl_I')
    cycle.pyc_connect_flow('duct6.Fl_O',     'hpc.Fl_I')
    cycle.pyc_connect_flow('hpc.Fl_O',       'burner.Fl_I')
    cycle.pyc_connect_flow('burner.Fl_O',    'hpt.Fl_I')
    cycle.pyc_connect_flow('hpt.Fl_O',       'duct11.Fl_I')
    cycle.pyc_connect_flow('duct11.Fl_O',    'lpt.Fl_I')
    cycle.pyc_connect_flow('lpt.Fl_O',       'duct13.Fl_I')
    cycle.pyc_connect_flow('duct13.Fl_O',    'core_nozz.Fl_I')
    cycle.pyc_connect_flow('splitter.Fl_O2', 'byp_nozz.Fl_I')

    prob.model.connect('core_nozz.Fg', 'perf.Fg_0')
    prob.model.connect('byp_nozz.Fg',  'perf.Fg_1')
    prob.model.connect('inlet.F_ram',  'perf.ram_drag')
    prob.model.connect('burner.Wfuel', 'perf.Wfuel_0')
    prob.model.connect('fan.trq',  'lpt.pwr_in', src_indices=[0])
    prob.model.connect('hpc.trq',  'hpt.pwr_in')

    prob.setup(check=False, force_alloc_complex=True)
    return prob
```

- [ ] **Step 4: Tesztek futtatása — elvárt PASS**

```bash
pytest tests/test_cfm56.py -v
```

Elvárt: `4 passed`

- [ ] **Step 5: Commit**

```bash
git add engine/cfm56.py tests/test_cfm56.py
git commit -m "feat: add CFM56-5B parameters and pyCycle model builders"
```

---

## Task 4: Szimuláció wrapper (TDD)

**Files:**
- Create: `engine/simulation.py`
- Modify: `engine/__init__.py`
- Create: `tests/test_simulation.py`

- [ ] **Step 1: Teszt fájl írása**

```python
# tests/test_simulation.py
import pytest
from engine.simulation import run_design_point, run_off_design
from engine.results import EngineResults

TAKEOFF = {'flight_phase': 'takeoff', 'altitude_ft': 0, 'mach': 0.25}


def test_run_design_point_returns_engine_results():
    result = run_design_point(**TAKEOFF)
    assert isinstance(result, EngineResults)


def test_run_design_point_thrust_physical_range():
    result = run_design_point(**TAKEOFF)
    assert 80.0 < result.thrust_kN < 160.0


def test_run_design_point_opr_physical_range():
    result = run_design_point(**TAKEOFF)
    assert 20.0 < result.opr < 35.0


def test_run_design_point_stations_populated():
    result = run_design_point(**TAKEOFF)
    assert len(result.stations) >= 6


def test_run_off_design_returns_list():
    phases = [
        {'flight_phase': 'takeoff',  'altitude_ft': 0,      'mach': 0.25},
        {'flight_phase': 'cruise',   'altitude_ft': 35000,  'mach': 0.82},
    ]
    results = run_off_design(phases)
    assert len(results) == 2
    assert all(isinstance(r, EngineResults) for r in results)


def test_cruise_thrust_less_than_takeoff():
    takeoff = run_design_point(flight_phase='takeoff', altitude_ft=0,     mach=0.25)
    cruise  = run_design_point(flight_phase='cruise',  altitude_ft=35000, mach=0.82)
    assert cruise.thrust_kN < takeoff.thrust_kN
```

- [ ] **Step 2: Teszt futtatása — elvárt FAIL**

```bash
pytest tests/test_simulation.py -v
```

Elvárt: `ModuleNotFoundError: No module named 'engine.simulation'`

- [ ] **Step 3: engine/simulation.py implementálása**

```python
# engine/simulation.py
from typing import List
import numpy as np
from engine.cfm56 import build_design_model, CFM56_PARAMS
from engine.results import EngineResults, StationData

# Állomásnevek és pyCycle path-ok
_STATION_PATHS = {
    'inlet_in':    'inlet.Fl_I',
    'fan_exit':    'fan.Fl_O',
    'lpc_exit':    'lpc.Fl_O',
    'hpc_exit':    'hpc.Fl_O',
    'burner_exit': 'burner.Fl_O',
    'hpt_exit':    'hpt.Fl_O',
    'lpt_exit':    'lpt.Fl_O',
    'core_nozz':   'core_nozz.Fl_O',
    'byp_nozz':    'byp_nozz.Fl_O',
}

# ISA légkör: hőmérséklet és nyomás magasság szerint
def _isa(altitude_ft: float):
    """Visszaadja (T_K, P_kPa) értékeket adott magasságon (ISA modell)."""
    h_m = altitude_ft * 0.3048
    if h_m <= 11000:
        T = 288.15 - 0.0065 * h_m
        P = 101.325 * (T / 288.15) ** 5.2561
    else:
        T = 216.65
        P = 22.632 * np.exp(-0.0001577 * (h_m - 11000))
    return T, P


def _extract_results(prob, flight_phase: str, altitude_ft: float, mach: float) -> EngineResults:
    """Kinyeri az OpenMDAO Problem-ból az EngineResults objektumot."""
    result = EngineResults(
        flight_phase=flight_phase,
        altitude_ft=altitude_ft,
        mach=mach,
        thrust_kN=float(prob.get_val('perf.Fn', units='kN')[0]),
        sfc=float(prob.get_val('perf.TSFC', units='kg/(kN*s)')[0]),
        opr=float(prob.get_val('perf.OPR')[0]) if 'perf.OPR' in prob.model._var_allprocs_abs2meta else
            float(prob.get_val('hpc.Fl_O:tot:P')[0] / prob.get_val('inlet.Fl_I:tot:P')[0]),
        bpr=float(prob.get_val('splitter.BPR')[0]),
        fuel_flow=float(prob.get_val('burner.Wfuel', units='kg/s')[0]),
        fan_eff=float(prob.get_val('fan.eff')[0]),
        lpc_eff=float(prob.get_val('lpc.eff')[0]),
        hpc_eff=float(prob.get_val('hpc.eff')[0]),
        hpt_eff=float(prob.get_val('hpt.eff')[0]),
        lpt_eff=float(prob.get_val('lpt.eff')[0]),
    )

    for name, path in _STATION_PATHS.items():
        try:
            T = float(prob.get_val(f'{path}:tot:T', units='K')[0])
            P = float(prob.get_val(f'{path}:tot:P', units='kPa')[0])
            h = float(prob.get_val(f'{path}:tot:h', units='kJ/kg')[0])
            result.stations[name] = StationData(station=name, T=T, P=P, h=h)
        except KeyError:
            pass

    return result


def run_design_point(flight_phase: str, altitude_ft: float, mach: float) -> EngineResults:
    """CFM56-5B design point szimulációja adott repülési állapotra."""
    p = CFM56_PARAMS
    T_amb, P_amb = _isa(altitude_ft)

    prob = build_design_model()

    # Repülési feltételek
    prob.set_val('fc.alt',   altitude_ft, units='ft')
    prob.set_val('fc.MN',    mach)
    prob.set_val('fc.dTs',   0.0)

    # Design paraméterek
    prob.set_val('fan.PR',   p['fan_PR'])
    prob.set_val('fan.eff',  p['fan_eff'])
    prob.set_val('lpc.PR',   p['lpc_PR'])
    prob.set_val('lpc.eff',  p['lpc_eff'])
    prob.set_val('hpc.PR',   p['hpc_PR'])
    prob.set_val('hpc.eff',  p['hpc_eff'])
    prob.set_val('burner.TtOut', p['T4_design'], units='K')
    prob.set_val('hpt.eff',  p['hpt_eff'])
    prob.set_val('lpt.eff',  p['lpt_eff'])
    prob.set_val('inlet.MN', p['inlet_MN'])
    prob.set_val('fan.MN',   p['fan_MN'])
    prob.set_val('hpc.MN',   p['hpc_MN'])
    prob.set_val('burner.dPqP', p['burner_dPqP'])
    prob.set_val('core_nozz.Cv', p['core_nozz_Cv'])
    prob.set_val('byp_nozz.Cv',  p['byp_nozz_Cv'])
    prob.set_val('inlet.Fl_I:stat:W', p['mass_flow'] / (1 + p['bpr']), units='kg/s')

    prob.run_model()
    return _extract_results(prob, flight_phase, altitude_ft, mach)


def run_off_design(flight_phases: List[dict]) -> List[EngineResults]:
    """Off-design analízis több repülési fázisra."""
    return [run_design_point(**phase) for phase in flight_phases]
```

- [ ] **Step 4: engine/__init__.py frissítése**

```python
# engine/__init__.py
from engine.results import EngineResults, StationData
from engine.simulation import run_design_point, run_off_design
```

- [ ] **Step 5: Tesztek futtatása — elvárt PASS**

```bash
pytest tests/test_simulation.py -v
```

Elvárt: `6 passed`  
*(A szimuláció futhat 1-2 percig — ez normális)*

- [ ] **Step 6: Commit**

```bash
git add engine/simulation.py engine/__init__.py tests/test_simulation.py
git commit -m "feat: add simulation wrapper with run_design_point and run_off_design"
```

---

## Task 5: 2D Állomás-diagram (TDD)

**Files:**
- Create: `visualization/station_diagram.py`
- Modify: `visualization/__init__.py`
- Create: `tests/test_visualization.py`

- [ ] **Step 1: Teszt fájl írása**

```python
# tests/test_visualization.py
import pytest
import matplotlib
matplotlib.use('Agg')  # headless
import matplotlib.figure
import plotly.graph_objects as go

from engine.results import EngineResults, StationData
from visualization.station_diagram import plot_station_diagram
from visualization.ts_diagram import plot_ts_diagram
from visualization.model_3d import plot_3d_model


def _make_result(phase='takeoff'):
    r = EngineResults(flight_phase=phase, altitude_ft=0, mach=0.25,
                      thrust_kN=133.4, sfc=0.01098, opr=27.0, bpr=5.5)
    stations = [
        ('inlet_in',    288.15,  101.3,    0.0),
        ('fan_exit',    330.0,   170.7,   41.9),
        ('lpc_exit',    390.0,   341.4,  102.2),
        ('hpc_exit',    710.0,  2736.0,  430.0),
        ('burner_exit', 1700.0, 2654.0, 1600.0),
        ('hpt_exit',    1150.0,  680.0, 1050.0),
        ('lpt_exit',    820.0,   130.0,  540.0),
        ('core_nozz',   780.0,   101.3,  500.0),
    ]
    for name, T, P, h in stations:
        r.stations[name] = StationData(station=name, T=T, P=P, h=h)
    return r


def test_station_diagram_returns_figure():
    fig = plot_station_diagram(_make_result())
    assert isinstance(fig, matplotlib.figure.Figure)


def test_ts_diagram_returns_figure():
    results = [_make_result('takeoff'), _make_result('cruise')]
    fig = plot_ts_diagram(results)
    assert isinstance(fig, matplotlib.figure.Figure)


def test_3d_model_returns_plotly_figure():
    fig = plot_3d_model(_make_result())
    assert isinstance(fig, go.Figure)
```

- [ ] **Step 2: Teszt futtatása — elvárt FAIL**

```bash
pytest tests/test_visualization.py -v
```

Elvárt: `ModuleNotFoundError: No module named 'visualization.station_diagram'`

- [ ] **Step 3: visualization/station_diagram.py implementálása**

```python
# visualization/station_diagram.py
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from engine.results import EngineResults

_STATION_ORDER = [
    'inlet_in', 'fan_exit', 'lpc_exit', 'hpc_exit',
    'burner_exit', 'hpt_exit', 'lpt_exit', 'core_nozz',
]
_STATION_LABELS = {
    'inlet_in':    'Inlet\n(St. 2)',
    'fan_exit':    'Fan\nkimenet',
    'lpc_exit':    'LPC\nkimenet',
    'hpc_exit':    'HPC\nkimenet',
    'burner_exit': 'Égőtér\nkimenet',
    'hpt_exit':    'HPT\nkimenet',
    'lpt_exit':    'LPT\nkimenet',
    'core_nozz':   'Core\nfúvócső',
}


def plot_station_diagram(results: EngineResults) -> plt.Figure:
    """2D állomás-diagram T és P értékekkel minden állomáson."""
    stations = [s for s in _STATION_ORDER if s in results.stations]
    T_vals = [results.stations[s].T for s in stations]
    P_vals = [results.stations[s].P for s in stations]
    labels = [_STATION_LABELS.get(s, s) for s in stations]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8))
    fig.suptitle(
        f'CFM56-5B Állomás-diagram — {results.flight_phase.upper()}\n'
        f'Alt: {results.altitude_ft} ft | Mach: {results.mach} | '
        f'Tolóerő: {results.thrust_kN:.1f} kN | OPR: {results.opr:.1f}',
        fontsize=13, fontweight='bold'
    )

    cmap = plt.cm.RdYlBu_r
    norm = plt.Normalize(min(T_vals), max(T_vals))
    colors = [cmap(norm(T)) for T in T_vals]
    x = np.arange(len(stations))

    # Hőmérséklet
    bars1 = ax1.bar(x, T_vals, color=colors, edgecolor='black', linewidth=0.8)
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=9)
    ax1.set_ylabel('Hőmérséklet [K]', fontsize=11)
    ax1.set_title('Teljes hőmérséklet (Tt) az állomások mentén', fontsize=11)
    ax1.grid(axis='y', alpha=0.4)
    for bar, T in zip(bars1, T_vals):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 10,
                 f'{T:.0f} K', ha='center', va='bottom', fontsize=8)

    # Nyomás
    bars2 = ax2.bar(x, P_vals, color='steelblue', edgecolor='black', linewidth=0.8)
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=9)
    ax2.set_ylabel('Nyomás [kPa]', fontsize=11)
    ax2.set_title('Teljes nyomás (Pt) az állomások mentén', fontsize=11)
    ax2.grid(axis='y', alpha=0.4)
    for bar, P in zip(bars2, P_vals):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 10,
                 f'{P:.0f} kPa', ha='center', va='bottom', fontsize=8)

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    fig.colorbar(sm, ax=ax1, label='Hőmérséklet [K]', shrink=0.8)
    plt.tight_layout()
    return fig
```

- [ ] **Step 4: visualization/ts_diagram.py implementálása**

```python
# visualization/ts_diagram.py
import matplotlib.pyplot as plt
import numpy as np
from typing import List
from engine.results import EngineResults

_STATION_ORDER = [
    'inlet_in', 'fan_exit', 'lpc_exit', 'hpc_exit',
    'burner_exit', 'hpt_exit', 'lpt_exit', 'core_nozz',
]
_COLORS = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3']


def _entropy_approx(stations_data, cp=1.005):
    """Közelítő entrópianövekedés kJ/(kg·K) — csak vizualizációhoz."""
    T_vals = [s.T for s in stations_data]
    P_vals = [s.P for s in stations_data]
    s_vals = [0.0]
    R = 0.287
    for i in range(1, len(T_vals)):
        ds = cp * np.log(T_vals[i] / T_vals[i - 1]) - R * np.log(P_vals[i] / P_vals[i - 1])
        s_vals.append(s_vals[-1] + ds)
    return s_vals


def plot_ts_diagram(results_list: List[EngineResults]) -> plt.Figure:
    """T-s diagram több repülési fázisra."""
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_xlabel('Specifikus entrópia [kJ/(kg·K)]', fontsize=12)
    ax.set_ylabel('Hőmérséklet [K]', fontsize=12)
    ax.set_title('CFM56-5B T-s diagram (Brayton-ciklus)', fontsize=13, fontweight='bold')
    ax.grid(alpha=0.3)

    for idx, result in enumerate(results_list):
        stations = [result.stations[s] for s in _STATION_ORDER if s in result.stations]
        if len(stations) < 3:
            continue
        T_vals = [s.T for s in stations]
        s_vals = _entropy_approx(stations)
        color = _COLORS[idx % len(_COLORS)]
        ax.plot(s_vals, T_vals, '-o', color=color, linewidth=2, markersize=5,
                label=f'{result.flight_phase} | Mach {result.mach} | {result.altitude_ft} ft')
        for i, (sv, tv, station) in enumerate(zip(s_vals, T_vals, stations)):
            if i in (0, 3, 4, 7):
                ax.annotate(station.station.replace('_', '\n'),
                            xy=(sv, tv), xytext=(sv + 0.01, tv + 20),
                            fontsize=7, color=color)

    ax.legend(loc='upper left', fontsize=9)
    plt.tight_layout()
    return fig
```

- [ ] **Step 5: visualization/model_3d.py implementálása**

```python
# visualization/model_3d.py
import numpy as np
import plotly.graph_objects as go
from engine.results import EngineResults

# CFM56 keresztmetszeti profil (x=tengelyirány m, r=sugár m) — közelítő geometria
_PROFILE = np.array([
    # x,    r_core, r_bypass
    [0.00,  0.25,   0.55],   # fan belépő
    [0.30,  0.25,   0.55],   # fan kilépő
    [0.30,  0.25,   0.55],   # splitter
    [0.60,  0.22,   0.52],   # LPC
    [0.90,  0.18,   0.48],   # HPC belépő
    [1.20,  0.14,   0.44],   # HPC kilépő
    [1.40,  0.14,   0.38],   # égőtér
    [1.70,  0.16,   0.30],   # HPT
    [2.00,  0.19,   0.22],   # LPT
    [2.40,  0.22,   0.22],   # fúvócső belépő
    [2.60,  0.18,   0.18],   # fúvócső kilépő
])


def _revolution_surface(x_arr, r_arr, n_theta=60):
    """Forgástestet generál egy 2D profilból."""
    theta = np.linspace(0, 2 * np.pi, n_theta)
    X = np.outer(x_arr, np.ones(n_theta))
    Y = np.outer(r_arr, np.cos(theta))
    Z = np.outer(r_arr, np.sin(theta))
    return X, Y, Z


def plot_3d_model(results: EngineResults) -> go.Figure:
    """3D forgástest modell a CFM56 közelítő geometriájával, hőmérséklet-színskálával."""
    x = _PROFILE[:, 0]
    r_core = _PROFILE[:, 1]
    r_byp = _PROFILE[:, 2]

    station_order = [
        'inlet_in', 'fan_exit', 'fan_exit', 'lpc_exit',
        'lpc_exit', 'hpc_exit', 'hpc_exit', 'burner_exit',
        'hpt_exit', 'lpt_exit', 'core_nozz',
    ]
    T_stations = []
    for s in station_order:
        if s in results.stations:
            T_stations.append(results.stations[s].T)
        else:
            T_stations.append(500.0)
    T_arr = np.array(T_stations)

    n_theta = 60
    theta = np.linspace(0, 2 * np.pi, n_theta)
    T_surface = np.outer(T_arr, np.ones(n_theta))

    X_core, Y_core, Z_core = _revolution_surface(x, r_core, n_theta)
    X_byp,  Y_byp,  Z_byp  = _revolution_surface(x, r_byp,  n_theta)

    fig = go.Figure()
    fig.add_trace(go.Surface(
        x=X_core, y=Y_core, z=Z_core,
        surfacecolor=T_surface,
        colorscale='RdYlBu_r',
        cmin=280, cmax=1800,
        colorbar=dict(title='Hőmérséklet [K]', x=1.02),
        name='Core',
        opacity=0.95,
    ))
    fig.add_trace(go.Surface(
        x=X_byp, y=Y_byp, z=Z_byp,
        surfacecolor=np.full_like(T_surface, 320.0),
        colorscale='Blues',
        cmin=280, cmax=400,
        showscale=False,
        name='Bypass',
        opacity=0.35,
    ))

    fig.update_layout(
        title=dict(
            text=f'CFM56-5B 3D Modell — {results.flight_phase.upper()}<br>'
                 f'Tolóerő: {results.thrust_kN:.1f} kN | OPR: {results.opr:.1f} | '
                 f'Mach: {results.mach}',
            x=0.5
        ),
        scene=dict(
            xaxis_title='Tengelyirány [m]',
            yaxis_title='Y [m]',
            zaxis_title='Z [m]',
            aspectmode='data',
            camera=dict(eye=dict(x=1.5, y=1.5, z=0.8)),
        ),
        width=900, height=600,
    )
    return fig
```

- [ ] **Step 6: visualization/__init__.py frissítése**

```python
# visualization/__init__.py
from visualization.station_diagram import plot_station_diagram
from visualization.ts_diagram import plot_ts_diagram
from visualization.model_3d import plot_3d_model
```

- [ ] **Step 7: Tesztek futtatása — elvárt PASS**

```bash
pytest tests/test_visualization.py -v
```

Elvárt: `3 passed`

- [ ] **Step 8: Commit**

```bash
git add visualization/ tests/test_visualization.py
git commit -m "feat: add 2D station diagram, T-s diagram, and 3D engine model"
```

---

## Task 6: Jupyter Notebookok

**Files:**
- Create: `notebooks/01_design_point.ipynb`
- Create: `notebooks/02_off_design.ipynb`
- Create: `notebooks/03_visualization.ipynb`

- [ ] **Step 1: 01_design_point.ipynb létrehozása**

Jupyter-ben hozd létre, majd add hozzá ezeket a cellákat:

**Cella 1 (Markdown):**
```markdown
# CFM56-5B — Design Point Analízis
**Repülési állapot:** Felszállás | Alt: 0 ft | Mach: 0.25
```

**Cella 2 (Code):**
```python
import sys
sys.path.insert(0, '..')
from engine import run_design_point

result = run_design_point(flight_phase='takeoff', altitude_ft=0, mach=0.25)
result.summary()
```

**Cella 3 (Code):**
```python
result.to_dataframe()
```

**Cella 4 (Code):**
```python
import matplotlib
matplotlib.use('inline')
from visualization import plot_station_diagram

fig = plot_station_diagram(result)
fig.savefig('design_point_stations.png', dpi=150, bbox_inches='tight')
fig
```

- [ ] **Step 2: 02_off_design.ipynb létrehozása**

**Cella 1 (Markdown):**
```markdown
# CFM56-5B — Off-Design Analízis
Három repülési fázis összehasonlítása: Felszállás · Emelkedés · Cruise
```

**Cella 2 (Code):**
```python
import sys
sys.path.insert(0, '..')
from engine import run_off_design
import pandas as pd

phases = [
    {'flight_phase': 'takeoff', 'altitude_ft': 0,      'mach': 0.25},
    {'flight_phase': 'climb',   'altitude_ft': 10000,  'mach': 0.50},
    {'flight_phase': 'cruise',  'altitude_ft': 35000,  'mach': 0.82},
]
results = run_off_design(phases)
for r in results:
    r.summary()
    print()
```

**Cella 3 (Code):**
```python
summary = pd.DataFrame([{
    'Fázis':       r.flight_phase,
    'Magasság ft': r.altitude_ft,
    'Mach':        r.mach,
    'Tolóerő kN':  round(r.thrust_kN, 1),
    'SFC':         round(r.sfc, 5),
    'OPR':         round(r.opr, 2),
    'BPR':         round(r.bpr, 2),
} for r in results])
summary
```

**Cella 4 (Code):**
```python
from visualization import plot_ts_diagram
fig = plot_ts_diagram(results)
fig.savefig('off_design_ts.png', dpi=150, bbox_inches='tight')
fig
```

- [ ] **Step 3: 03_visualization.ipynb létrehozása**

**Cella 1 (Markdown):**
```markdown
# CFM56-5B — 2D/3D Vizualizáció
```

**Cella 2 (Code):**
```python
import sys
sys.path.insert(0, '..')
from engine import run_design_point
from visualization import plot_station_diagram, plot_ts_diagram, plot_3d_model

takeoff = run_design_point(flight_phase='takeoff', altitude_ft=0,     mach=0.25)
cruise  = run_design_point(flight_phase='cruise',  altitude_ft=35000, mach=0.82)
```

**Cella 3 (Code):**
```python
fig = plot_station_diagram(takeoff)
fig
```

**Cella 4 (Code):**
```python
fig3d = plot_3d_model(takeoff)
fig3d.write_html('cfm56_3d.html')
fig3d.show()
```

- [ ] **Step 4: Notebookok futtatása ellenőrzésként**

```bash
cd /Users/ziadmohamed/Documents/Uni/Szakdolgozat/Engine/Engine
source venv/bin/activate
jupyter nbconvert --to notebook --execute notebooks/01_design_point.ipynb --output notebooks/01_design_point_executed.ipynb
```

Elvárt: Hibamentes futás, `01_design_point_executed.ipynb` létrejön.

- [ ] **Step 5: Commit**

```bash
git add notebooks/
git commit -m "feat: add Jupyter notebooks for design point, off-design, and visualization"
```

---

## Task 7: Parancssoros szkriptek

**Files:**
- Create: `scripts/run_design.py`
- Create: `scripts/run_off_design.py`

- [ ] **Step 1: scripts/run_design.py létrehozása**

```python
# scripts/run_design.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import run_design_point
from visualization import plot_station_diagram, plot_3d_model

if __name__ == '__main__':
    print("CFM56-5B Design Point szimuláció — Felszállás")
    print("=" * 50)

    result = run_design_point(flight_phase='takeoff', altitude_ft=0, mach=0.25)
    result.summary()

    print("\nÁllomás adatok:")
    print(result.to_dataframe().to_string(index=False))

    fig2d = plot_station_diagram(result)
    fig2d.savefig('design_point_stations.png', dpi=150, bbox_inches='tight')
    print("\n2D diagram mentve: design_point_stations.png")

    fig3d = plot_3d_model(result)
    fig3d.write_html('cfm56_3d.html')
    print("3D modell mentve: cfm56_3d.html")
```

- [ ] **Step 2: scripts/run_off_design.py létrehozása**

```python
# scripts/run_off_design.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from engine import run_off_design
from visualization import plot_ts_diagram, plot_station_diagram

PHASES = [
    {'flight_phase': 'takeoff', 'altitude_ft': 0,      'mach': 0.25},
    {'flight_phase': 'climb',   'altitude_ft': 10000,  'mach': 0.50},
    {'flight_phase': 'cruise',  'altitude_ft': 35000,  'mach': 0.82},
]

if __name__ == '__main__':
    print("CFM56-5B Off-Design analízis — 3 repülési fázis")
    print("=" * 50)

    results = run_off_design(PHASES)

    for r in results:
        r.summary()
        print()

    summary = pd.DataFrame([{
        'Fázis':       r.flight_phase,
        'Magasság ft': r.altitude_ft,
        'Mach':        r.mach,
        'Tolóerő kN':  round(r.thrust_kN, 1),
        'SFC':         round(r.sfc, 5),
        'OPR':         round(r.opr, 2),
        'BPR':         round(r.bpr, 2),
    } for r in results])
    print("\nÖsszefoglaló táblázat:")
    print(summary.to_string(index=False))

    fig_ts = plot_ts_diagram(results)
    fig_ts.savefig('off_design_ts.png', dpi=150, bbox_inches='tight')
    print("\nT-s diagram mentve: off_design_ts.png")

    for r in results:
        fig = plot_station_diagram(r)
        fname = f'stations_{r.flight_phase}.png'
        fig.savefig(fname, dpi=150, bbox_inches='tight')
        print(f"Állomás-diagram mentve: {fname}")
```

- [ ] **Step 3: Szkriptek tesztelése**

```bash
cd /Users/ziadmohamed/Documents/Uni/Szakdolgozat/Engine/Engine
source venv/bin/activate
python scripts/run_design.py
```

Elvárt kimenet: Tolóerő, SFC, OPR értékek megjelennek, PNG és HTML fájlok létrejönnek.

- [ ] **Step 4: Commit**

```bash
git add scripts/
git commit -m "feat: add command-line scripts for design point and off-design analysis"
```

---

## Task 8: Összes teszt futtatása és validáció

- [ ] **Step 1: Teljes tesztcsomag futtatása**

```bash
cd /Users/ziadmohamed/Documents/Uni/Szakdolgozat/Engine/Engine
source venv/bin/activate
pytest tests/ -v
```

Elvárt: Minden teszt PASS.

- [ ] **Step 2: Szimulált értékek validálása irodalmi adatokkal**

A `run_design_point` futtatása után ellenőrizd:

| Paraméter | Szimulált | Irodalmi | Max. eltérés |
|-----------|-----------|----------|--------------|
| OPR | kb. 27.0 | 27.0 | ±5% |
| BPR | kb. 5.5 | 5.5 | ±5% |
| Tolóerő [kN] | 110–145 | 133.4 | ±10% |
| EGT [°C] | 900–970 | 940–950 | ±5% |

Ha az értékek kívül esnek: ellenőrizd a `CFM56_PARAMS` értékeit és a `burner.TtOut` beállítást.

- [ ] **Step 3: Végső commit**

```bash
git add .
git commit -m "chore: final validation and cleanup"
```

---

## Gyors referencia

```bash
# Virtuális környezet aktiválása
source venv/bin/activate

# Tesztek
pytest tests/ -v

# Design point futtatás
python scripts/run_design.py

# Off-design futtatás
python scripts/run_off_design.py

# Jupyter indítása
jupyter notebook notebooks/
```
