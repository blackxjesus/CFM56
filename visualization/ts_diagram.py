# visualization/ts_diagram.py
import matplotlib.pyplot as plt
import numpy as np
from typing import List
from engine.results import EngineResults

_STATION_ORDER = [
    'S0_freestream', 'S2_inlet_exit', 'S21_fan_exit', 'S25_lpc_exit',
    'S3_hpc_exit', 'S4_burner_exit', 'S45_hpt_exit', 'S5_lpt_exit', 'S8_core_nozz',
    'inlet_in', 'fan_exit', 'lpc_exit', 'hpc_exit',
    'burner_exit', 'hpt_exit', 'lpt_exit', 'core_nozz',
]
_COLORS = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3']


def _entropy_approx(stations_data, cp=1.005):
    """Approximate entropy increase kJ/(kg·K) — for visualization only."""
    T_vals = [s.T for s in stations_data]
    P_vals = [s.P for s in stations_data]
    s_vals = [0.0]
    R = 0.287
    for i in range(1, len(T_vals)):
        ds = cp * np.log(T_vals[i] / T_vals[i - 1]) - R * np.log(P_vals[i] / P_vals[i - 1])
        s_vals.append(s_vals[-1] + ds)
    return s_vals


def plot_ts_diagram(results_list: List[EngineResults]) -> plt.Figure:
    """T-s diagram for multiple flight phases."""
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_xlabel('Specifikus entrópia [kJ/(kg·K)]', fontsize=12)
    ax.set_ylabel('Hőmérséklet [K]', fontsize=12)
    ax.set_title('CFM56-5B T-s diagram (Brayton-ciklus)', fontsize=13, fontweight='bold')
    ax.grid(alpha=0.3)

    for idx, result in enumerate(results_list):
        stations = [result.stations[s] for s in _STATION_ORDER if s in result.stations]
        if len(stations) < 3:
            continue
        T_vals = [s.T for s in stations]
        s_vals = _entropy_approx(stations)
        color = _COLORS[idx % len(_COLORS)]
        ax.plot(s_vals, T_vals, '-o', color=color, linewidth=2, markersize=5,
                label=f'{result.flight_phase} | Mach {result.mach} | {result.altitude_ft} ft')
        for i, (sv, tv, station) in enumerate(zip(s_vals, T_vals, stations)):
            if i in (0, 3, 4, 7):
                ax.annotate(station.station.replace('_', '\n'),
                            xy=(sv, tv), xytext=(sv + 0.01, tv + 20),
                            fontsize=7, color=color)

    ax.legend(loc='upper left', fontsize=9)
    plt.tight_layout()
    return fig
