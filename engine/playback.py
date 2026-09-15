# engine/playback.py
"""
Pure frame/state advance logic for the real-time engine-start animation.

No Streamlit dependency — the Streamlit fragment in app.py calls step_playback
once per wall-clock tick. See
docs/superpowers/specs/2026-06-13-unified-realtime-cockpit-design.md.
"""


def start_armed(mode, master, bleed):
    """True when the panel commands a start sequence.

    A320 procedure: a start is only initiated with MODE at IGN/START and
    ENG MASTER ON (with bleed air). CRANK motors the engine dry. NORM never
    starts an engine.
    """
    if not bleed:
        return False
    if mode == 'IGN/START':
        return master
    return mode == 'CRANK'


def cockpit_action(eng_state, mode, master, bleed, scenario_changed=False):
    """Decide what the panel state does to the engine: 'start', 'shutdown' or None.

    - OFF: start when armed.
    - STARTING: abort when no longer armed (e.g. MODE back to NORM mid-start).
    - RUNNING / FAULT: only ENG MASTER OFF shuts down / clears; once the engine
      has stabilised the MODE selector can return to NORM.
    - A changed fault scenario restarts the start, but only while armed.
    """
    armed = start_armed(mode, master, bleed)
    if eng_state == 'OFF':
        return 'start' if armed else None
    if armed and scenario_changed:
        return 'start'
    if eng_state == 'STARTING' and not armed:
        return 'shutdown'
    if eng_state in ('RUNNING', 'FAULT') and not master:
        return 'shutdown'
    return None


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
