# tests/test_engine_viewer.py
"""State sent to the 3D view (visualization/engine_viewer.py)."""
import json
import os

from engine.results import EngineResults, StationData, StartTransient
from visualization.engine_viewer import engine_view_state, STATIONS, _DIR


def _result():
    r = EngineResults(flight_phase='takeoff', altitude_ft=0, mach=0.25)
    for key, T, P, h in [('S2_inlet_exit', 292.0, 106.0, 0.0),
                         ('S3_hpc_exit', 800.0, 2796.0, 520.0),
                         ('S4_burner_exit', 1700.0, 2712.0, 1650.0),
                         ('S5_lpt_exit', 1071.0, 272.0, 900.0)]:
        r.stations[key] = StationData(station=key, T=T, P=P, h=h)
    return r


def _start():
    return StartTransient(scenario='NORMAL', t=[0.0, 0.5, 1.0],
                          N1=[0.0, 5.0, 10.0], N2=[0.0, 10.0, 20.0],
                          EGT=[15.0, 200.0, 400.0], FF=[0.0, 50.0, 100.0],
                          thrust=[0.0, 0.1, 0.2])


def test_off_rotor_stopped_reference_stations():
    s = engine_view_state('OFF', _result(), 80.0)
    assert s['mode'] == 'off' and s['n1'] == 0.0 and s['hot_K'] == 0.0
    assert s['reference'] is True
    assert [st['id'] for st in s['stations']] == ['2', '3', '4', '5']   # missing ones skipped
    assert s['stations'][2] == dict(id='4', name='Combustor exit',
                                    T=1700.0, P=2712.0, h=1650.0)


def test_running_uses_n1_and_t4():
    s = engine_view_state('RUNNING', _result(), 82.3456)
    assert s['n1'] == 82.35 and s['hot_K'] == 1700.0 and s['hot_label'] == 'T4'
    assert s['reference'] is False and 'trace' not in s


def test_starting_plays_trace_from_current_frame():
    s = engine_view_state('STARTING', _result(), 80.0, _start(), frame=1.6, speed=5)
    assert s['trace']['N1'] == [0.0, 5.0, 10.0]
    assert s['t0'] == 0.5 and s['rate'] == 5.0
    assert s['n1'] == 5.0 and s['hot_K'] == 473.1 and s['hot_label'] == 'EGT'


def test_fault_holds_last_frame():
    s = engine_view_state('FAULT', _result(), 80.0, _start(), frame=0.0, speed=10)
    assert s['rate'] == 0.0 and s['t0'] == 1.0 and s['n1'] == 10.0


def test_state_is_json_serialisable():
    json.dumps(engine_view_state('STARTING', _result(), 80.0, _start()))


def test_component_files_present():
    assert os.path.isfile(os.path.join(_DIR, 'index.html'))
    assert os.path.getsize(os.path.join(_DIR, 'cfm56-5b.glb')) > 1_000_000
    html = open(os.path.join(_DIR, 'index.html'), encoding='utf-8').read()
    for _, label, _ in STATIONS:      # every station has a marker position
        assert f"'{label}':" in html
