# visualization/ewd.py
"""
A320 ECAM Engine/Warning Display (E/WD) — SVG renderer.

ewd_svg(n1, egt, n2, ff, status_text, status_color, fob_kg) builds the upper-ECAM
engine display: dual round N1 and EGT dial gauges (needle + red-line + green
digital readout), N2 % and FF KG/H digital readouts, a per-engine status box
(READY FOR START / STARTING / fault), and the FOB line. Single-engine data is
mirrored into both ENG 1 and ENG 2 columns. Pure function, returns an SVG string
shown via streamlit.components.v1.html. No Streamlit import.

Gauge geometry: a 270° dial opening at the bottom; fraction 0 -> 1 maps to the
sweep 135°..405° (clockwise). N1 is scaled 0..110 %, EGT 0..1000 °C.
"""
import math

GREEN = '#2bd92b'
CYAN = '#3fd0e0'
AMBER = '#ffaa00'
RED = '#ff3b30'


def _polar(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def _arc(cx, cy, r, d0, d1, color, w):
    x0, y0 = _polar(cx, cy, r, d0)
    x1, y1 = _polar(cx, cy, r, d1)
    large = 1 if (d1 - d0) % 360 > 180 else 0
    return (f'<path d="M {x0:.1f} {y0:.1f} A {r} {r} 0 {large} 1 {x1:.1f} {y1:.1f}" '
            f'fill="none" stroke="{color}" stroke-width="{w}"/>')


def _gauge(cx, cy, r, frac, redfrac, value, vcolor, marks=None):
    frac = max(0.0, min(1.0, frac))
    sweep = 270.0
    bg = _arc(cx, cy, r, 135, 135 + sweep, '#3a3f45', 5)
    red = _arc(cx, cy, r, 135 + sweep * redfrac, 135 + sweep, RED, 5)
    lvl = _arc(cx, cy, r, 135, 135 + sweep * frac, GREEN, 5) if frac > 0 else ''
    ang = 135 + sweep * frac
    nx, ny = _polar(cx, cy, r * 0.82, ang)
    needle = (f'<line x1="{cx}" y1="{cy}" x2="{nx:.1f}" y2="{ny:.1f}" '
              f'stroke="#e8e8e8" stroke-width="3"/>'
              f'<circle cx="{cx}" cy="{cy}" r="4" fill="#cfd2d6"/>')
    tick = ''
    for mfrac, label in (marks or []):
        lx, ly = _polar(cx, cy, r * 0.62, 135 + sweep * mfrac)
        tick += (f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" '
                 f'font-size="10" fill="#9aa0a6" font-family="monospace">{label}</text>')
    by = cy + r * 0.48
    box = (f'<rect x="{cx-28}" y="{by:.0f}" width="56" height="22" rx="2" '
           f'fill="#06140a" stroke="{vcolor}" stroke-width="1.5"/>'
           f'<text x="{cx}" y="{by+16:.0f}" text-anchor="middle" font-size="16" '
           f'font-weight="bold" fill="{vcolor}" font-family="monospace">{value}</text>')
    return bg + red + lvl + tick + needle + box


def _digital(cx, cy, value, color):
    return (f'<rect x="{cx-30}" y="{cy-13}" width="60" height="24" rx="2" '
            f'fill="#06140a" stroke="{color}" stroke-width="1.2"/>'
            f'<text x="{cx}" y="{cy+5}" text-anchor="middle" font-size="16" '
            f'font-weight="bold" fill="{color}" font-family="monospace">{value}</text>')


def _param(cx, cy, label, value):
    return (f'<text x="{cx}" y="{cy}" text-anchor="middle" font-size="10" fill="{CYAN}" '
            f'font-family="monospace">{label}</text>'
            f'<text x="{cx}" y="{cy+17}" text-anchor="middle" font-size="14" '
            f'font-weight="bold" fill="{GREEN}" font-family="monospace">{value}</text>')


def _status_box(cx, cy, text, color):
    if not text:
        return ''
    w = max(120, 9 * len(text))
    return (f'<rect x="{cx-w/2:.0f}" y="{cy-13}" width="{w:.0f}" height="24" rx="3" '
            f'fill="#06140a" stroke="{color}" stroke-width="1.5"/>'
            f'<text x="{cx}" y="{cy+5}" text-anchor="middle" font-size="12" '
            f'font-weight="bold" fill="{color}" font-family="monospace">{text}</text>')


def ewd_svg(n1, egt, n2, ff, status_text, status_color, fob_kg=12000,
            epr=None, opr=None, sfc=None, thr=None, n1_lim='TOGA'):
    """Render the full dual-engine E/WD as an SVG string (data mirrored L/R).

    n1/egt/n2/ff are the live primary parameters. epr/opr/sfc/thr are the steady
    performance parameters (shown in the secondary row; '---' when None, i.e. not
    available during start).
    """
    n1_v = f'{n1:.1f}'
    egt_v = f'{round(egt)}'
    n2_v = f'{n2:.1f}'
    ff_v = f'{round(ff)}'
    egt_col = RED if egt > 725 else (AMBER if egt > 500 else GREEN)
    n1_marks = [(0.545, '6'), (0.909, '10')]
    epr_v = f'{epr:.3f}' if epr is not None else '---'
    opr_v = f'{opr:.2f}' if opr is not None else '---'
    sfc_v = f'{sfc:.4f}' if sfc is not None else '---'
    thr_v = f'{thr:.1f}' if thr is not None else '---'
    idle = '<text x="230" y="28" text-anchor="middle" font-size="11" fill="' + GREEN + \
        '" font-family="monospace">IDLE</text>' if 55 <= n2 <= 66 else ''

    parts = [
        '<svg viewBox="0 0 460 420" style="width:100%;max-width:440px;height:auto;'
        'display:block;margin:0 auto" xmlns="http://www.w3.org/2000/svg">',
        '<rect x="3" y="3" width="454" height="414" rx="10" fill="#070a07" '
        'stroke="#2a2f2a" stroke-width="2"/>',
        # top annunciations: bleed config + N1 LIM mode
        '<text x="120" y="26" text-anchor="middle" font-size="10" fill="' + CYAN +
        '" font-family="monospace">PACKS/NAI/WAI</text>',
        idle,
        f'<text x="430" y="22" text-anchor="end" font-size="10" fill="{CYAN}" '
        f'font-family="monospace">N1 LIM</text>'
        f'<text x="430" y="36" text-anchor="end" font-size="12" font-weight="bold" '
        f'fill="{GREEN}" font-family="monospace">{n1_lim}</text>',
        # ── N1 row ──
        '<text x="230" y="62" text-anchor="middle" font-size="13" fill="' + CYAN +
        '" font-family="monospace">N1</text>'
        '<text x="230" y="77" text-anchor="middle" font-size="10" fill="' + CYAN +
        '" font-family="monospace">%</text>',
        _gauge(108, 100, 44, n1 / 110.0, 100 / 110.0, n1_v, GREEN, n1_marks),
        _gauge(352, 100, 44, n1 / 110.0, 100 / 110.0, n1_v, GREEN, n1_marks),
        '<text x="230" y="118" text-anchor="middle" font-size="11" fill="' + CYAN +
        '" font-family="monospace">N2 %</text>',
        _digital(230, 140, n2_v, GREEN),
        # ── EGT row ──
        '<text x="230" y="205" text-anchor="middle" font-size="13" fill="' + CYAN +
        '" font-family="monospace">EGT</text>'
        '<text x="230" y="220" text-anchor="middle" font-size="10" fill="' + CYAN +
        '" font-family="monospace">&#176;C</text>',
        _gauge(108, 225, 42, egt / 1000.0, 0.9, egt_v, egt_col),
        _gauge(352, 225, 42, egt / 1000.0, 0.9, egt_v, egt_col),
        '<text x="230" y="252" text-anchor="middle" font-size="11" fill="' + CYAN +
        '" font-family="monospace">FF KG/H</text>',
        _digital(230, 274, ff_v, GREEN),
        # ── secondary performance params ──
        f'<line x1="30" y1="300" x2="430" y2="300" stroke="#2a2f2a" stroke-width="1"/>',
        _param(70, 322, 'EPR', epr_v),
        _param(170, 322, 'THR kN', thr_v),
        _param(290, 322, 'OPR', opr_v),
        _param(395, 322, 'SFC', sfc_v),
        # ── status boxes + FOB ──
        _status_box(108, 365, status_text, status_color),
        _status_box(352, 365, status_text, status_color),
        f'<text x="230" y="402" text-anchor="middle" font-size="12" fill="{CYAN}" '
        f'font-family="monospace">FOB: <tspan fill="{GREEN}">{round(fob_kg)}</tspan> KG</text>',
        '</svg>',
    ]
    return ''.join(parts)
