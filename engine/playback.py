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
