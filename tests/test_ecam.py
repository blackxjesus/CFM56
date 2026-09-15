# tests/test_ecam.py
from visualization.ecam import (egt_color, estimate_n1, estimate_n2,
                                 ecam_rows_starting, ecam_rows_running, render_ecam)
from engine.results import EngineResults, StationData, StartTransient


def test_egt_color_thresholds():
    assert egt_color(400) == '#00ff00'
    assert egt_color(600) == '#ffaa00'
    assert egt_color(720) == '#ff3030'


def test_starting_rows_have_placeholders_for_steady_only_fields():
    sd = StartTransient(scenario='NORMAL')
    sd.t.append(0.0); sd.N1.append(5.0); sd.N2.append(20.0)
    sd.EGT.append(300.0); sd.FF.append(400.0); sd.thrust.append(0.5)
    sd.start_valve.append(True); sd.igniter.append(True)
    rows = ecam_rows_starting(sd, 0)
    by_label = {r[0]: r[1] for r in rows}
    assert by_label['N1'] == '5.0'
    assert by_label['N2'] == '20.0'
    assert by_label['EGT'] == '300'
    assert by_label['FF'] == '400'
    assert by_label['EPR'] == '---'
    assert by_label['OPR'] == '---'
    assert by_label['SFC'] == '---'


def test_running_rows_all_numeric():
    r = EngineResults(flight_phase='takeoff', altitude_ft=0, mach=0.25,
                      thrust_kN=113.8, sfc=0.01351, opr=26.96, fuel_flow=1.538)
    r.stations['S2_inlet_exit'] = StationData(station='s2', T=300.0, P=105.8, h=0.0)
    r.stations['S8_core_nozz'] = StationData(station='s8', T=700.0, P=172.9, h=0.0)
    r.stations['S5_lpt_exit'] = StationData(station='s5', T=990.0, P=120.0, h=0.0)
    rows = ecam_rows_running(r, throttle=100)
    by_label = {r_[0]: r_[1] for r_ in rows}
    assert by_label['THR'] == '113.8'
    assert by_label['OPR'] == '26.96'
    assert by_label['EPR'] != '---'
    assert by_label['EGT'] == str(round(990.0 - 273.15))
    assert by_label['FF'] == str(round(1.538 * 3600))
    assert len(rows) == 8


def test_render_ecam_returns_html_with_labels():
    rows = [('N1', '5.0', '#00ff00', '%'), ('EGT', '300', '#ffaa00', '°C')]
    html = render_ecam(rows, valve=True, igniter=True,
                       events_line='0s STARTER ON', title='ENGINE · START')
    assert isinstance(html, str)
    assert 'N1' in html and 'EGT' in html
    assert 'STARTER VALVE' in html
    assert 'ENGINE · START' in html
