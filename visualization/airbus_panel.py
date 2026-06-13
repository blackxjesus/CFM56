# visualization/airbus_panel.py
"""
Airbus overhead ENG panel styling for the Streamlit app.

PANEL_CSS is a <style> block injected once via st.markdown(..., unsafe_allow_html=True).
It paints the Airbus grey-blue overhead panel, styles the interactive st.button
controls as white switch caps (lit green when ON/selected via type="primary"), and
defines the rotary ENG MODE knob graphic. `rotary_html(mode)` returns the knob HTML
with its pointer rotated to the current mode. `fire_fault_html()` returns the
decorative FIRE/FAULT annunciators for authenticity.

Caveat: this is CSS-on-Streamlit-buttons, not hardware-accurate 3D. See spec.
"""

PANEL_CSS = """<style>
/* ── Airbus grey-blue overhead panel frame ─────────────────────────────── */
/* The whole left column becomes the panel: it is the column that contains the
   hidden .panel-marker sentinel (st.markdown div's don't wrap later widgets,
   so we style the column via :has() instead). */
.panel-marker { display: none; }
[data-testid="column"]:has(.panel-marker) {
    background: linear-gradient(150deg, #8290a0 0%, #6b7886 55%, #586473 100%);
    border: 3px solid #3a434d;
    border-radius: 8px;
    padding: 16px 20px 22px;
    box-shadow: inset 0 1px 0 #9fabb8, inset 0 -3px 8px rgba(0,0,0,0.35),
                0 8px 22px rgba(0,0,0,0.6);
}
.panel-title {
    color: #f1f3f6; letter-spacing: 4px; font-size: 13px; font-weight: bold;
    font-family: 'Courier New', monospace; text-align: center; margin-bottom: 14px;
    border-bottom: 1px solid #4d5763; padding-bottom: 8px;
    text-shadow: 0 1px 1px rgba(0,0,0,0.4);
}
.ap-label {
    color: #161a1f; font-family: 'Courier New', monospace; font-size: 11px;
    font-weight: bold; letter-spacing: 2px; margin: 10px 0 4px;
    text-transform: uppercase;
}

/* ── White switch caps (st.button) ──────────────────────────────────────── */
div[data-testid="stButton"] > button {
    width: 100%;
    background: linear-gradient(180deg, #f5f5f0 0%, #d4d6cf 100%);
    color: #15171a;
    border: 1px solid #565b62;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
    font-weight: bold;
    letter-spacing: 1.5px;
    min-height: 50px;
    box-shadow: 0 3px 5px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.9);
    transition: all 0.08s ease;
}
div[data-testid="stButton"] > button:hover { border-color: #2a2d31; color: #000; }
div[data-testid="stButton"] > button:active { transform: translateY(1px); }

/* LIT / ON / selected -> type="primary" (Airbus green annunciator) */
div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(180deg, #eafbe9 0%, #b7e6b4 100%);
    color: #0a3d16;
    border: 1px solid #16a34a;
    text-shadow: 0 0 4px rgba(134,239,172,0.9);
    box-shadow: 0 0 12px rgba(34,197,94,0.7),
                inset 0 0 8px rgba(74,222,128,0.5),
                inset 0 1px 0 rgba(255,255,255,0.9);
}
div[data-testid="stButton"] > button[kind="primary"]:hover { border-color: #22c55e; }

/* ── Rotary ENG MODE knob ───────────────────────────────────────────────── */
.knob-wrap { position: relative; height: 150px; margin: 2px 0 6px; }
.knob {
    position: absolute; left: 50%; top: 48px; width: 80px; height: 80px;
    margin-left: -40px; border-radius: 50%;
    background: radial-gradient(circle at 38% 32%, #fbfbf8, #c4c6c0 58%, #8c8e87);
    border: 2px solid #45484d;
    box-shadow: 0 5px 9px rgba(0,0,0,0.55), inset 0 2px 4px rgba(255,255,255,0.7),
                inset 0 -3px 6px rgba(0,0,0,0.3);
}
.knob-ptr {
    position: absolute; left: 50%; top: 7px; width: 5px; height: 33px;
    margin-left: -2.5px; background: #15171a; border-radius: 2px;
    transform-origin: 50% 100%;
}
.knob-pos {
    position: absolute; font-family: 'Courier New', monospace; font-size: 10px;
    font-weight: bold; color: #15171a; letter-spacing: 1px;
}
.knob-pos.on { color: #0a3d16; text-shadow: 0 0 6px rgba(34,197,94,0.9); }
.kp-norm  { top: 2px;  left: 50%; transform: translateX(-50%); }
.kp-crank { top: 66px; left: 0; }
.kp-ign   { top: 66px; right: 0; }

/* ── Decorative FIRE / FAULT annunciators ──────────────────────────────── */
.fire-row { display: flex; justify-content: space-between; margin: 8px 0; }
.fire-btn {
    width: 46%; text-align: center; padding: 8px 0; border-radius: 4px;
    background: #2a0c0c; border: 1px solid #6e1a1a; color: #ff5a5a;
    font-family: 'Courier New', monospace; font-weight: bold; font-size: 11px;
    letter-spacing: 1px; box-shadow: inset 0 0 6px rgba(0,0,0,0.6);
}
</style>"""


def rotary_html(mode):
    """Return the rotary ENG MODE knob HTML with the pointer rotated to `mode`."""
    angles = {'CRANK': -52, 'NORM': 0, 'IGN/START': 52}
    ang = angles.get(mode, 0)

    def cls(pos):
        return 'knob-pos on' if pos == mode else 'knob-pos'

    return f"""<div class="knob-wrap">
        <div class="{cls('CRANK')} kp-crank">CRANK</div>
        <div class="{cls('NORM')} kp-norm">NORM</div>
        <div class="{cls('IGN/START')} kp-ign">IGN/<br>START</div>
        <div class="knob"><div class="knob-ptr" style="transform:rotate({ang}deg);"></div></div>
    </div>"""


def fire_fault_html():
    """Return the decorative FIRE/FAULT annunciator pair (engine 1)."""
    return """<div class="fire-row">
        <div class="fire-btn">FIRE<br>FAULT 1</div>
        <div class="fire-btn">FIRE<br>FAULT 2</div>
    </div>"""
