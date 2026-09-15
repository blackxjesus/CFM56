import pytest

from engine.start_transient import simulate_start, StartScenario
from engine.fadec import EngMode, CockpitConfig
from engine.trend import history_from_start, step_trend, TrendHistory

COCKPIT = CockpitConfig(mode=EngMode.IGN_START, master_on=True, bleed_available=True)
TARGET = dict(N1=60.0, N2=85.0, EGT=600.0, FF=4000.0)


def test_history_continues_from_end_of_start():
    sd = simulate_start(StartScenario.NORMAL, COCKPIT)
    h = history_from_start(sd)
    n = len(h.t)
    cur = step_trend(h, TARGET, 1.0)
    assert len(h.t) == n + 1 and h.t[-1] == pytest.approx(sd.t[-1] + 1.0)
    # First step moves only part of the way: no jump to the target
    assert sd.N2[-1] < cur['N2'] < TARGET['N2']
    assert cur['N2'] - sd.N2[-1] < 0.5 * (TARGET['N2'] - sd.N2[-1])


def test_converges_to_target_and_logs_label():
    h = TrendHistory(t=[0.0], N1=[20.0], N2=[60.0], EGT=[450.0], FF=[600.0])
    step_trend(h, TARGET, 1.0, label='THR 50%')
    for _ in range(60):
        cur = step_trend(h, TARGET, 1.0)
    assert cur['FF'] == pytest.approx(TARGET['FF'], rel=1e-3)
    assert h.events == [(1.0, 'THR 50%')]


def test_window_trims_old_samples_and_events():
    h = TrendHistory(t=[0.0], N1=[0.0], N2=[0.0], EGT=[0.0], FF=[0.0],
                     events=[(0.0, 'STARTER ON')])
    for _ in range(20):
        step_trend(h, TARGET, 1.0, window=10.0)
    assert h.t[0] >= 10.0 and len(h.t) == len(h.N2)
    assert h.events == []
