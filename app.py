"""
CFM56-5B Thermodynamic Simulation — Streamlit Web App
Run with: streamlit run app.py
"""
import sys, os, pickle, math
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import streamlit.components.v1 as components
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from visualization.station_diagram import plot_station_diagram
from visualization.ts_diagram import plot_ts_diagram
from visualization.model_3d import plot_3d_model

from engine import simulate_start, StartScenario, CockpitConfig, EngMode

# ── Page config ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title='CFM56-5B Engine Simulator',
    page_icon='✈️',
    layout='wide',
)

# ── Load lookup table ────────────────────────────────────────────────────
@st.cache_resource
def load_lookup():
    with open('data/lookup.pkl', 'rb') as f:
        return pickle.load(f)

lookup = load_lookup()

FLIGHT_PHASES = [
    'Takeoff   (0 ft, Mach 0.25)',
    'Climb     (15 000 ft, Mach 0.50)',
    'Cruise    (35 000 ft, Mach 0.78)',
]

# ── N1/N2 estimates ──────────────────────────────────────────────────────
def estimate_n1(t): return 22.0 + 0.78 * t
def estimate_n2(t): return 70.0 + 0.30 * t

def compute_epr(result):
    try:
        return result.stations['S8_core_nozz'].P / result.stations['S2_inlet_exit'].P
    except Exception:
        return None

# ── ECAM HTML ─────────────────────────────────────────────────────────────
def ecam_html(result, n1, n2):
    egt_st = result.stations.get('S5_lpt_exit', result.stations.get('lpt_exit'))
    egt_c  = round(egt_st.T - 273.15) if egt_st else 0
    ff_kgh = round(result.fuel_flow * 3600)
    thr    = result.thrust_kN
    opr    = result.opr
    sfc    = result.sfc
    epr_v  = compute_epr(result) or 1.0

    rows = [
        ('N1',  f'{n1:.1f}',          f'{n1:.1f}',          '#00ff00', '%'),
        ('EGT', str(egt_c),            str(egt_c),            '#ffaa00', '°C'),
        ('N2',  f'{n2:.1f}',          f'{n2:.1f}',          '#00cc00', '%'),
        ('EPR', f'{epr_v:.3f}',        f'{epr_v:.3f}',        '#00ff00', ''),
        ('FF',  str(ff_kgh),           str(ff_kgh),           '#00e000', 'KG/H'),
        ('THR', f'{thr:.1f}',         f'{thr:.1f}',         '#00e000', 'kN'),
        ('OPR', f'{opr:.2f}',         f'{opr:.2f}',         '#00e000', ''),
        ('SFC', f'{sfc:.5f}',         f'{sfc:.5f}',         '#00cc00', 'kg/kN·s'),
    ]

    font_sizes = {
        'N1': '28px', 'EGT': '24px', 'N2': '20px', 'EPR': '20px',
        'FF': '18px', 'THR': '18px', 'OPR': '18px', 'SFC': '14px',
    }

    inner = ''
    for lbl, v1, v2, col, unit in rows:
        fs = font_sizes.get(lbl, '18px')
        inner += f"""
        <div style="display:flex;justify-content:space-between;
                    align-items:baseline;margin:5px 0;padding:2px 0;
                    border-bottom:1px solid #1a1a1a;">
          <span style="color:#888;font-size:11px;width:40px;">{lbl}</span>
          <span style="font-size:{fs};color:{col};font-weight:bold;">{v1}</span>
          <span style="font-size:{fs};color:{col};font-weight:bold;">{v2}</span>
          <span style="color:#555;font-size:10px;width:65px;text-align:right;">{unit}</span>
        </div>"""

    return f"""
    <div style="background:#050505;font-family:'Courier New',monospace;
                border:2px solid #444;border-radius:8px;padding:16px 20px;
                min-width:420px;">
      <div style="display:flex;justify-content:space-around;color:#00aaff;
                  font-size:12px;letter-spacing:2px;border-bottom:1px solid #333;
                  padding-bottom:8px;margin-bottom:10px;">
        <span>── ENGINE 1 ──</span>
        <span>── ENGINE 2 ──</span>
      </div>
      {inner}
      <div style="text-align:center;color:#333;font-size:8px;margin-top:10px;">
        EPR/EGT/FF/THR/OPR/SFC FROM SIMULATION · N1/N2 ESTIMATED
      </div>
    </div>"""

# ── Engine-start ECAM HTML ─────────────────────────────────────────────────
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

# ── Layout ────────────────────────────────────────────────────────────────
st.title('✈️ CFM56-5B Engine Simulator')
st.caption('Termodinamikai szimulátor · Nyíregyházi Egyetem · Repülőmérnöki Szakdolgozat · DZRCRP')

app_mode = st.radio('Mode', ['Steady-State', '🔥 Engine Start'], horizontal=True)

if app_mode == 'Steady-State':
    col_ctrl, col_ecam = st.columns([2, 1])

    with col_ctrl:
        phase = st.selectbox('Flight Phase', FLIGHT_PHASES)
        throttle = st.slider('Throttle [%]', 0, 100, 100, step=5,
                             help='0% = idle (T4 ≈ 1000K) | 100% = TOGA (T4 = 1700K)')
        T4 = 1000.0 + throttle * 7.0
        st.caption(f'T4 = {T4:.0f} K   |   N1 ≈ {estimate_n1(throttle):.1f}%   |   N2 ≈ {estimate_n2(throttle):.1f}%')

    result = lookup[(phase, throttle)]
    n1 = estimate_n1(throttle)
    n2 = estimate_n2(throttle)

    with col_ecam:
        components.html(ecam_html(result, n1, n2), height=400)

    st.divider()

    # ── Diagrams ──────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(['📊 Station Diagram', '🌡️ T-s Diagram', '🔩 3D Model'])

    with tab1:
        fig1 = plot_station_diagram(result)
        st.pyplot(fig1, use_container_width=False)
        plt.close(fig1)

    with tab2:
        fig2 = plot_ts_diagram([result])
        st.pyplot(fig2, use_container_width=False)
        plt.close(fig2)

    with tab3:
        fig3 = plot_3d_model(result)
        st.plotly_chart(fig3, use_container_width=True)

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
        step = float(st_data.t[1] - st_data.t[0]) if len(st_data.t) > 1 else 0.5
        frame = st.slider('Time [s]', 0.0, float(st_data.t[-1]), 0.0, step=step)
        i = min(range(len(st_data.t)), key=lambda k: abs(st_data.t[k] - frame))

        g1, g2 = st.columns([1, 1])
        with g1:
            components.html(start_ecam_html(st_data, i), height=360)
        with g2:
            df = st_data.to_dataframe().set_index('t')
            st.line_chart(df[['N1', 'N2']])
            st.line_chart(df[['EGT']])

        events_so_far = [f'{t:.1f}s — {lbl}' for t, lbl in st_data.events if t <= frame]
        st.write('  ·  '.join(events_so_far) or '— standby —')
        if st_data.faults:
            st.error('FADEC fault: ' + ', '.join(st_data.faults))
