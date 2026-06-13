# tests/test_simulate_start.py
import pytest
from engine.start_transient import simulate_start, StartScenario
from engine.fadec import EngMode, CockpitConfig

NORMAL_COCKPIT = CockpitConfig(mode=EngMode.IGN_START, master_on=True, bleed_available=True)


def test_normal_start_reaches_idle():
    st = simulate_start(StartScenario.NORMAL, NORMAL_COCKPIT)
    assert st.N2[-1] >= 0.99 * 60.0
    assert st.N2[-1] <= 60.0 * 1.02


def test_normal_start_time_plausible():
    st = simulate_start(StartScenario.NORMAL, NORMAL_COCKPIT)
    assert 20.0 <= st.t[-1] <= 150.0


def test_normal_start_egt_peak_below_redline():
    st = simulate_start(StartScenario.NORMAL, NORMAL_COCKPIT)
    assert max(st.EGT) < 725.0


def test_time_monotonic_and_no_nans():
    import math
    st = simulate_start(StartScenario.NORMAL, NORMAL_COCKPIT)
    assert all(st.t[i] < st.t[i + 1] for i in range(len(st.t) - 1))
    assert all(not math.isnan(v) for v in st.N2 + st.EGT + st.FF)


def test_events_logged_in_order():
    st = simulate_start(StartScenario.NORMAL, NORMAL_COCKPIT)
    labels = [lbl for _, lbl in st.events]
    assert 'STARTER ON' in labels
    assert 'LIGHT-OFF' in labels
    assert 'IDLE' in labels
    assert labels.index('STARTER ON') < labels.index('LIGHT-OFF') < labels.index('IDLE')
