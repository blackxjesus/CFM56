# scripts/run_design.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib
matplotlib.use('Agg')

from engine import run_design_point
from visualization import plot_station_diagram, plot_3d_model

if __name__ == '__main__':
    print("CFM56-5B Design Point szimuláció — Felszállás")
    print("=" * 50)

    result = run_design_point(flight_phase='takeoff', altitude_ft=0, mach=0.25)
    result.summary()

    print("\nÁllomás adatok:")
    print(result.to_dataframe().to_string(index=False))

    fig2d = plot_station_diagram(result)
    fig2d.savefig('design_point_stations.png', dpi=150, bbox_inches='tight')
    print("\n2D diagram mentve: design_point_stations.png")

    fig3d = plot_3d_model(result)
    fig3d.write_html('cfm56_3d.html')
    print("3D modell mentve: cfm56_3d.html")
