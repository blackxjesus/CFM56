# tests/test_start_plant.py
import pytest
from engine.start_transient import PlantParams, StartScenario, scenario_params, ff_frac


def test_plant_params_turbine_gain_anchored_to_idle():
    p = PlantParams()
    assert p.turbine_gain == pytest.approx(p.k_drag * p.idle_N2)


def test_scenario_params_normal():
    sp = scenario_params(StartScenario.NORMAL)
    assert sp == {'ff_cap': 1.0, 'fuel_mult': 1.0,
                  'fuel_valve_ok': True, 'igniter_ok': True, 'bleed_factor': 1.0}


def test_scenario_params_hung_caps_fuel():
    assert scenario_params(StartScenario.HUNG)['ff_cap'] == pytest.approx(0.7)


def test_scenario_params_no_fuel_blocks_valve():
    assert scenario_params(StartScenario.NO_FUEL)['fuel_valve_ok'] is False


def test_ff_frac_zero_below_lightoff():
    p = PlantParams()
    assert ff_frac(10.0, 1.0, p) == 0.0


def test_ff_frac_floor_at_lightoff():
    p = PlantParams()
    assert ff_frac(p.lightoff_N2, 1.0, p) == pytest.approx(p.ff_min)


def test_ff_frac_capped_for_hung():
    p = PlantParams()
    assert ff_frac(p.idle_N2, 0.7, p) == pytest.approx(0.7)


from engine.start_transient import dN2_dt, egt, derived_outputs


def test_torque_balances_at_idle_when_lit():
    p = PlantParams()
    rate = dN2_dt(p.idle_N2, lit=True, valve_open=False, p=p, ff_cap=1.0, bleed_factor=1.0)
    assert abs(rate) < 1e-6


def test_accelerates_from_zero_with_starter():
    p = PlantParams()
    rate = dN2_dt(0.0, lit=False, valve_open=True, p=p, ff_cap=1.0, bleed_factor=1.0)
    assert rate > 0.0


def test_motoring_plateau_no_fuel():
    p = PlantParams()
    rate_low = dN2_dt(10.0, lit=False, valve_open=True, p=p, ff_cap=1.0, bleed_factor=1.0)
    rate_high = dN2_dt(30.0, lit=False, valve_open=True, p=p, ff_cap=1.0, bleed_factor=1.0)
    assert rate_low > 0.0 and rate_high < 0.0


def test_egt_ambient_when_not_lit():
    p = PlantParams()
    assert egt(20.0, lit=False, fuel_mult=1.0, p=p) == pytest.approx(p.ambient_EGT)


def test_egt_lightoff_bump_below_redline_normal():
    p = PlantParams()
    peak = egt(p.bump_peak_N2, lit=True, fuel_mult=1.0, p=p)
    assert 500.0 < peak < p.egt_redline


def test_egt_hot_start_exceeds_redline():
    p = PlantParams()
    peak = egt(p.bump_peak_N2, lit=True, fuel_mult=1.8, p=p)
    assert peak > p.egt_redline


def test_derived_outputs_at_idle():
    p = PlantParams()
    n1, thr, ff = derived_outputs(p.idle_N2, lit=True, fuel_flowing=True, ff_cap=1.0, p=p)
    assert n1 == pytest.approx(p.idle_N1, rel=0.05)
    assert ff == pytest.approx(p.idle_FF, rel=0.05)
    assert thr == pytest.approx(p.idle_thrust, rel=0.05)
