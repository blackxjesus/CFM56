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


def spool_speeds(result, throttle):
    """N1/N2 [%] from the off-design solution; empirical estimate as fallback."""
    n1 = getattr(result, 'N1', 0.0) or estimate_n1(throttle)
    n2 = getattr(result, 'N2', 0.0) or estimate_n2(throttle)
    return n1, n2


EGT_TAKEOFF_LIMIT = 950.0  # °C, EASA TCDS E.003
EGT_START_LIMIT = 725.0    # °C, EASA TCDS E.003


def egt_color(egt_c, limit=EGT_TAKEOFF_LIMIT):
    """Red above the EGT limit in force (start 725 °C / take-off 950 °C)."""
    return '#ff3030' if egt_c > limit else '#00ff00'


def compute_epr(result):
    """Core-nozzle to inlet total pressure ratio P8/P2.

    Not a cockpit EPR (the A320 CFM56 shows none); displayed as 'P8/P2'.
    """
    try:
        return result.stations['S8_core_nozz'].P / result.stations['S2_inlet_exit'].P
    except Exception:
        return None


def ecam_rows_starting(sd, i):
    """Rows for the STARTING phase. Steady-only fields show '---'."""
    n1 = sd.N1[i]; n2 = sd.N2[i]; egt = sd.EGT[i]; ff = sd.FF[i]; thr = sd.thrust[i]
    return [
        ('N1',  f'{n1:.1f}',  '#00ff00',          '%'),
        ('EGT', f'{egt:.0f}', egt_color(egt, EGT_START_LIMIT), '°C'),
        ('N2',  f'{n2:.1f}',  '#00cc00',          '%'),
        ('P8/P2', '---',       '#555',             ''),
        ('FF',  f'{ff:.0f}',  '#00e000',          'KG/H'),
        ('THR', f'{thr:.1f}', '#00e000',          'kN'),
        ('OPR', '---',         '#555',             ''),
        ('SFC', '---',         '#555',             'g/kN·s'),
    ]


def ecam_rows_running(result, throttle):
    """Rows for the RUNNING phase, all live from the steady EngineResults."""
    egt_st = result.stations.get('S5_lpt_exit')
    egt_c = round(egt_st.T - 273.15) if egt_st else 0
    epr = compute_epr(result) or 1.0
    n1, n2 = spool_speeds(result, throttle)
    return [
        ('N1',  f'{n1:.1f}', '#00ff00',       '%'),
        ('EGT', str(egt_c),                      egt_color(egt_c), '°C'),
        ('N2',  f'{n2:.1f}', '#00cc00',       '%'),
        ('P8/P2', f'{epr:.3f}',                  '#00ff00',       ''),
        ('FF',  str(round(result.fuel_flow * 3600)), '#00e000',  'KG/H'),
        ('THR', f'{result.thrust_kN:.1f}',       '#00e000',       'kN'),
        ('OPR', f'{result.opr:.2f}',             '#00e000',       ''),
        ('SFC', f'{result.sfc * 1000:.2f}',      '#00cc00',       'g/kN·s'),
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
