# tests/test_airbus_panel.py
from visualization.airbus_panel import (PANEL_CSS, panel_image, hit_test,
                                        PANEL_REGIONS, IMG_W, IMG_H)


def test_panel_css_is_style_block():
    assert isinstance(PANEL_CSS, str)
    assert PANEL_CSS.strip().startswith('<style>')
    assert PANEL_CSS.strip().endswith('</style>')
    assert 'panel-marker' in PANEL_CSS        # column styled as the panel via :has()


def test_panel_image_renders_at_fixed_size():
    img = panel_image('NORM', master_on=False, bleed_on=True)
    assert img.size == (IMG_W, IMG_H)
    assert img.mode == 'RGB'


def test_panel_image_state_changes_pixels():
    # Toggling the master should change the rendered image (lever/cap moves).
    off = panel_image('NORM', master_on=False, bleed_on=True).tobytes()
    on = panel_image('NORM', master_on=True, bleed_on=True).tobytes()
    assert off != on


def test_hit_test_maps_regions():
    # A click in the centre of each region resolves to that control.
    for name, (x0, y0, x1, y1) in PANEL_REGIONS.items():
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
        assert hit_test(cx, cy) == name


def test_hit_test_misses_empty_area():
    assert hit_test(2, 2) is None
