# Unified Real-Time A320 Engine Experience — Design Spec

**Date:** 2026-06-13
**Status:** Approved (brainstorming) — pending implementation plan
**Builds on:** `2026-06-13-engine-start-fadec-design.md` (transient start subsystem), branch `feat/engine-start-fadec`.

## 1. Purpose

Merge the app's two separate modes (Steady-State and Engine Start) into a single
continuous cockpit experience: cold-and-dark → real-time animated start →
"RUNNING" ready state where the engine is operated through the existing
steady-state data. Add full Airbus-style ENG controls and self-running real-time
gauge animation.

## 2. Engine state machine

A single `eng_state` held in `st.session_state` drives the whole screen:

```
OFF ──(MASTER ON + MODE in NORM/IGN + APU BLEED)──▶ STARTING
STARTING ──(N2 reaches idle, no fault)──▶ RUNNING
STARTING ──(fault detected)──▶ FAULT
RUNNING  ──(MASTER OFF)──▶ OFF        (shutdown)
FAULT    ──(MASTER OFF)──▶ OFF        (clear / dry-crank)
```

- **OFF** — cold & dark. Only the Airbus ENG panel is shown.
- **STARTING** — real-time auto-playing start; ECAM sweeps live with N1/N2/EGT/FF/THR.
- **RUNNING** — engine at idle = ready. Throttle lever + flight-phase selector
  unlock; full ECAM (N1/N2/EGT/EPR/FF/THR/OPR/SFC) + Station/T-s/3D diagrams go
  live from `data/lookup.pkl`.
- **FAULT** — start aborted; ECAM freezes on the fault frame with a red
  annunciation. MASTER OFF returns to OFF; CRANK mode available for dry motoring.

Scope: **single engine** (one ECAM column). Both columns are not modelled.

## 3. Real-time autoplay

Implemented with a Streamlit fragment:

```python
@st.fragment(run_every=0.1)   # 100 ms wall-clock tick
def _animate():
    ... advance frame while STARTING, render ECAM, rerun on transition ...
```

- The transient `StartTransient` (from `simulate_start`) is computed once when the
  start begins and stored in `st.session_state.start_data`.
- Each tick advances `frame` by `speed * tick_dt / sim_dt` sim-frames, where
  `sim_dt = 0.5 s` (the simulation step), `tick_dt = 0.1 s`, and `speed ∈ {1, 5, 10}`.
  So 1× ≈ real-time (~60 s), 10× ≈ ~6 s.
- When `frame` reaches the last frame: set `eng_state` to `RUNNING` (no faults) or
  `FAULT` (faults present) and call `st.rerun()` (full app rerun) so the
  throttle/phase controls and diagrams render.
- The fragment only advances while `eng_state == STARTING`; otherwise it is inert.

Speed is chosen via a small control in the panel. 10× is documented as the
smoothest for demos.

## 4. Airbus overhead ENG panel (full look)

Styled via CSS injected with `st.markdown(..., unsafe_allow_html=True)` applied to
real Streamlit widgets, wrapped in a dark metallic panel frame.

- **ENG MODE** — segmented rotary selector `CRANK · NORM · IGN/START`
  (a horizontal `st.radio` restyled as detented segments).
- **ENG MASTER 1** — guarded toggle switch with a green ON light (styled `st.toggle`).
- **APU BLEED** — Airbus pushbutton with blue **ON** indication / amber **FAULT**
  when unavailable (styled `st.toggle`/button).
- **Scenario injector** — NORMAL + the four faults (HUNG/HOT/NO_FUEL/NO_IGNITION),
  in a small "MAINT" sub-panel, only settable while OFF.
- **Speed** — 1× / 5× / 10× selector.

**Constraint (recorded):** This is CSS-on-Streamlit-widgets, not a hardware-accurate
3D panel. It reads convincingly as the Airbus ENG panel but interaction is via the
underlying real widgets.

## 5. Unified ECAM renderer

A single renderer replaces both the current `ecam_html` (in app.py) and
`start_ecam_html`. It renders whatever data is physically available for the state:

- **STARTING**: N1, N2, EGT (green < 500 °C, amber 500–700, red > 700/redline),
  FF, THR live from the transient frame; EPR/OPR/SFC show `---`; STARTER VALVE
  OPEN/CLOSED + IGN A/B indications; a rolling event line of FADEC events up to the
  current time.
- **RUNNING**: all eight fields (N1, N2, EGT, EPR, FF, THR, OPR, SFC) live from the
  `EngineResults` at the selected `(phase, throttle)`; STARTER VALVE CLOSED.
- The renderer is a pure function returning an HTML string, displayed via
  `streamlit.components.v1.html`.

Note: during START, EPR/OPR/SFC and station data are not available from the
transient model (they require the steady pyCycle data, valid only at/after idle),
hence the `---` placeholders. This matches the real Airbus ECAM start page.

## 6. RUNNING-state operation

Reuses existing machinery:
- Throttle slider (0–100 %) + flight-phase selector → key into `lookup[(phase, throttle)]`.
- Idle (just after start) corresponds to throttle 0.
- The existing `plot_station_diagram`, `plot_ts_diagram`, `plot_3d_model` render in
  tabs, exactly as the current Steady-State mode does.

## 7. File structure

| File | New? | Responsibility |
|------|------|----------------|
| `engine/playback.py` | new | Pure `step_playback(...)` — frame/state advance logic, no Streamlit. Unit-tested. |
| `visualization/ecam.py` | new | Pure HTML-string ECAM renderer(s) for START and RUNNING states. Smoke-tested. |
| `visualization/airbus_panel.py` | new | CSS + panel-chrome HTML strings for the Airbus ENG panel. |
| `app.py` | modified | State-machine orchestration, fragment autoplay, control wiring (Streamlit glue; manual verification). |

The existing `ecam_html` and `start_ecam_html` move into `visualization/ecam.py`
(unified into one renderer); `app.py` shrinks to orchestration.

## 8. `step_playback` contract

```python
def step_playback(eng_state, frame, n_frames, speed, tick_dt, sim_dt, terminal_state):
    """Advance the start playback by one wall-clock tick.

    Returns (new_eng_state, new_frame).
    - Only advances when eng_state == 'STARTING'; otherwise returns inputs unchanged.
    - new_frame = min(frame + speed*tick_dt/sim_dt, n_frames-1).
    - When frame reaches the last index: new_eng_state = terminal_state (caller-decided).
    """
```

`terminal_state` is computed by the caller from the `StartTransient`:
`'FAULT'` if faults present, `'RUNNING'` if it reached idle (N2 ≥ 0.95·idle), else
`'STARTING'` (hold at the last frame — e.g. CRANK dry-motoring, which never reaches
idle and is not a fault). This generalization lets CRANK hold at its plateau rather
than false-transitioning to RUNNING.

States are the string literals `'OFF' | 'STARTING' | 'RUNNING' | 'FAULT'`.

## 9. Testing

**Pure units (TDD):**
- `step_playback`: no advance when not STARTING; frame advances by speed factor;
  frame clamps at `n_frames-1`; transitions to RUNNING at end without faults and
  to FAULT at end with faults; speed scaling (10× advances 10× a 1× tick).
- `ecam.py` renderer: STARTING output contains N1/N2/EGT/FF/THR and `---` for
  EPR/OPR/SFC; RUNNING output contains all eight fields with numeric values; EGT
  color thresholds (green/amber/red) applied at the right boundaries.

**Manual (Streamlit glue):** launch `streamlit run app.py`; walk OFF → STARTING
(verify gauges auto-sweep at each speed) → RUNNING (throttle/phase/diagrams live);
trigger each fault → FAULT annunciation; MASTER OFF shutdown; CRANK dry-motoring.

Existing 50 automated tests must stay green.

## 10. Out of scope (YAGNI)

- Two independent engines / per-engine divergence (single engine only).
- Approximated EPR/OPR/SFC during START (shown as `---` instead).
- Diagrams during START (they appear only in RUNNING).
- Hardware-accurate 3D panel (CSS-styled widgets only).
- Auto-abort/recovery (FADEC remains detect-only, per the prior spec).
