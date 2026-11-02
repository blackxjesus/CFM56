# tests/test_fuel.py
from engine.fuel import burn_fuel, FOB_INITIAL_KG


def test_one_hour_at_ff_uses_ff():
    assert burn_fuel(12000, 2400, 3600) == 9600


def test_ff_equals_sfc_times_thrust():
    # takeoff: SFC 13.44 g/(kN*s) * 113.7 kN = 1.528 kg/s = 5501 kg/h
    ff_kg_h = 13.44e-3 * 113.7 * 3600
    assert abs((12000 - burn_fuel(12000, ff_kg_h, 10.0)) - 13.44e-3 * 113.7 * 10) < 1e-9


def test_speed_scales_burn():
    # SPEED 10 -> one 0.1 s tick is 1 s of sim time: ten times the burn of SPEED 1
    slow = 12000 - burn_fuel(12000, 3600, 1 * 0.1)
    fast = 12000 - burn_fuel(12000, 3600, 10 * 0.1)
    assert abs(fast - 10 * slow) < 1e-9


def test_never_negative_and_no_burn_when_stopped():
    assert burn_fuel(5, 3600, 3600) == 0.0
    assert burn_fuel(100, 0, 60) == 100
    assert burn_fuel(100, 3600, 0) == 100
    assert FOB_INITIAL_KG == 12000
