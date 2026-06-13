# tests/test_airbus_panel.py
from visualization.airbus_panel import PANEL_CSS


def test_panel_css_is_style_block():
    assert isinstance(PANEL_CSS, str)
    assert PANEL_CSS.strip().startswith('<style>')
    assert PANEL_CSS.strip().endswith('</style>')


def test_panel_css_targets_expected_widgets():
    assert 'stRadio' in PANEL_CSS
    assert 'stToggle' in PANEL_CSS
    assert 'ovhd-panel' in PANEL_CSS
