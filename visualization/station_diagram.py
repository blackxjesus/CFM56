# visualization/station_diagram.py
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from engine.results import EngineResults

_STATION_LABELS = {
    'inlet_in':      'Inlet\n(St. 2)',
    'fan_exit':      'Fan\nkimenet',
    'lpc_exit':      'LPC\nkimenet',
    'hpc_exit':      'HPC\nkimenet',
    'burner_exit':   'Égőtér\nkimenet',
    'hpt_exit':      'HPT\nkimenet',
    'lpt_exit':      'LPT\nkimenet',
    'core_nozz':     'Core\nfúvócső',
    'S0_freestream': 'Szabad\nlevegő',
    'S2_inlet_exit': 'Inlet\n(St. 2)',
    'S21_fan_exit':  'Fan\nkimenet',
    'S25_lpc_exit':  'LPC\nkimenet',
    'S3_hpc_exit':   'HPC\nkimenet',
    'S4_burner_exit':'Égőtér\nkimenet',
    'S45_hpt_exit':  'HPT\nkimenet',
    'S5_lpt_exit':   'LPT\nkimenet',
    'S8_core_nozz':  'Core\nfúvócső',
    'S18_byp_nozz':  'Bypass\nfúvócső',
}

# Preferált sorrend — ha nincs egyezés, az összes állomást vesszük
_PREFERRED_ORDER = [
    'S0_freestream', 'S2_inlet_exit', 'S21_fan_exit', 'S25_lpc_exit',
    'S3_hpc_exit', 'S4_burner_exit', 'S45_hpt_exit', 'S5_lpt_exit', 'S8_core_nozz',
    'inlet_in', 'fan_exit', 'lpc_exit', 'hpc_exit',
    'burner_exit', 'hpt_exit', 'lpt_exit', 'core_nozz',
]


def plot_station_diagram(results: EngineResults) -> plt.Figure:
    """2D állomás-diagram T és P értékekkel minden állomáson."""
    # Használjuk a preferált sorrendet, ha van egyezés — különben az összes állomást
    ordered = [s for s in _PREFERRED_ORDER if s in results.stations]
    if not ordered:
        ordered = list(results.stations.keys())
    stations = ordered
    T_vals = [results.stations[s].T for s in stations]
    P_vals = [results.stations[s].P for s in stations]
    labels = [_STATION_LABELS.get(s, s.replace('_', '\n')) for s in stations]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8))
    fig.suptitle(
        f'CFM56-5B Állomás-diagram — {results.flight_phase.upper()}\n'
        f'Alt: {results.altitude_ft} ft | Mach: {results.mach} | '
        f'Tolóerő: {results.thrust_kN:.1f} kN | OPR: {results.opr:.1f}',
        fontsize=13, fontweight='bold'
    )

    cmap = plt.cm.RdYlBu_r
    norm = plt.Normalize(min(T_vals), max(T_vals))
    colors = [cmap(norm(T)) for T in T_vals]
    x = np.arange(len(stations))

    bars1 = ax1.bar(x, T_vals, color=colors, edgecolor='black', linewidth=0.8)
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=9)
    ax1.set_ylabel('Hőmérséklet [K]', fontsize=11)
    ax1.set_title('Teljes hőmérséklet (Tt) az állomások mentén', fontsize=11)
    ax1.grid(axis='y', alpha=0.4)
    for bar, T in zip(bars1, T_vals):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 10,
                 f'{T:.0f} K', ha='center', va='bottom', fontsize=8)

    bars2 = ax2.bar(x, P_vals, color='steelblue', edgecolor='black', linewidth=0.8)
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=9)
    ax2.set_ylabel('Nyomás [kPa]', fontsize=11)
    ax2.set_title('Teljes nyomás (Pt) az állomások mentén', fontsize=11)
    ax2.grid(axis='y', alpha=0.4)
    for bar, P in zip(bars2, P_vals):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 10,
                 f'{P:.0f} kPa', ha='center', va='bottom', fontsize=8)

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    fig.colorbar(sm, ax=ax1, label='Hőmérséklet [K]', shrink=0.8)
    plt.tight_layout(rect=[0, 0, 1, 0.93])
    return fig
