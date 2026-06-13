# visualization/airbus_panel.py
"""
Airbus overhead ENG panel for the Streamlit app.

Two pieces:
  * PANEL_CSS — a <style> block (injected once) that styles the left column as the
    Airbus panel surround and the st.button controls as switch caps.
  * panel_svg(mode, master_on) — a hand-built SVG that renders the ENG panel
    faithfully (dark slate body, corner screws, ENG 1/ENG 2 toggle switches with
    white caps, a 3D rotary MODE knob whose pointer rotates to the selection, and
    black FIRE buttons). It reflects state; the actual clicks are handled by the
    st.button controls placed beneath it.

Caveat: the SVG is the display; Streamlit buttons drive state. See spec.
"""

PANEL_CSS = """<style>
/* The whole left column is the panel surround (it contains .panel-marker). */
.panel-marker { display: none; }
[data-testid="column"]:has(.panel-marker) {
    background: linear-gradient(160deg, #2c3036 0%, #1c1f23 100%);
    border: 2px solid #0c0d0f;
    border-radius: 10px;
    padding: 14px 16px 18px;
    box-shadow: inset 0 1px 0 #44474c, 0 8px 22px rgba(0,0,0,0.6);
}
.ap-label {
    color: #9aa0a6; font-family: 'Courier New', monospace; font-size: 11px;
    font-weight: bold; letter-spacing: 2px; margin: 10px 0 4px; text-transform: uppercase;
}

/* Control buttons beneath the SVG: white switch caps, lit green when ON/selected */
div[data-testid="stButton"] > button {
    width: 100%;
    background: linear-gradient(180deg, #f5f5f0 0%, #d4d6cf 100%);
    color: #15171a; border: 1px solid #565b62; border-radius: 4px;
    font-family: 'Courier New', monospace; font-weight: bold; letter-spacing: 1px;
    min-height: 42px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.9);
    transition: all 0.08s ease;
}
div[data-testid="stButton"] > button:hover { border-color: #2a2d31; color: #000; }
div[data-testid="stButton"] > button:active { transform: translateY(1px); }
div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(180deg, #eafbe9 0%, #b7e6b4 100%);
    color: #0a3d16; border: 1px solid #16a34a;
    box-shadow: 0 0 10px rgba(34,197,94,0.65), inset 0 0 8px rgba(74,222,128,0.5),
                inset 0 1px 0 rgba(255,255,255,0.9);
}
</style>"""


def _toggle(cx, label, on):
    """One ENG MASTER toggle switch: base, lever (up=ON/down=OFF), white cap, labels."""
    word, num = label.split()
    if on:
        lever = (f'<line x1="{cx}" y1="128" x2="{cx}" y2="92" stroke="#d4d7db" '
                 f'stroke-width="8" stroke-linecap="round"/>')
        cap_y = 64
    else:
        lever = (f'<line x1="{cx}" y1="128" x2="{cx}" y2="162" stroke="#9aa0a6" '
                 f'stroke-width="8" stroke-linecap="round"/>')
        cap_y = 150
    base = (f'<ellipse cx="{cx}" cy="128" rx="14" ry="7" fill="#26292e" stroke="#0c0d0f"/>'
            f'<ellipse cx="{cx}" cy="126" rx="9" ry="4" fill="#3a3f45"/>')
    cap = (f'<rect x="{cx-19}" y="{cap_y}" width="38" height="30" rx="4" '
           f'fill="#edefe9" stroke="#777c83" stroke-width="1.5"/>'
           f'<text x="{cx}" y="{cap_y+13}" text-anchor="middle" font-size="9" '
           f'font-weight="bold" fill="#15171a" font-family="monospace">{word}</text>'
           f'<text x="{cx}" y="{cap_y+25}" text-anchor="middle" font-size="12" '
           f'font-weight="bold" fill="#15171a" font-family="monospace">{num}</text>')
    on_c = '#e6e9ed' if on else '#62666d'
    off_c = '#62666d' if on else '#e6e9ed'
    labels = (f'<text x="{cx-34}" y="100" font-size="9" fill="{on_c}" '
              f'font-family="monospace">ON</text>'
              f'<text x="{cx-36}" y="160" font-size="9" fill="{off_c}" '
              f'font-family="monospace">OFF</text>')
    return base + lever + cap + labels


def panel_svg(mode, master_on):
    """Render the ENG panel SVG, reflecting the MODE selection and ENG 1 master state."""
    ang = {'CRANK': -50, 'NORM': 0, 'IGN/START': 50}.get(mode, 0)
    grn = '#7CFC00'

    def mlabel(text, x, y, anchor, pos):
        col = grn if pos == mode else '#cfd2d6'
        return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="10" '
                f'font-weight="bold" fill="{col}" font-family="monospace">{text}</text>')

    screws = ''.join(
        f'<circle cx="{x}" cy="{y}" r="5" fill="#5a5f66" stroke="#1c1f23"/>'
        f'<line x1="{x-3}" y1="{y}" x2="{x+3}" y2="{y}" stroke="#1c1f23" stroke-width="1"/>'
        for x, y in ((26, 26), (354, 26), (26, 274), (354, 274)))

    knob = (
        '<defs><radialGradient id="kg" cx="38%" cy="32%">'
        '<stop offset="0%" stop-color="#fbfbf8"/><stop offset="60%" stop-color="#c2c4be"/>'
        '<stop offset="100%" stop-color="#8a8c85"/></radialGradient></defs>'
        '<circle cx="190" cy="150" r="32" fill="url(#kg)" stroke="#3a3d42" stroke-width="2"/>'
        '<circle cx="190" cy="150" r="32" fill="none" stroke="rgba(0,0,0,0.25)" stroke-width="1"/>'
        f'<g transform="rotate({ang} 190 150)">'
        '<line x1="190" y1="150" x2="190" y2="123" stroke="#15171a" stroke-width="5" '
        'stroke-linecap="round"/></g>')

    fire = (
        '<rect x="70" y="226" width="48" height="46" rx="4" fill="#0d0d0f" stroke="#5a1d1d"/>'
        '<text x="94" y="246" text-anchor="middle" font-size="7" fill="#c23b3b" '
        'font-family="monospace">FIRE</text>'
        '<text x="94" y="256" text-anchor="middle" font-size="7" fill="#c23b3b" '
        'font-family="monospace">FAULT</text>'
        '<text x="94" y="288" text-anchor="middle" font-size="11" fill="#cfd2d6" '
        'font-weight="bold" font-family="monospace">1</text>'
        '<rect x="262" y="226" width="48" height="46" rx="4" fill="#0d0d0f" stroke="#5a1d1d"/>'
        '<text x="286" y="246" text-anchor="middle" font-size="7" fill="#c23b3b" '
        'font-family="monospace">FIRE</text>'
        '<text x="286" y="256" text-anchor="middle" font-size="7" fill="#c23b3b" '
        'font-family="monospace">FAULT</text>'
        '<text x="286" y="288" text-anchor="middle" font-size="11" fill="#cfd2d6" '
        'font-weight="bold" font-family="monospace">2</text>')

    return f"""<svg viewBox="0 0 380 300" width="100%" xmlns="http://www.w3.org/2000/svg">
        <rect x="8" y="8" width="364" height="284" rx="12" fill="#444a52"
              stroke="#23262a" stroke-width="3"/>
        <rect x="8" y="8" width="364" height="284" rx="12" fill="none"
              stroke="rgba(255,255,255,0.08)" stroke-width="1"/>
        {screws}
        <text x="190" y="36" text-anchor="middle" font-size="13" font-weight="bold"
              fill="#e7e9ec" letter-spacing="3" font-family="monospace">ENG</text>
        {_toggle(95, 'ENG 1', master_on)}
        {_toggle(285, 'ENG 2', False)}
        {mlabel('MODE', 190, 112, 'middle', None)}
        {mlabel('NORM', 190, 128, 'middle', 'NORM')}
        {knob}
        {mlabel('CRANK', 150, 205, 'end', 'CRANK')}
        {mlabel('IGN/START', 230, 205, 'start', 'IGN/START')}
        {fire}
    </svg>"""
