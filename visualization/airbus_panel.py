# visualization/airbus_panel.py
"""
Airbus overhead ENG panel styling for the Streamlit app.

PANEL_CSS is a <style> block injected once via st.markdown(..., unsafe_allow_html=True).
The ENG controls are built from st.button widgets (not radio/toggle, which can't be
fully restyled) so they can be styled into illuminated Airbus pushbuttons. A button
rendered with type="primary" is the LIT/ON/selected state; type="secondary" is the
dark/unlit state. The `.ovhd-panel` class draws the dark metallic panel frame and
`.ap-label` is the small legend above each control.

Caveat: this is CSS-on-Streamlit-buttons, not hardware-accurate 3D. See spec.
"""

PANEL_CSS = """<style>
/* ── Dark metallic overhead-panel frame ───────────────────────────────── */
.ovhd-panel {
    background: linear-gradient(150deg, #34383d 0%, #202327 55%, #15181b 100%);
    border: 2px solid #0a0b0d;
    border-radius: 12px;
    padding: 16px 20px 22px;
    box-shadow: inset 0 1px 0 #50545a, inset 0 -3px 8px rgba(0,0,0,0.6),
                0 8px 22px rgba(0,0,0,0.65);
}
.ovhd-panel .panel-title {
    color: #e7e9ec; letter-spacing: 4px; font-size: 12px; font-weight: bold;
    font-family: 'Courier New', monospace; text-align: center; margin-bottom: 14px;
    border-bottom: 1px solid #44484e; padding-bottom: 8px;
}
.ap-label {
    color: #9aa0a6; font-family: 'Courier New', monospace; font-size: 11px;
    letter-spacing: 2px; margin: 12px 0 4px; text-transform: uppercase;
}

/* ── Airbus pushbutton-switches (st.button) ──────────────────────────── */
div[data-testid="stButton"] > button {
    width: 100%;
    background: linear-gradient(180deg, #2a2e33 0%, #14171a 100%);
    color: #c5c9cf;
    border: 1px solid #0a0b0d;
    border-top: 1px solid #444a51;
    border-radius: 5px;
    font-family: 'Courier New', monospace;
    font-weight: bold;
    letter-spacing: 1.5px;
    min-height: 56px;
    box-shadow: 0 3px 5px rgba(0,0,0,0.55), inset 0 1px 0 rgba(255,255,255,0.07);
    transition: all 0.08s ease;
}
div[data-testid="stButton"] > button:hover {
    border-top-color: #6b727a; color: #ffffff;
}
div[data-testid="stButton"] > button:active {
    box-shadow: inset 0 2px 5px rgba(0,0,0,0.7);
    transform: translateY(1px);
}

/* LIT / ON / selected state -> type="primary" */
div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(180deg, #1e3360 0%, #0c1830 100%);
    color: #eaf2ff;
    border: 1px solid #3b82f6;
    text-shadow: 0 0 6px rgba(147,197,253,0.9);
    box-shadow: 0 0 12px rgba(37,99,235,0.75),
                inset 0 0 10px rgba(96,165,250,0.45),
                inset 0 1px 0 rgba(255,255,255,0.12);
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    border-color: #60a5fa; color: #ffffff;
}
</style>"""
