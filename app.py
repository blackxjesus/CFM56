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
from visualization.ecam import estimate_n1, estimate_n2, compute_epr
from visualization.ewd import ewd_svg
from visualization.airbus_panel import PANEL_CSS, panel_image, hit_test
from streamlit_image_coordinates import streamlit_image_coordinates
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
ss.setdefault('mode', 'NORM')          # CRANK | NORM | IGN/START
ss.setdefault('master', False)
ss.setdefault('bleed', True)

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
    ss.started_scenario = scenario_name

def shutdown():
    ss.eng_state = 'OFF'
    ss.frame = 0.0
    ss.start_data = None

# ── Header ────────────────────────────────────────────────────────────────
st.title('✈️ CFM56-5B Engine Simulator')
st.caption('Termodinamikai szimulátor · Nyíregyházi Egyetem · Repülőmérnöki Szakdolgozat · DZRCRP')

col_panel, col_ecam = st.columns([1, 1.25])

# ── Airbus ENG panel (left) — illuminated pushbuttons ─────────────────────
with col_panel:
    st.markdown('<div class="panel-marker"></div>'
                '<div class="panel-title">ENG START PANEL</div>',
                unsafe_allow_html=True)
    off = ss.eng_state == 'OFF'

    # Clickable ENG panel image — click the ENG 1 switch / MODE knob / APU BLEED
    img = panel_image(ss.mode, ss.master, ss.bleed)
    key = f"engpanel_{ss.get('click_seq', 0)}"
    click = streamlit_image_coordinates(img, key=key)
    if click is not None:
        hit = hit_test(click['x'], click['y'])
        if hit:
            ss.click_seq = ss.get('click_seq', 0) + 1   # remount -> allow repeat clicks
            if hit == 'master':
                ss.master = not ss.master
            elif hit == 'bleed':
                ss.bleed = not ss.bleed
            elif hit == 'mode':
                order = ['CRANK', 'NORM', 'IGN/START']
                ss.mode = order[(order.index(ss.mode) + 1) % len(order)]
            st.rerun()
    st.caption('Click the panel: ENG 1 switch · MODE knob · APU BLEED')

    st.selectbox('SCENARIO (MAINT)',
                 ['NORMAL', 'HUNG', 'HOT', 'NO_FUEL', 'NO_IGNITION'],
                 key='scenario',
                 help='Pick a start fault, then start the engine. Changing it '
                      'while the engine is running restarts the start with that fault.')
    ss.speed = st.select_slider('SPEED', options=[1, 5, 10], value=ss.speed)

mode, master, bleed = ss.mode, ss.master, ss.bleed
scenario_name = ss.scenario

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
elif (ss.eng_state != 'OFF' and start_armed()
      and scenario_name != ss.get('started_scenario')):
    # fault changed while the engine is active -> restart the start with it
    begin_start(mode, master, bleed, scenario_name)
    st.rerun()
elif ss.eng_state == 'STARTING' and not start_armed():
    shutdown()
    st.rerun()
elif ss.eng_state in ('RUNNING', 'FAULT') and not master and mode != 'CRANK':
    shutdown()
    st.rerun()

# ── ECAM E/WD (right) ────────────────────────────────────────────────────
_GRN, _AMB, _RED = '#2bd92b', '#ffaa00', '#ff3b30'

with col_ecam:
    if ss.eng_state == 'OFF':
        components.html(ewd_svg(0, 0, 0, 0, 'READY FOR START', _GRN), height=720)

    elif ss.eng_state == 'STARTING':
        @st.fragment(run_every=TICK_DT)
        def _animate():
            sd = ss.start_data
            terminal = terminal_state_for(sd)
            new_state, new_frame = step_playback(
                ss.eng_state, ss.frame, len(sd.t), ss.speed, TICK_DT, SIM_DT, terminal)
            ss.frame = new_frame
            i = int(new_frame)
            status = 'CRANKING' if mode == 'CRANK' else 'STARTING'
            components.html(ewd_svg(sd.N1[i], sd.EGT[i], sd.N2[i], sd.FF[i],
                                    status, _AMB), height=720)
            ev = ' · '.join(f'{t:.0f}s {l}' for t, l in sd.events if t <= sd.t[i])
            st.caption(ev or '— standby —')
            if new_state != 'STARTING':
                ss.eng_state = new_state
                st.rerun()
        _animate()

    elif ss.eng_state == 'FAULT':
        sd = ss.start_data
        i = len(sd.t) - 1
        components.html(ewd_svg(sd.N1[i], sd.EGT[i], sd.N2[i], sd.FF[i],
                                sd.faults[0], _RED), height=720)
        ev = ' · '.join(f'{t:.0f}s {l}' for t, l in sd.events)
        st.caption(ev)
        st.error('FADEC: ' + ', '.join(sd.faults) + ' — set ENG MASTER OFF to clear.')

    elif ss.eng_state == 'RUNNING':
        throttle = ss.get('throttle', 0)
        phase = ss.get('phase', FLIGHT_PHASES[0])
        result = lookup[(phase, throttle)]
        egt_st = result.stations.get('S5_lpt_exit')
        egt_c = (egt_st.T - 273.15) if egt_st else 0.0
        components.html(ewd_svg(estimate_n1(throttle), egt_c, estimate_n2(throttle),
                                result.fuel_flow * 3600, '', _GRN,
                                epr=compute_epr(result), opr=result.opr,
                                sfc=result.sfc, thr=result.thrust_kN), height=720)

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

    # ── Engine performance parameters ───────────────────────────────────
    epr = compute_epr(result) or 1.0
    st.markdown('**Engine parameters**')
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric('Thrust', f'{result.thrust_kN:.1f} kN')
    m2.metric('EPR', f'{epr:.3f}')
    m3.metric('OPR', f'{result.opr:.2f}')
    m4.metric('BPR', f'{result.bpr:.2f}')
    m5.metric('SFC', f'{result.sfc:.5f}', help='kg/(kN·s)')
    m6.metric('Fuel flow', f'{result.fuel_flow * 3600:.0f} kg/h')

    with st.expander('Station thermodynamics (T, P, h)'):
        df = result.to_dataframe().rename(columns={
            'station': 'Station', 'T_K': 'T [K]', 'P_kPa': 'P [kPa]', 'h_kJkg': 'h [kJ/kg]'})
        st.dataframe(df.style.format({'T [K]': '{:.1f}', 'P [kPa]': '{:.1f}',
                                      'h [kJ/kg]': '{:.1f}'}),
                     use_container_width=True, hide_index=True)

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
