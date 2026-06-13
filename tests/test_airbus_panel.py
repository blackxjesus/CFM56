# tests/test_airbus_panel.py
from visualization.airbus_panel import PANEL_CSS, panel_svg


def test_panel_css_is_style_block():
    assert isinstance(PANEL_CSS, str)
    assert PANEL_CSS.strip().startswith('<style>')
    assert PANEL_CSS.strip().endswith('</style>')


def test_panel_css_targets_expected_widgets():
    # Controls are styled st.button widgets, with a lit 'primary' state, on a
    # column styled as the panel surround.
    assert 'stButton' in PANEL_CSS
    assert 'kind="primary"' in PANEL_CSS
    assert 'panel-marker' in PANEL_CSS        # column styled as the panel via :has()
    assert 'ap-label' in PANEL_CSS


def test_panel_svg_reflects_state():
    svg = panel_svg('CRANK', master_on=True)
    assert svg.lstrip().startswith('<svg')
    assert 'rotate(-50' in svg                # knob pointer at CRANK
    assert 'ENG' in svg and 'FIRE' in svg


def test_panel_svg_norm_pointer_upright():
    assert 'rotate(0 190 150)' in panel_svg('NORM', master_on=False)
