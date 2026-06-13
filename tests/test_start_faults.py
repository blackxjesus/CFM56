# tests/test_start_faults.py
from engine.start_transient import simulate_start, StartScenario
from engine.fadec import EngMode, CockpitConfig

COCKPIT = CockpitConfig(mode=EngMode.IGN_START, master_on=True, bleed_available=True)


def test_hung_start_stagnates_below_idle():
    st = simulate_start(StartScenario.HUNG, COCKPIT)
    assert st.N2[-1] < 0.95 * 60.0
    assert 'HUNG START' in st.faults
    assert len(st.faults) == 1


def test_hot_start_exceeds_redline():
    st = simulate_start(StartScenario.HOT, COCKPIT)
    assert max(st.EGT) > 725.0
    assert 'EGT EXCEEDANCE' in st.faults
    assert len(st.faults) == 1


def test_no_fuel_motors_with_ambient_egt():
    st = simulate_start(StartScenario.NO_FUEL, COCKPIT)
    assert st.N2[-1] < 30.0
    assert max(st.EGT) <= 16.0
    assert max(st.FF) == 0.0
    assert 'NO LIGHT-OFF' in st.faults
    assert len(st.faults) == 1


def test_no_ignition_wet_start():
    st = simulate_start(StartScenario.NO_IGNITION, COCKPIT)
    assert max(st.EGT) <= 16.0
    assert max(st.FF) > 0.0
    assert 'WET START' in st.faults
    assert len(st.faults) == 1
