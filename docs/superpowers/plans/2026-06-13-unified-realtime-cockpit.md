# Unified Real-Time A320 Engine Experience Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Merge the app's two modes into one continuous cockpit experience — cold-and-dark → real-time auto-playing engine start (Airbus controls) → "RUNNING" ready state operated through the existing steady-state data and diagrams.

**Architecture:** Two new pure, testable modules — `engine/playback.py` (frame/state advance logic) and `visualization/ecam.py` (HTML ECAM renderer) — plus `visualization/airbus_panel.py` (CSS chrome). `app.py` becomes a Streamlit state machine that uses a `st.fragment(run_every=...)` to auto-advance the start animation, then unlocks throttle/phase/diagrams in RUNNING.

**Tech Stack:** Python 3, Streamlit ≥1.33 (1.37.1 present — has `st.fragment`/`st.toggle`), `streamlit.components.v1.html`, matplotlib/plotly (existing), `pytest`.

---

## Reference constants & contracts (used across tasks)

- Engine states (string literals): `'OFF' | 'STARTING' | 'RUNNING' | 'FAULT'`.
- `SIM_DT = 0.5` (sim seconds per `StartTransient` frame), `TICK_DT = 0.1` (wall-clock fragment tick), speeds `{1, 5, 10}`.
- Idle N2 ≈ `60.0` (matches `PlantParams.idle_N2`).
- EGT color thresholds: `< 500 °C` green `#00ff00`, `500–700 °C` amber `#ffaa00`, `> 700 °C` red `#ff3030`.
- `StartTransient` fields available during START: `t, N1, N2, EGT, FF, thrust, start_valve, igniter, events, faults` (FF is kg/h).
- `EngineResults` (RUNNING) fields: `thrust_kN, sfc, opr, fuel_flow` (kg/s) and `stations['S5_lpt_exit'].T` (K), `compute_epr` uses `stations['S8_core_nozz'].P / stations['S2_inlet_exit'].P`.
- Flight phases (verbatim keys into `lookup`):
  ```python
  FLIGHT_PHASES = [
      'Takeoff   (0 ft, Mach 0.25)',
      'Climb     (15 000 ft, Mach 0.50)',
      'Cruise    (35 000 ft, Mach 0.78)',
  ]
  ```

---

## Task 1: `step_playback` frame/state advance logic

**Files:**
- Create: `engine/playback.py`
- Test: `tests/test_playback.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_playback.py
import pytest
from engine.playback import step_playback


def test_no_advance_when_not_starting():
    assert step_playback('OFF', 0.0, 100, 10, 0.1, 0.5, 'RUNNING') == ('OFF', 0.0)
    assert step_playback('RUNNING', 5.0, 100, 10, 0.1, 0.5, 'RUNNING') == ('RUNNING', 5.0)


def test_advances_by_speed_factor():
    # speed 10, tick 0.1, sim_dt 0.5 -> +10*0.1/0.5 = +2.0 frames per tick
    state, frame = step_playback('STARTING', 0.0, 100, 10, 0.1, 0.5, 'RUNNING')
    assert state == 'STARTING'
    assert frame == pytest.approx(2.0)


def test_speed_one_is_real_time():
    # speed 1 -> +1*0.1/0.5 = +0.2 frames per tick
    _, frame = step_playback('STARTING', 0.0, 100, 1, 0.1, 0.5, 'RUNNING')
    assert frame == pytest.approx(0.2)


def test_transitions_to_terminal_at_end_running():
    state, frame = step_playback('STARTING', 99.0, 100, 10, 0.1, 0.5, 'RUNNING')
    assert state == 'RUNNING'
    assert frame == pytest.approx(99.0)   # clamped to n_frames-1


def test_transitions_to_fault_at_end():
    state, _ = step_playback('STARTING', 99.0, 100, 10, 0.1, 0.5, 'FAULT')
    assert state == 'FAULT'


def test_crank_holds_at_last_frame_when_terminal_is_starting():
    # terminal_state 'STARTING' means hold (dry motoring): stay STARTING, clamp frame
    state, frame = step_playback('STARTING', 99.0, 100, 10, 0.1, 0.5, 'STARTING')
    assert state == 'STARTING'
    assert frame == pytest.approx(99.0)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_playback.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'engine.playback'`

- [ ] **Step 3: Create the module**

```python
# engine/playback.py
"""
Pure frame/state advance logic for the real-time engine-start animation.

No Streamlit dependency — the Streamlit fragment in app.py calls step_playback
once per wall-clock tick. See
docs/superpowers/specs/2026-06-13-unified-realtime-cockpit-design.md.
"""


def step_playback(eng_state, frame, n_frames, speed, tick_dt, sim_dt, terminal_state):
    """Advance the start playback by one wall-clock tick.

    Returns (new_eng_state, new_frame).

    - Only advances while eng_state == 'STARTING'; otherwise returns inputs unchanged.
    - Advances frame by speed * tick_dt / sim_dt sim-frames per tick.
    - On reaching the last frame (n_frames - 1): returns terminal_state and clamps
      the frame. terminal_state is caller-decided:
        'RUNNING'  — normal start reached idle
        'FAULT'    — a start fault was detected
        'STARTING' — hold at the last frame (e.g. CRANK dry motoring)
    """
    if eng_state != 'STARTING':
        return eng_state, frame
    new_frame = frame + speed * tick_dt / sim_dt
    last = n_frames - 1
    if new_frame >= last:
        return terminal_state, float(last)
    return 'STARTING', new_frame
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_playback.py -v`
Expected: PASS (6 passed)

- [ ] **Step 5: Commit**

```bash
git add engine/playback.py tests/test_playback.py
git commit -m "feat: add step_playback pure animation advance logic"
```

---

## Task 2: Unified ECAM renderer

**Files:**
- Create: `visualization/ecam.py`
- Test: `tests/test_ecam.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_ecam.py
from visualization.ecam import (egt_color, estimate_n1, estimate_n2,
                                 ecam_rows_starting, ecam_rows_running, render_ecam)
from engine.results import EngineResults, StationData, StartTransient


def test_egt_color_thresholds():
    assert egt_color(400) == '#00ff00'
    assert egt_color(600) == '#ffaa00'
    assert egt_color(720) == '#ff3030'


def test_starting_rows_have_placeholders_for_steady_only_fields():
    sd = StartTransient(scenario='NORMAL')
    sd.t.append(0.0); sd.N1.append(5.0); sd.N2.append(20.0)
    sd.EGT.append(300.0); sd.FF.append(400.0); sd.thrust.append(0.5)
    sd.start_valve.append(True); sd.igniter.append(True)
    rows = ecam_rows_starting(sd, 0)
    by_label = {r[0]: r[1] for r in rows}
    assert by_label['N1'] == '5.0'
    assert by_label['N2'] == '20.0'
    assert by_label['EGT'] == '300'
    assert by_label['FF'] == '400'
    assert by_label['EPR'] == '---'
    assert by_label['OPR'] == '---'
    assert by_label['SFC'] == '---'


def test_running_rows_all_numeric():
    r = EngineResults(flight_phase='takeoff', altitude_ft=0, mach=0.25,
                      thrust_kN=113.8, sfc=0.01351, opr=26.96, fuel_flow=1.538)
    r.stations['S2_inlet_exit'] = StationData(station='s2', T=300.0, P=105.8, h=0.0)
    r.stations['S8_core_nozz'] = StationData(station='s8', T=700.0, P=172.9, h=0.0)
    r.stations['S5_lpt_exit'] = StationData(station='s5', T=990.0, P=120.0, h=0.0)
    rows = ecam_rows_running(r, throttle=100)
    by_label = {r_[0]: r_[1] for r_ in rows}
    assert by_label['THR'] == '113.8'
    assert by_label['OPR'] == '26.96'
    assert by_label['EPR'] != '---'          # computed from station pressures
    assert by_label['EGT'] == str(round(990.0 - 273.15))
    assert by_label['FF'] == str(round(1.538 * 3600))
    assert len(rows) == 8


def test_render_ecam_returns_html_with_labels():
    rows = [('N1', '5.0', '#00ff00', '%'), ('EGT', '300', '#ffaa00', '°C')]
    html = render_ecam(rows, valve=True, igniter=True,
                       events_line='0s STARTER ON', title='ENGINE · START')
    assert isinstance(html, str)
    assert 'N1' in html and 'EGT' in html
    assert 'STARTER VALVE' in html
    assert 'ENGINE · START' in html
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_ecam.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'visualization.ecam'`

- [ ] **Step 3: Create the module**

```python
# visualization/ecam.py
"""
Unified ECAM panel renderer for the CFM56-5B simulator.

Pure functions that build the dual-purpose ECAM display used in both the
STARTING (transient) and RUNNING (steady-state) phases. Returns HTML strings
rendered via streamlit.components.v1.html. No Streamlit import here.
See docs/superpowers/specs/2026-06-13-unified-realtime-cockpit-design.md.
"""

# Row = (label, value_str, color, unit)


def estimate_n1(throttle):
    return 22.0 + 0.78 * throttle


def estimate_n2(throttle):
    return 70.0 + 0.30 * throttle


def egt_color(egt_c):
    if egt_c > 700:
        return '#ff3030'
    if egt_c >= 500:
        return '#ffaa00'
    return '#00ff00'


def compute_epr(result):
    try:
        return result.stations['S8_core_nozz'].P / result.stations['S2_inlet_exit'].P
    except Exception:
        return None


def ecam_rows_starting(sd, i):
    """Rows for the STARTING phase. Steady-only fields show '---'."""
    n1 = sd.N1[i]; n2 = sd.N2[i]; egt = sd.EGT[i]; ff = sd.FF[i]; thr = sd.thrust[i]
    return [
        ('N1',  f'{n1:.1f}',  '#00ff00',          '%'),
        ('EGT', f'{egt:.0f}', egt_color(egt),      '°C'),
        ('N2',  f'{n2:.1f}',  '#00cc00',          '%'),
        ('EPR', '---',         '#555',             ''),
        ('FF',  f'{ff:.0f}',  '#00e000',          'KG/H'),
        ('THR', f'{thr:.1f}', '#00e000',          'kN'),
        ('OPR', '---',         '#555',             ''),
        ('SFC', '---',         '#555',             'kg/kN·s'),
    ]


def ecam_rows_running(result, throttle):
    """Rows for the RUNNING phase, all live from the steady EngineResults."""
    egt_st = result.stations.get('S5_lpt_exit')
    egt_c = round(egt_st.T - 273.15) if egt_st else 0
    epr = compute_epr(result) or 1.0
    return [
        ('N1',  f'{estimate_n1(throttle):.1f}', '#00ff00',       '%'),
        ('EGT', str(egt_c),                      egt_color(egt_c), '°C'),
        ('N2',  f'{estimate_n2(throttle):.1f}', '#00cc00',       '%'),
        ('EPR', f'{epr:.3f}',                    '#00ff00',       ''),
        ('FF',  str(round(result.fuel_flow * 3600)), '#00e000',  'KG/H'),
        ('THR', f'{result.thrust_kN:.1f}',       '#00e000',       'kN'),
        ('OPR', f'{result.opr:.2f}',             '#00e000',       ''),
        ('SFC', f'{result.sfc:.5f}',             '#00cc00',       'kg/kN·s'),
    ]


def render_ecam(rows, *, valve, igniter, events_line, title):
    """Render the ECAM HTML for a single engine column from a list of Rows."""
    inner = ''
    for lbl, v, col, unit in rows:
        inner += f"""<div style="display:flex;justify-content:space-between;
            align-items:baseline;margin:5px 0;padding:2px 0;
            border-bottom:1px solid #1a1a1a;">
            <span style="color:#888;font-size:12px;width:46px;">{lbl}</span>
            <span style="font-size:24px;color:{col};font-weight:bold;">{v}</span>
            <span style="color:#555;font-size:10px;width:70px;text-align:right;">{unit}</span>
            </div>"""
    valve_txt = (f'<span style="color:{"#00ff00" if valve else "#555"}">'
                 f'STARTER VALVE {"OPEN" if valve else "CLOSED"}</span>')
    ign_txt = (f'<span style="color:{"#00ff00" if igniter else "#555"}">'
               f'IGN {"A/B" if igniter else "OFF"}</span>')
    return f"""<div style="background:#050505;font-family:'Courier New',monospace;
        border:2px solid #444;border-radius:8px;padding:16px 20px;min-width:380px;">
        <div style="text-align:center;color:#00aaff;font-size:13px;letter-spacing:2px;
            border-bottom:1px solid #333;padding-bottom:8px;margin-bottom:10px;">
            ── {title} ──</div>
        {inner}
        <div style="margin-top:10px;font-size:11px;display:flex;
            justify-content:space-between;">{valve_txt}{ign_txt}</div>
        <div style="margin-top:8px;color:#00aaff;font-size:11px;min-height:14px;">
            {events_line}</div>
        </div>"""
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_ecam.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add visualization/ecam.py tests/test_ecam.py
git commit -m "feat: add unified ECAM renderer (start + running rows)"
```

---

## Task 3: Airbus ENG panel CSS

**Files:**
- Create: `visualization/airbus_panel.py`
- Test: `tests/test_airbus_panel.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_airbus_panel.py
from visualization.airbus_panel import PANEL_CSS


def test_panel_css_is_style_block():
    assert isinstance(PANEL_CSS, str)
    assert PANEL_CSS.strip().startswith('<style>')
    assert PANEL_CSS.strip().endswith('</style>')


def test_panel_css_targets_expected_widgets():
    # styles the radio (ENG MODE) and toggle (MASTER / BLEED) widgets
    assert 'stRadio' in PANEL_CSS
    assert 'stToggle' in PANEL_CSS
    assert 'ovhd-panel' in PANEL_CSS
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_airbus_panel.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'visualization.airbus_panel'`

- [ ] **Step 3: Create the module**

```python
# visualization/airbus_panel.py
"""
Airbus overhead ENG panel styling for the Streamlit app.

PANEL_CSS is a <style> block injected once via st.markdown(..., unsafe_allow_html=True).
It restyles the real Streamlit widgets (radio = ENG MODE rotary, toggles = ENG
MASTER / APU BLEED) to resemble the Airbus overhead ENG panel, and provides an
`.ovhd-panel` wrapper class for the dark metallic panel frame.

Caveat: this is CSS-on-Streamlit-widgets, not hardware-accurate 3D. See spec.
"""

PANEL_CSS = """<style>
/* Dark metallic overhead-panel frame */
.ovhd-panel {
    background: linear-gradient(145deg, #2a2d31, #16181b);
    border: 2px solid #0c0d0f;
    border-radius: 10px;
    padding: 18px 20px;
    box-shadow: inset 0 1px 0 #44474c, 0 6px 18px rgba(0,0,0,0.6);
    font-family: 'Courier New', monospace;
}
.ovhd-panel .panel-title {
    color: #cfd2d6; letter-spacing: 3px; font-size: 12px;
    text-align: center; margin-bottom: 12px; border-bottom: 1px solid #3a3d42;
    padding-bottom: 6px;
}

/* ENG MODE selector -> detented rotary segments */
div[data-testid="stRadio"] > div {
    flex-direction: row; gap: 0; background: #0d0e10;
    border: 1px solid #3a3d42; border-radius: 6px; overflow: hidden;
}
div[data-testid="stRadio"] label {
    margin: 0 !important; padding: 8px 14px; color: #9aa0a6;
    border-right: 1px solid #3a3d42; font-size: 12px; letter-spacing: 1px;
}
div[data-testid="stRadio"] label:has(input:checked) {
    background: #1d4ed8; color: #fff;
    box-shadow: inset 0 0 8px rgba(96,165,250,0.6);
}

/* ENG MASTER / APU BLEED toggles -> switch look */
div[data-testid="stToggle"] label { color: #cfd2d6; font-size: 12px; letter-spacing: 1px; }
div[data-testid="stToggle"] label:has(input:checked) { color: #4ade80; }

/* Lighted pushbutton hint */
.btn-light { display:inline-block; width:10px; height:10px; border-radius:2px;
    margin-left:6px; vertical-align:middle; }
.btn-on  { background:#2563eb; box-shadow:0 0 6px #2563eb; }
.btn-flt { background:#f59e0b; box-shadow:0 0 6px #f59e0b; }
</style>"""
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_airbus_panel.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add visualization/airbus_panel.py tests/test_airbus_panel.py
git commit -m "feat: add Airbus overhead ENG panel CSS"
```

---

## Task 4: Rewrite `app.py` as the unified state machine

**Files:**
- Modify (full replace): `app.py`
- (No automated test — Streamlit glue; verified by ast-parse + headless smoke + manual.)

- [ ] **Step 1: Replace `app.py` with the unified implementation**

Replace the entire contents of `app.py` with:

```python
"""
CFM56-5B Engine Simulator — Unified real-time A320 cockpit experience.
Run with: streamlit run app.py

Flow: OFF (cold & dark) -> STARTING (real-time auto-play) -> RUNNING (operate)
      -> FAULT on a failed start. See
      docs/superpowers/specs/2026-06-13-unified-realtime-cockpit-design.md.
"""
import sys, os, pickle
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import streamlit.components.v1 as components
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from visualization.station_diagram import plot_station_diagram
from visualization.ts_diagram import plot_ts_diagram
from visualization.model_3d import plot_3d_model
from visualization.ecam import ecam_rows_starting, ecam_rows_running, render_ecam
from visualization.airbus_panel import PANEL_CSS
from engine import simulate_start, StartScenario, CockpitConfig, EngMode
from engine.playback import step_playback

# ── Config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title='CFM56-5B Engine Simulator', page_icon='✈️', layout='wide')
st.markdown(PANEL_CSS, unsafe_allow_html=True)

SIM_DT = 0.5
TICK_DT = 0.1
IDLE_N2 = 60.0

FLIGHT_PHASES = [
    'Takeoff   (0 ft, Mach 0.25)',
    'Climb     (15 000 ft, Mach 0.50)',
    'Cruise    (35 000 ft, Mach 0.78)',
]

@st.cache_resource
def load_lookup():
    with open('data/lookup.pkl', 'rb') as f:
        return pickle.load(f)

lookup = load_lookup()

ss = st.session_state
ss.setdefault('eng_state', 'OFF')      # OFF | STARTING | RUNNING | FAULT
ss.setdefault('frame', 0.0)
ss.setdefault('start_data', None)
ss.setdefault('speed', 10)

# ── Helpers ─────────────────────────────────────────────────────────────────
def terminal_state_for(sd):
    """Decide where the playback lands when it reaches the last frame."""
    if sd.faults:
        return 'FAULT'
    if sd.N2[-1] >= 0.95 * IDLE_N2:
        return 'RUNNING'
    return 'STARTING'   # CRANK dry-motoring / plateau: hold at last frame

def begin_start(mode_label, master_on, bleed, scenario_name):
    mode_map = {'CRANK': EngMode.CRANK, 'NORM': EngMode.NORM, 'IGN/START': EngMode.IGN_START}
    cockpit = CockpitConfig(mode=mode_map[mode_label], master_on=master_on,
                            bleed_available=bleed)
    ss.start_data = simulate_start(StartScenario[scenario_name], cockpit)
    ss.frame = 0.0
    ss.eng_state = 'STARTING'

def shutdown():
    ss.eng_state = 'OFF'
    ss.frame = 0.0
    ss.start_data = None

# ── Header ────────────────────────────────────────────────────────────────
st.title('✈️ CFM56-5B Engine Simulator')
st.caption('Termodinamikai szimulátor · Nyíregyházi Egyetem · Repülőmérnöki Szakdolgozat · DZRCRP')

col_panel, col_ecam = st.columns([1, 1])

# ── Airbus ENG panel (left) ──────────────────────────────────────────────
with col_panel:
    st.markdown('<div class="ovhd-panel"><div class="panel-title">ENG</div>',
                unsafe_allow_html=True)
    off = ss.eng_state == 'OFF'
    mode = st.radio('ENG MODE', ['CRANK', 'NORM', 'IGN/START'], index=1,
                    horizontal=True, key='eng_mode')
    master = st.toggle('ENG MASTER 1', key='master')
    bleed = st.toggle('APU BLEED', value=True, key='bleed')
    scenario_name = st.selectbox('SCENARIO (MAINT)',
                                 ['NORMAL', 'HUNG', 'HOT', 'NO_FUEL', 'NO_IGNITION'],
                                 disabled=not off,
                                 help='Inject a start fault while OFF.')
    ss.speed = st.select_slider('SPEED', options=[1, 5, 10], value=ss.speed)
    st.markdown('</div>', unsafe_allow_html=True)

# Decide whether to begin / shutdown based on control state
def start_armed():
    if not bleed:
        return False
    if mode in ('NORM', 'IGN/START') and master:
        return True
    if mode == 'CRANK':
        return True
    return False

if ss.eng_state == 'OFF' and start_armed():
    begin_start(mode, master, bleed, scenario_name)
    st.rerun()
elif ss.eng_state in ('RUNNING', 'FAULT') and not master and mode != 'CRANK':
    shutdown()
    st.rerun()

# ── ECAM + animation (right) ────────────────────────────────────────────
with col_ecam:
    if ss.eng_state == 'OFF':
        components.html(render_ecam(
            [(l, '---', '#555', u) for l, u in
             [('N1', '%'), ('EGT', '°C'), ('N2', '%'), ('EPR', ''),
              ('FF', 'KG/H'), ('THR', 'kN'), ('OPR', ''), ('SFC', 'kg/kN·s')]],
            valve=False, igniter=False, events_line='ENGINE OFF',
            title='ENGINE'), height=420)

    elif ss.eng_state == 'STARTING':
        @st.fragment(run_every=TICK_DT)
        def _animate():
            sd = ss.start_data
            terminal = terminal_state_for(sd)
            new_state, new_frame = step_playback(
                ss.eng_state, ss.frame, len(sd.t), ss.speed, TICK_DT, SIM_DT, terminal)
            ss.frame = new_frame
            i = int(new_frame)
            rows = ecam_rows_starting(sd, i)
            ev = ' · '.join(f'{t:.0f}s {l}' for t, l in sd.events if t <= sd.t[i])
            title = 'ENGINE · CRANK' if mode == 'CRANK' else 'ENGINE · START'
            components.html(render_ecam(rows, valve=sd.start_valve[i],
                                        igniter=sd.igniter[i], events_line=ev,
                                        title=title), height=420)
            if new_state != 'STARTING':
                ss.eng_state = new_state
                st.rerun()
        _animate()

    elif ss.eng_state == 'FAULT':
        sd = ss.start_data
        i = len(sd.t) - 1
        rows = ecam_rows_starting(sd, i)
        ev = ' · '.join(f'{t:.0f}s {l}' for t, l in sd.events)
        components.html(render_ecam(rows, valve=sd.start_valve[i],
                                    igniter=sd.igniter[i], events_line=ev,
                                    title='ENGINE · FAULT'), height=420)
        st.error('FADEC: ' + ', '.join(sd.faults) + ' — set ENG MASTER OFF to clear.')

    elif ss.eng_state == 'RUNNING':
        throttle = ss.get('throttle', 0)
        phase = ss.get('phase', FLIGHT_PHASES[0])
        result = lookup[(phase, throttle)]
        components.html(render_ecam(ecam_rows_running(result, throttle),
                                    valve=False, igniter=False,
                                    events_line='ENGINE RUNNING',
                                    title='ENGINE'), height=420)

# ── RUNNING controls + diagrams ─────────────────────────────────────────
if ss.eng_state == 'RUNNING':
    st.divider()
    c1, c2 = st.columns([2, 1])
    with c1:
        phase = st.selectbox('Flight Phase', FLIGHT_PHASES, key='phase')
        throttle = st.slider('Throttle [%]', 0, 100, ss.get('throttle', 0), step=5,
                             key='throttle',
                             help='0% = idle (T4 ≈ 1000K) | 100% = TOGA (T4 = 1700K)')
        T4 = 1000.0 + throttle * 7.0
        st.caption(f'T4 = {T4:.0f} K')
    result = lookup[(phase, throttle)]

    tab1, tab2, tab3 = st.tabs(['📊 Station Diagram', '🌡️ T-s Diagram', '🔩 3D Model'])
    with tab1:
        fig1 = plot_station_diagram(result)
        st.pyplot(fig1, use_container_width=False); plt.close(fig1)
    with tab2:
        fig2 = plot_ts_diagram([result])
        st.pyplot(fig2, use_container_width=False); plt.close(fig2)
    with tab3:
        fig3 = plot_3d_model(result)
        st.plotly_chart(fig3, use_container_width=True)
```

- [ ] **Step 2: Verify the file parses**

Run: `python -c "import ast; ast.parse(open('app.py').read()); print('AST OK')"`
Expected: prints `AST OK`

- [ ] **Step 3: Headless smoke test of the imported pure helpers used by app**

Run:
```bash
python -c "
from engine import simulate_start, StartScenario, CockpitConfig, EngMode
from engine.playback import step_playback
from visualization.ecam import ecam_rows_starting, ecam_rows_running, render_ecam
sd = simulate_start(StartScenario.NORMAL, CockpitConfig())
# simulate the fragment loop at 10x until it leaves STARTING
state, frame = 'STARTING', 0.0
for _ in range(100000):
    state, frame = step_playback(state, frame, len(sd.t), 10, 0.1, 0.5, 'RUNNING' if not sd.faults else 'FAULT')
    if state != 'STARTING': break
print('ended in', state, 'at frame', int(frame), 'of', len(sd.t)-1)
assert state == 'RUNNING'
html = render_ecam(ecam_rows_starting(sd, 5), valve=True, igniter=True, events_line='x', title='T')
assert 'N1' in html
print('SMOKE OK')
"
```
Expected: prints `ended in RUNNING ...` then `SMOKE OK`

- [ ] **Step 4: Launch and confirm it starts**

Run: `streamlit run app.py --server.headless true --server.port 8502 > /tmp/st_unified.log 2>&1 &` then after ~6 s `cat /tmp/st_unified.log` and `curl -s http://localhost:8502/_stcore/health`.
Expected: log shows "You can now view your Streamlit app", health returns `ok`. (Stop the server afterward.)

- [ ] **Step 5: Commit**

```bash
git add app.py
git commit -m "feat: unified real-time cockpit (OFF/STARTING/RUNNING/FAULT state machine)"
```

---

## Task 5: Manual visual verification & polish checkpoint

**Files:** `app.py`, `visualization/airbus_panel.py`, `visualization/ecam.py` (CSS/markup tweaks only, as needed)

This task is an interactive checkpoint — CSS/Streamlit rendering can only be judged in a browser. No new automated tests; do not change the tested pure logic in `engine/playback.py` or the row-builder return shapes in `visualization/ecam.py`.

- [ ] **Step 1: Run the app and walk every state**

Run: `streamlit run app.py`
Verify in the browser:
- **OFF**: only the Airbus ENG panel + a dashed `---` ECAM are shown; no throttle/diagrams.
- **Start**: ENG MODE → IGN/START, APU BLEED on, ENG MASTER 1 on → ECAM auto-sweeps in real time (try SPEED 1×, 5×, 10×); events tick in order STARTER ON → IGNITION ON → LIGHT-OFF → STARTER CUTOUT → IDLE.
- **RUNNING**: on reaching idle, the throttle slider + flight-phase selector + Station/T-s/3D tabs appear; full ECAM (N1/N2/EGT/EPR/FF/THR/OPR/SFC) is live; moving throttle/phase updates everything.
- **Faults**: set SCENARIO to HOT / HUNG / NO_FUEL / NO_IGNITION while OFF, then start → ECAM freezes on the fault with a red FADEC annunciation; MASTER OFF clears to OFF.
- **CRANK**: ENG MODE → CRANK (MASTER off) → dry-motoring ECAM holds at the plateau, no light-off, no RUNNING transition.

- [ ] **Step 2: Polish CSS/layout in collaboration with the user**

Adjust `PANEL_CSS` (panel frame, rotary segments, switch look, lighted pushbutton) and ECAM spacing/sizing until it reads as the Airbus ENG panel and the gauges look right. Keep changes confined to CSS strings and markup; re-run `python -c "import ast; ast.parse(open('app.py').read())"` after edits.

- [ ] **Step 3: Confirm the full automated suite still passes**

Run: `pytest tests/ -q`
Expected: all tests pass (62 = prior 50 + 6 playback + 4 ecam + 2 airbus_panel).

- [ ] **Step 4: Commit any polish changes**

```bash
git add app.py visualization/airbus_panel.py visualization/ecam.py
git commit -m "polish: Airbus ENG panel + ECAM visual refinements"
```

---

## Self-Review notes (addressed)

- **Spec coverage:** state machine (Task 4), real-time autoplay via fragment + `step_playback` (Tasks 1, 4), Airbus panel (Task 3), unified ECAM with START `---` placeholders + RUNNING full data (Task 2), RUNNING throttle/phase/diagrams reusing existing plots (Task 4), single engine (one ECAM column throughout), testing of pure units + manual glue (Tasks 1–2, 5). All spec sections map to a task.
- **`terminal_state` vs `has_faults`:** the spec §8 named `has_faults`; this plan generalizes to a caller-computed `terminal_state` so CRANK dry-motoring can hold (`'STARTING'`) rather than false-transition to RUNNING. Spec §8 updated to match.
- **Type/name consistency:** `step_playback(eng_state, frame, n_frames, speed, tick_dt, sim_dt, terminal_state)`, `ecam_rows_starting(sd, i)`, `ecam_rows_running(result, throttle)`, `render_ecam(rows, *, valve, igniter, events_line, title)`, `PANEL_CSS`, states `'OFF'|'STARTING'|'RUNNING'|'FAULT'` — used identically across tasks.
- **Reuse:** RUNNING state reuses existing `plot_station_diagram`, `plot_ts_diagram`, `plot_3d_model`, and `lookup`. `estimate_n1/n2`/`compute_epr` move into `visualization/ecam.py` (single home); the old `app.py` `ecam_html`/`start_ecam_html` are replaced by the unified renderer.
