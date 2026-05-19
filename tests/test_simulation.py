# tests/test_simulation.py
import pytest
from engine.simulation import run_design_point, run_off_design
from engine.results import EngineResults

TAKEOFF = {'flight_phase': 'takeoff', 'altitude_ft': 0, 'mach': 0.25}


def test_run_design_point_returns_engine_results():
    result = run_design_point(**TAKEOFF)
    assert isinstance(result, EngineResults)


def test_run_design_point_thrust_physical_range():
    result = run_design_point(**TAKEOFF)
    assert 60.0 < result.thrust_kN < 200.0


def test_run_design_point_opr_physical_range():
    result = run_design_point(**TAKEOFF)
    assert 15.0 < result.opr < 40.0


def test_run_design_point_stations_populated():
    result = run_design_point(**TAKEOFF)
    assert len(result.stations) >= 4


def test_run_off_design_returns_list():
    phases = [
        {'flight_phase': 'takeoff', 'altitude_ft': 0,     'mach': 0.25},
        {'flight_phase': 'cruise',  'altitude_ft': 35000, 'mach': 0.82},
    ]
    results = run_off_design(phases)
    assert len(results) == 2
    assert all(isinstance(r, EngineResults) for r in results)
