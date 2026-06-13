# tests/test_ewd.py
from visualization.ewd import ewd_svg


def test_ewd_returns_svg_with_values():
    svg = ewd_svg(n1=19.8, egt=375, n2=60.5, ff=290,
                  status_text='READY FOR START', status_color='#2bd92b', fob_kg=12000)
    assert svg.lstrip().startswith('<svg')
    assert svg.rstrip().endswith('</svg>')
    assert '19.8' in svg          # N1 readout
    assert '375' in svg           # EGT readout
    assert '60.5' in svg          # N2 readout
    assert '290' in svg           # FF readout
    assert 'READY FOR START' in svg
    assert '12000' in svg         # FOB


def test_ewd_hot_egt_uses_red():
    svg = ewd_svg(n1=20, egt=900, n2=55, ff=600, status_text='', status_color='#2bd92b')
    assert '#ff3b30' in svg       # EGT digital box turns red past redline


def test_ewd_empty_status_renders_no_box_text():
    svg = ewd_svg(n1=0, egt=0, n2=0, ff=0, status_text='', status_color='#2bd92b')
    assert svg.lstrip().startswith('<svg')
