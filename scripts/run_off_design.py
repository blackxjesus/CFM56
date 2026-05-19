# scripts/run_off_design.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib
matplotlib.use('Agg')

import pandas as pd
from engine import run_off_design
from visualization import plot_ts_diagram, plot_station_diagram

PHASES = [
    {'flight_phase': 'takeoff', 'altitude_ft': 0,      'mach': 0.25},
    {'flight_phase': 'climb',   'altitude_ft': 10000,  'mach': 0.50},
    {'flight_phase': 'cruise',  'altitude_ft': 35000,  'mach': 0.82},
]

if __name__ == '__main__':
    print("CFM56-5B Off-Design analízis — 3 repülési fázis")
    print("=" * 50)

    results = run_off_design(PHASES)

    for r in results:
        r.summary()
        print()

    summary = pd.DataFrame([{
        'Fázis':       r.flight_phase,
        'Magasság ft': r.altitude_ft,
        'Mach':        r.mach,
        'Tolóerő kN':  round(r.thrust_kN, 1),
        'SFC':         round(r.sfc, 5),
        'OPR':         round(r.opr, 2),
        'BPR':         round(r.bpr, 2),
    } for r in results])
    print("\nÖsszefoglaló táblázat:")
    print(summary.to_string(index=False))

    fig_ts = plot_ts_diagram(results)
    fig_ts.savefig('off_design_ts.png', dpi=150, bbox_inches='tight')
    print("\nT-s diagram mentve: off_design_ts.png")

    for r in results:
        fig = plot_station_diagram(r)
        fname = f'stations_{r.flight_phase}.png'
        fig.savefig(fname, dpi=150, bbox_inches='tight')
        print(f"Állomás-diagram mentve: {fname}")
