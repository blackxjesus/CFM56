# visualization/engine_viewer.py
"""Interactive CFM56-5B 3D model linked to the simulation.

A small Streamlit custom component (visualization/engine3d/index.html) shows
the glTF model with <model-viewer>. The iframe stays mounted between reruns,
so a throttle change only sends new values; the 12 MB model is loaded once.

What the view shows, per engine state:
  - station markers with T, P, h of the selected operating point;
  - hot section (combustor + exhaust) glowing with the local gas temperature:
    the station profile scaled to T4 at station 4 (running) or to EGT at
    station 5 (idle, start), so the nozzle glows only when it is hot there;
  - optional heat map: every part coloured by the gas temperature at its axial
    position, linear between the stations (core 2-21-25-3-4-45-5-8, casing
    2-21-18), same 300-1800 K scale as the markers; computed in the shader;
  - rotor spinning with N1 (visual speed, scaled down from the real rpm);
  - during a start the browser plays the N1/EGT trace itself, at the
    playback speed, from the frame the E/WD has reached.

Model: "CFM56-5B Engine A319 NEO 98-120 kN" by CloudHubOmniTeam (Sketchfab),
CC BY 4.0. Converted to metal-roughness materials with WebP textures
(gltf-transform metalrough + webp); geometry and animations unchanged.
The title says NEO, but the CFM56-5B powers the A319ceo; the NEO uses the
LEAP-1A or PW1100G.
"""
import os

import streamlit.components.v1 as components

_DIR = os.path.join(os.path.dirname(__file__), 'engine3d')
_component = components.declare_component('engine3d', path=_DIR)

# (station key in EngineResults.stations, marker label, description)
STATIONS = [
    ('S2_inlet_exit', '2', 'Fan inlet'),
    ('S21_fan_exit', '21', 'Fan exit'),
    ('S18_byp_nozz', '18', 'Bypass nozzle'),
    ('S25_lpc_exit', '25', 'Booster exit'),
    ('S3_hpc_exit', '3', 'HPC exit'),
    ('S4_burner_exit', '4', 'Combustor exit'),
    ('S45_hpt_exit', '45', 'HPT exit'),
    ('S5_lpt_exit', '5', 'LPT exit'),
    ('S8_core_nozz', '8', 'Core nozzle'),
]


def _stations(result):
    out = []
    for key, label, name in STATIONS:
        st = result.stations.get(key)
        if st is None:
            continue
        out.append(dict(id=label, name=name, T=round(st.T, 1),
                        P=round(st.P, 1), h=round(st.h, 1)))
    return out


def engine_view_state(eng_state, result, n1, start_data=None, frame=0.0,
                      speed=1, sim_dt=0.5, idle=None):
    """Plain dict sent to the 3D view. Pure function, no Streamlit.

    eng_state: 'OFF' | 'STARTING' | 'RUNNING' | 'FAULT'
    result:    EngineResults of the selected operating point (cycle analysis)
    n1:        N1 [%] of that operating point
    idle:      {N1, EGT, ...} when RUNNING at throttle 0 % (ground idle); the
               rotor and glow follow idle, the stations stay a reference
    """
    t4 = result.stations.get('S4_burner_exit')
    state = dict(
        mode=eng_state.lower(),
        stations=_stations(result),
        reference=eng_state != 'RUNNING',
        n1=0.0, hot_K=0.0, hot_label='',
    )
    if eng_state == 'RUNNING' and idle is not None:
        state.update(n1=round(float(idle['N1']), 2), reference=True,
                     hot_K=round(float(idle['EGT']) + 273.15, 1), hot_label='EGT')
    elif eng_state == 'RUNNING':
        state.update(n1=round(float(n1), 2),
                     hot_K=round(t4.T, 1) if t4 else 0.0, hot_label='T4')
    elif eng_state in ('STARTING', 'FAULT') and start_data is not None:
        sd = start_data
        last = len(sd.t) - 1
        i = last if eng_state == 'FAULT' else min(int(frame), last)
        state.update(
            n1=round(float(sd.N1[i]), 2),
            hot_K=round(float(sd.EGT[i]) + 273.15, 1), hot_label='EGT',
            trace=dict(t=[round(float(x), 3) for x in sd.t],
                       N1=[round(float(x), 2) for x in sd.N1],
                       EGT=[round(float(x), 1) for x in sd.EGT]),
            # The start plays in the browser from here, at `rate` sim-s per s.
            t0=float(sd.t[i]),
            rate=float(speed) if eng_state == 'STARTING' else 0.0,
        )
    return state


def engine_viewer(state, height=600, key='engine3d'):
    """Render the 3D view. Same key across reruns keeps the model loaded."""
    _component(state=state, height=height, key=key, default=None)


_throttle = components.declare_component(
    'throttle_lever', path=os.path.join(os.path.dirname(__file__), 'throttle'))

# Fixed rail in the left page margin: the lever stays in view while scrolling.
THROTTLE_CSS = """<style>
[data-testid="stMainBlockContainer"] { padding-left: 8rem; }
.st-key-throttle_rail {
    position: fixed; left: 16px; top: 50%; transform: translateY(-50%);
    width: 88px !important; z-index: 999;
}
</style>"""


def throttle_lever(value, height=300, key='throttle_lever'):
    """Vertical throttle lever, 0-100 % in 5 % steps; returns the set value."""
    v = _throttle(value=int(value), height=height, key=key, default=int(value))
    return int(v) if v is not None else int(value)
