"""Physical consistency of the solved pyCycle design point."""
import pytest
from engine.cfm56 import build_design_model, CFM56_PARAMS


@pytest.fixture(scope='module')
def solved_takeoff():
    prob = build_design_model()
    prob.set_val('fc.alt', 0.0, units='ft')
    prob.set_val('fc.MN', 0.25)
    prob.set_val('T4_target', CFM56_PARAMS['T4_design'], units='K')
    prob.run_model()
    return prob


def test_hp_shaft_power_balanced(solved_takeoff):
    pwr = solved_takeoff.get_val('hp_shaft.pwr_net', units='kW')[0]
    hpc = abs(solved_takeoff.get_val('hpc.power', units='kW')[0])
    assert abs(pwr) < 1e-3 * hpc


def test_lp_shaft_power_balanced(solved_takeoff):
    pwr = solved_takeoff.get_val('lp_shaft.pwr_net', units='kW')[0]
    fan = abs(solved_takeoff.get_val('fan.power', units='kW')[0])
    assert abs(pwr) < 1e-3 * fan


def test_t4_matches_target(solved_takeoff):
    T4 = solved_takeoff.get_val('burner.Fl_O:tot:T', units='K')[0]
    assert T4 == pytest.approx(CFM56_PARAMS['T4_design'], abs=0.5)


def test_nozzles_exhaust_to_ambient(solved_takeoff):
    ps0 = solved_takeoff.get_val('fc.Fl_O:stat:P', units='kPa')[0]
    for noz in ('core_nozz', 'byp_nozz'):
        assert solved_takeoff.get_val(f'{noz}.Ps_exhaust', units='kPa')[0] == pytest.approx(ps0, rel=1e-6)
