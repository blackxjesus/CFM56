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
from visualization.engine_viewer import engine_viewer, engine_view_state
from visualization.ecam import spool_speeds, compute_epr
from visualization.ewd import ewd_svg, EGT_START_LIMIT
from visualization.start_plot import plot_start_transient, EGT_TAKEOFF_LIMIT
from visualization.airbus_panel import PANEL_CSS, panel_image, hit_test
from streamlit_image_coordinates import streamlit_image_coordinates
from engine import simulate_start, StartScenario, CockpitConfig, EngMode
from engine.playback import step_playback, cockpit_action
from engine.trend import history_from_start, step_trend
from engine.fuel import burn_fuel, FOB_INITIAL_KG

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
ss.setdefault('trend', None)         # TrendHistory: start + running trace
ss.setdefault('speed', 10)
ss.setdefault('mode', 'NORM')          # CRANK | NORM | IGN/START
ss.setdefault('master', False)
ss.setdefault('bleed', True)
ss.setdefault('fob', FOB_INITIAL_KG)  # kg, burns with FF over sim time; reload refuels

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
    ss.trend = None
    ss.started_scenario = scenario_name

def shutdown():
    ss.eng_state = 'OFF'
    ss.frame = 0.0
    ss.start_data = None
    ss.trend = None

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

    # Clickable ENG panel image — click the ENG 1 switch / MODE position / APU BLEED
    img = panel_image(ss.mode, ss.master, ss.bleed)
    click = streamlit_image_coordinates(img, key='engpanel')
    # The component keeps returning its last click on every rerun, so each click
    # is handled once, identified by its timestamp.
    if click is not None and click.get('unix_time') != ss.get('last_click'):
        ss.last_click = click.get('unix_time')
        hit = hit_test(click['x'], click['y'], click.get('width'), click.get('height'))
        if hit:
            if hit == 'master':
                ss.master = not ss.master
            elif hit == 'bleed':
                ss.bleed = not ss.bleed
            elif hit.startswith('mode:'):
                ss.mode = hit.split(':', 1)[1]
            st.rerun()
    st.caption('Click the panel: ENG 1 switch · MODE position (CRANK / NORM / IGN/START) · APU BLEED')
    if ss.eng_state == 'OFF' and ss.master and ss.mode == 'NORM':
        st.info('Start: set MODE to IGN/START. NORM does not start the engine.')
    elif ss.eng_state == 'RUNNING' and ss.mode == 'IGN/START':
        st.info('Engine stabilised — MODE can be returned to NORM.')

    st.selectbox('SCENARIO (MAINT)',
                 ['NORMAL', 'HUNG', 'HOT', 'NO_FUEL', 'NO_IGNITION'],
                 key='scenario',
                 help='Pick a start fault, then start the engine. Changing it '
                      'while the engine is running restarts the start with that fault.\n\n'
                      '**NORMAL** – no fault. Light-off at ~18 % N2, starter cuts out '
                      'at ~50 % N2, stabilises at idle (~60 % N2) in about 60 s. '
                      'EGT peaks ~630 °C, below the 725 °C redline.\n\n'
                      '**HUNG** – fuel flow is limited to 70 % of schedule. The engine '
                      'lights normally, but as the starter assistance fades the spool stops '
                      'accelerating and hangs at ~45 % N2, before starter cutout '
                      'and below idle. '
                      'Flag: HUNG START.\n\n'
                      '**HOT** – too much fuel (×1.8) during light-off. EGT shoots past '
                      'the 725 °C redline (~980 °C) just after light-off; the engine '
                      'still reaches idle. Flag: EGT EXCEEDANCE.\n\n'
                      '**NO_FUEL** – the fuel valve stays shut. The starter spins the '
                      'core to ~22 % N2, but with no fuel there is no light-off: '
                      'FF = 0, EGT stays at ambient. Flag: NO LIGHT-OFF.\n\n'
                      '**NO_IGNITION** – igniters fail. Fuel flows into the combustor but '
                      'never lights: FF > 0, EGT stays at ambient, N2 stays at ~22 %. '
                      'Flag: WET START.\n\n'
                      'Faults are flagged, not acted on: the FADEC model detects them '
                      'but does not abort the start automatically.')
    ss.speed = st.select_slider('SPEED', options=[1, 5, 10], value=ss.speed)

mode, master, bleed = ss.mode, ss.master, ss.bleed
scenario_name = ss.scenario

# Decide whether to begin / shutdown based on control state
action = cockpit_action(ss.eng_state, mode, master, bleed,
                        scenario_changed=scenario_name != ss.get('started_scenario'))
if action == 'start':
    begin_start(mode, master, bleed, scenario_name)
    st.rerun()
elif action == 'shutdown':
    shutdown()
    st.rerun()

# ── ECAM E/WD (right) ────────────────────────────────────────────────────
_GRN, _AMB, _RED = '#2bd92b', '#ffaa00', '#ff3b30'

with col_ecam:
    if ss.eng_state == 'OFF':
        components.html(ewd_svg(0, 0, 0, 0, 'READY FOR START', _GRN, fob_kg=ss.fob,
                                egt_limit=EGT_START_LIMIT), height=720)

    elif ss.eng_state == 'STARTING':
        @st.fragment(run_every=TICK_DT)
        def _animate():
            sd = ss.start_data
            terminal = terminal_state_for(sd)
            new_state, new_frame = step_playback(
                ss.eng_state, ss.frame, len(sd.t), ss.speed, TICK_DT, SIM_DT, terminal)
            i = int(new_frame)
            # Fuel used over the sim time this tick advanced (SPEED x tick).
            ss.fob = burn_fuel(ss.fob, sd.FF[i], (new_frame - ss.frame) * SIM_DT)
            ss.frame = new_frame
            status = 'CRANKING' if mode == 'CRANK' else 'STARTING'
            components.html(ewd_svg(sd.N1[i], sd.EGT[i], sd.N2[i], sd.FF[i],
                                    status, _AMB, fob_kg=ss.fob,
                                    egt_limit=EGT_START_LIMIT), height=720)
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
                                sd.faults[0], _RED, fob_kg=ss.fob,
                                egt_limit=EGT_START_LIMIT), height=720)
        ev = ' · '.join(f'{t:.0f}s {l}' for t, l in sd.events)
        st.caption(ev)
        st.error('FADEC: ' + ', '.join(sd.faults) + ' — set ENG MASTER OFF to clear.')

    elif ss.eng_state == 'RUNNING':
        # The E/WD eases toward the selected operating point with a spool lag,
        # continuing the start trace, so the trends below stay continuous.
        if ss.trend is None:
            ss.trend = history_from_start(ss.start_data)
            ss.trend_throttle = None

        @st.fragment(run_every=TICK_DT)
        def _run():
            throttle = ss.get('throttle', 0)
            phase = ss.get('phase', FLIGHT_PHASES[0])
            result = lookup[(phase, throttle)]
            egt_st = result.stations.get('S5_lpt_exit')
            n1, n2 = spool_speeds(result, throttle)
            target = dict(N1=n1, N2=n2,
                          EGT=(egt_st.T - 273.15) if egt_st else 0.0,
                          FF=result.fuel_flow * 3600)
            label = None
            if ss.get('trend_throttle') is not None and throttle != ss.trend_throttle:
                label = f'THR {throttle}%'
            ss.trend_throttle = throttle
            cur = step_trend(ss.trend, target, ss.speed * TICK_DT, label=label)
            # FF = SFC x thrust of the operating point, eased like the gauges;
            # burned over SPEED x tick seconds of sim time.
            ss.fob = burn_fuel(ss.fob, cur['FF'], ss.speed * TICK_DT)
            components.html(ewd_svg(cur['N1'], cur['EGT'], cur['N2'], cur['FF'],
                                    '', _GRN, fob_kg=ss.fob,
                                    epr=compute_epr(result), opr=result.opr,
                                    sfc=result.sfc, thr=result.thrust_kN), height=720)
        _run()

# ── Engine trends: N1/N2, EGT, FF against time ─────────────────────────
# Live while STARTING (redrawn each tick from the frame the E/WD fragment
# advances), the full trace after a FAULT, and once RUNNING the start trace
# continues live through throttle changes (stepped by the E/WD fragment).
if ss.start_data is not None:
    st.divider()
    st.subheader('Engine trends')
    if ss.eng_state == 'STARTING':
        @st.fragment(run_every=TICK_DT)
        def _trend():
            if ss.eng_state != 'STARTING' or ss.start_data is None:
                return
            st.plotly_chart(plot_start_transient(ss.start_data, int(ss.frame)),
                            key='start_trend')
        _trend()
    elif ss.eng_state == 'FAULT':
        sd = ss.start_data
        st.plotly_chart(plot_start_transient(sd, len(sd.t) - 1), key='start_trend')
    elif ss.trend is not None:
        @st.fragment(run_every=TICK_DT)
        def _run_trend():
            h = ss.trend
            if ss.eng_state != 'RUNNING' or h is None:
                return
            st.plotly_chart(plot_start_transient(h, len(h.t) - 1, egt_limit=EGT_TAKEOFF_LIMIT,
                                                 limit_label='T/O LIMIT'),
                            key='start_trend')
        _run_trend()

# ── Cycle analysis: operating point, parameters + diagrams (always shown) ──
# The E/WD follows these controls only while the engine is RUNNING; the
# analysis below is available in every engine state.
st.divider()
st.subheader('Cycle analysis')
if ss.eng_state != 'RUNNING':
    st.caption('Steady-state operating point (reference) — the engine is not '
               'running; the cycle diagrams apply from idle upwards.')
c1, c2 = st.columns([2, 1])
with c1:
    phase = st.selectbox('Flight Phase', FLIGHT_PHASES, key='phase')
    throttle = st.slider('Throttle [%]', 0, 100, ss.get('throttle', 0), step=5,
                         key='throttle',
                         help='0% = T4 1000 K (low part power, not ground idle) | '
                              '100% = TOGA (T4 = 1700 K)')
    T4 = 1000.0 + throttle * 7.0
result = lookup[(phase, throttle)]
n1_c, n2_c = spool_speeds(result, throttle)
c1.caption(f'T4 = {T4:.0f} K   |   N1 = {n1_c:.1f}%   |   N2 = {n2_c:.1f}%   |   '
           f'VBV = {getattr(result, "vbv_frac", 0.0) * 100:.0f}%   (off-design solution)')
if getattr(result, 'validity', None):
    c1.warning('Operating point outside the valid model range: '
               + '; '.join(result.validity)
               + '. The real FADEC would limit thrust before this point.')

# ── Engine performance parameters ───────────────────────────────────────
epr = compute_epr(result) or 1.0
st.markdown('**Engine parameters**')
m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric('Thrust', f'{result.thrust_kN:.1f} kN')
m2.metric('P8/P2', f'{epr:.3f}',
          help='Core-nozzle to inlet total pressure ratio. Not a cockpit EPR: '
               'the A320 CFM56 sets thrust by N1.')
m3.metric('OPR', f'{result.opr:.2f}')
m4.metric('BPR', f'{result.bpr:.2f}')
m5.metric('SFC', f'{result.sfc * 1000:.2f} g/(kN·s)')
m6.metric('Fuel flow', f'{result.fuel_flow * 3600:.0f} kg/h')

with st.expander('Station thermodynamics (T, P, h)'):
    df = result.to_dataframe().rename(columns={
        'station': 'Station', 'T_K': 'T [K]', 'P_kPa': 'P [kPa]', 'h_kJkg': 'h [kJ/kg]'})
    st.dataframe(df.style.format({'T [K]': '{:.1f}', 'P [kPa]': '{:.1f}',
                                  'h [kJ/kg]': '{:.1f}'}),
                 width='stretch', hide_index=True)

tab1, tab2, tab3 = st.tabs(['📊 Station Diagram', '🌡️ T-s Diagram', '🔩 3D Model'])
with tab1:
    fig1 = plot_station_diagram(result)
    st.pyplot(fig1, width='content'); plt.close(fig1)
with tab2:
    fig2 = plot_ts_diagram([result])
    st.pyplot(fig2, width='content'); plt.close(fig2)
with tab3:
    # Linked to the engine state: rotor follows N1, the hot section glows with
    # T4 (running) or EGT (start), markers show this operating point's T, P, h.
    # During a start the view plays the trace in the browser at SPEED.
    engine_viewer(engine_view_state(ss.eng_state, result, n1_c, ss.start_data,
                                    ss.frame, ss.speed, SIM_DT))
