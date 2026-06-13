# visualization/airbus_panel.py
"""
Airbus overhead ENG panel styling for the Streamlit app.

PANEL_CSS is a <style> block injected once via st.markdown(..., unsafe_allow_html=True).
It restyles the real Streamlit widgets (radio = ENG MODE rotary, toggles = ENG
MASTER / APU BLEED) to resemble the Airbus overhead ENG panel, and provides an
`.ovhd-panel` wrapper class for the dark metallic panel frame.

Caveat: this is CSS-on-Streamlit-widgets, not hardware-accurate 3D. See spec.
"""

PANEL_CSS = """<style>
/* Dark metallic overhead-panel frame */
.ovhd-panel {
    background: linear-gradient(145deg, #2a2d31, #16181b);
    border: 2px solid #0c0d0f;
    border-radius: 10px;
    padding: 18px 20px;
    box-shadow: inset 0 1px 0 #44474c, 0 6px 18px rgba(0,0,0,0.6);
    font-family: 'Courier New', monospace;
}
.ovhd-panel .panel-title {
    color: #cfd2d6; letter-spacing: 3px; font-size: 12px;
    text-align: center; margin-bottom: 12px; border-bottom: 1px solid #3a3d42;
    padding-bottom: 6px;
}

/* ENG MODE selector -> detented rotary segments */
div[data-testid="stRadio"] > div {
    flex-direction: row; gap: 0; background: #0d0e10;
    border: 1px solid #3a3d42; border-radius: 6px; overflow: hidden;
}
div[data-testid="stRadio"] label {
    margin: 0 !important; padding: 8px 14px; color: #9aa0a6;
    border-right: 1px solid #3a3d42; font-size: 12px; letter-spacing: 1px;
}
div[data-testid="stRadio"] label:has(input:checked) {
    background: #1d4ed8; color: #fff;
    box-shadow: inset 0 0 8px rgba(96,165,250,0.6);
}

/* ENG MASTER / APU BLEED toggles -> switch look */
div[data-testid="stToggle"] label { color: #cfd2d6; font-size: 12px; letter-spacing: 1px; }
div[data-testid="stToggle"] label:has(input:checked) { color: #4ade80; }

/* Lighted pushbutton hint */
.btn-light { display:inline-block; width:10px; height:10px; border-radius:2px;
    margin-left:6px; vertical-align:middle; }
.btn-on  { background:#2563eb; box-shadow:0 0 6px #2563eb; }
.btn-flt { background:#f59e0b; box-shadow:0 0 6px #f59e0b; }
</style>"""
