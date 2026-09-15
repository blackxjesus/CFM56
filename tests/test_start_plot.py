# tests/test_start_plot.py
from engine.start_transient import simulate_start, StartScenario
from engine.fadec import EngMode, CockpitConfig
from visualization.start_plot import plot_start_transient

COCKPIT = CockpitConfig(mode=EngMode.IGN_START, master_on=True, bleed_available=True)


def _traces(fig):
    return {tr.name: tr for tr in fig.data}


def test_traces_drawn_up_to_current_frame():
    sd = simulate_start(StartScenario.NORMAL, COCKPIT)
    fig = plot_start_transient(sd, 10)
    tr = _traces(fig)
    for name in ('N1', 'N2', 'EGT', 'FF'):
        assert len(tr[name].x) == 11
    assert list(tr['N2'].y) == sd.N2[:11]


def test_time_axis_fixed_to_whole_start():
    # The x-axis must not rescale while the animation plays.
    sd = simulate_start(StartScenario.NORMAL, COCKPIT)
    fig = plot_start_transient(sd, 3)
    assert tuple(fig.layout.xaxis.range) == (0, sd.t[-1])


def test_full_trace_when_frame_is_last_and_redline_shown():
    sd = simulate_start(StartScenario.HOT, COCKPIT)
    last = len(sd.t) - 1
    fig = plot_start_transient(sd, last)
    assert len(_traces(fig)['EGT'].x) == len(sd.t)
    assert any('725' in (s.label.text or '') for s in fig.layout.shapes if s.label)
