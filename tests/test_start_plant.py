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
