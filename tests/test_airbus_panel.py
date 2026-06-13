# tests/test_airbus_panel.py
from visualization.airbus_panel import PANEL_CSS


def test_panel_css_is_style_block():
    assert isinstance(PANEL_CSS, str)
    assert PANEL_CSS.strip().startswith('<style>')
    assert PANEL_CSS.strip().endswith('</style>')


def test_panel_css_targets_expected_widgets():
    # Controls are styled st.button widgets (illuminated Airbus pushbuttons),
    # with a lit 'primary' state and the panel frame / legend classes.
    assert 'stButton' in PANEL_CSS
    assert 'kind="primary"' in PANEL_CSS
    assert 'panel-marker' in PANEL_CSS        # column styled as the panel via :has()
    assert 'ap-label' in PANEL_CSS
    assert 'knob' in PANEL_CSS                # rotary ENG MODE knob
