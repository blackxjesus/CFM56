# tests/test_visualization.py
import pytest
import matplotlib
matplotlib.use('Agg')  # headless — no display needed
import matplotlib.figure
import plotly.graph_objects as go

from engine.results import EngineResults, StationData
from visualization.station_diagram import plot_station_diagram
from visualization.ts_diagram import plot_ts_diagram
from visualization.model_3d import plot_3d_model


def _make_result(phase='takeoff'):
    r = EngineResults(flight_phase=phase, altitude_ft=0, mach=0.25,
                      thrust_kN=133.4, sfc=0.01098, opr=27.0, bpr=5.5)
    stations = [
        ('inlet_in',    288.15,  101.3,    0.0),
        ('fan_exit',    330.0,   170.7,   41.9),
        ('lpc_exit',    390.0,   341.4,  102.2),
        ('hpc_exit',    710.0,  2736.0,  430.0),
        ('burner_exit', 1700.0, 2654.0, 1600.0),
        ('hpt_exit',    1150.0,  680.0, 1050.0),
        ('lpt_exit',    820.0,   130.0,  540.0),
        ('core_nozz',   780.0,   101.3,  500.0),
    ]
    for name, T, P, h in stations:
        r.stations[name] = StationData(station=name, T=T, P=P, h=h)
    return r


def test_station_diagram_returns_figure():
    fig = plot_station_diagram(_make_result())
    assert isinstance(fig, matplotlib.figure.Figure)


def test_ts_diagram_returns_figure():
    results = [_make_result('takeoff'), _make_result('cruise')]
    fig = plot_ts_diagram(results)
    assert isinstance(fig, matplotlib.figure.Figure)


def test_3d_model_returns_plotly_figure():
    fig = plot_3d_model(_make_result())
    assert isinstance(fig, go.Figure)
