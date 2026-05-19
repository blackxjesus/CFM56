# tests/test_results.py
import pytest
from engine.results import StationData, EngineResults


def test_station_data_stores_values():
    s = StationData(station='fan_inlet', T=288.15, P=101.325, h=0.0)
    assert s.station == 'fan_inlet'
    assert s.T == pytest.approx(288.15)
    assert s.P == pytest.approx(101.325)


def test_engine_results_default_empty_stations():
    r = EngineResults(flight_phase='takeoff', altitude_ft=0, mach=0.25)
    assert r.stations == {}
    assert r.thrust_kN == 0.0


def test_engine_results_to_dataframe():
    r = EngineResults(flight_phase='takeoff', altitude_ft=0, mach=0.25)
    r.stations['inlet'] = StationData(station='inlet', T=288.15, P=101.325, h=0.0)
    r.stations['fan_exit'] = StationData(station='fan_exit', T=330.0, P=170.7, h=41.9)
    df = r.to_dataframe()
    assert len(df) == 2
    assert list(df.columns) == ['station', 'T_K', 'P_kPa', 'h_kJkg']


def test_engine_results_summary_runs(capsys):
    r = EngineResults(flight_phase='takeoff', altitude_ft=0, mach=0.25,
                      thrust_kN=133.4, sfc=0.01098, opr=27.0)
    r.summary()
    out = capsys.readouterr().out
    assert 'takeoff' in out
    assert '133.4' in out
