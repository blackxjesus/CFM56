# tests/test_simulation.py
import pytest
from engine.simulation import run_design_point, run_off_design
from engine.results import EngineResults

TAKEOFF = {'flight_phase': 'takeoff', 'altitude_ft': 0, 'mach': 0.25}


@pytest.fixture(scope='module')
def takeoff():
    return run_design_point(**TAKEOFF)


@pytest.fixture(scope='module')
def phases():
    return run_off_design([
        {'flight_phase': 'takeoff', 'altitude_ft': 0,     'mach': 0.25},
        {'flight_phase': 'cruise',  'altitude_ft': 35000, 'mach': 0.78, 'T4': 1500.0},
    ])


def test_run_design_point_returns_engine_results(takeoff):
    assert isinstance(takeoff, EngineResults)


def test_run_design_point_thrust_physical_range(takeoff):
    assert 60.0 < takeoff.thrust_kN < 200.0


def test_run_design_point_opr_physical_range(takeoff):
    assert 15.0 < takeoff.opr < 40.0


def test_run_design_point_stations_populated(takeoff):
    assert len(takeoff.stations) >= 4


def test_run_design_point_rejects_unphysical_T4():
    # Fixed compressor PRs and mass flow cannot be driven at very low T4.
    with pytest.raises(RuntimeError):
        run_design_point('takeoff', 0, 0.25, T4_override=1000.0)


def test_run_off_design_returns_list(phases):
    assert len(phases) == 2
    assert all(isinstance(r, EngineResults) for r in phases)


def test_off_design_mass_flow_drops_with_altitude(phases):
    takeoff, cruise = phases
    assert cruise.mass_flow < 0.6 * takeoff.mass_flow


def test_off_design_opr_not_frozen(phases):
    takeoff, cruise = phases
    assert cruise.opr != pytest.approx(takeoff.opr, abs=0.05)


def test_takeoff_full_power_is_valid(phases):
    assert phases[0].validity == []
    assert phases[0].N1 == pytest.approx(100.0, abs=2.0)


def test_cruise_at_takeoff_T4_is_flagged():
    cruise_max, = run_off_design([
        {'flight_phase': 'cruise', 'altitude_ft': 35000, 'mach': 0.78, 'T4': 1700.0}])
    assert any('N1' in note for note in cruise_max.validity)


def test_off_design_cruise_tsfc_higher_than_takeoff(phases):
    takeoff, cruise = phases
    assert cruise.sfc > takeoff.sfc
