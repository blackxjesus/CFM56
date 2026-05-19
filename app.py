"""
CFM56-5B Thermodynamic Simulation — Streamlit Web App
Run with: streamlit run app.py
"""
import sys, os, pickle, math
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from visualization.station_diagram import plot_station_diagram
from visualization.ts_diagram import plot_ts_diagram
from visualization.model_3d import plot_3d_model

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

# ── Layout ────────────────────────────────────────────────────────────────
st.title('✈️ CFM56-5B Engine Simulator')
st.caption('Thermodynamic cycle simulation · Nyíregyházi Egyetem · BSc Thesis 2026')

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
    st.markdown(ecam_html(result, n1, n2), unsafe_allow_html=True)

st.divider()

# ── Diagrams ──────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(['📊 Station Diagram', '🌡️ T-s Diagram', '🔩 3D Model'])

with tab1:
    fig1 = plot_station_diagram(result)
    st.pyplot(fig1)
    plt.close(fig1)

with tab2:
    fig2 = plot_ts_diagram([result])
    st.pyplot(fig2)
    plt.close(fig2)

with tab3:
    fig3 = plot_3d_model(result)
    st.plotly_chart(fig3, use_container_width=True)
