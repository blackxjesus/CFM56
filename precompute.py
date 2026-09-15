"""
Pre-compute simulation results for all flight phase + throttle combinations.
Saves to data/lookup.pkl so the Streamlit app loads instantly, and writes
data/results.csv for the thesis tables.

The engine is sized once at sea-level static take-off; every phase/throttle
point is a true off-design solution of that engine (engine.simulation.OffDesignSolver).
"""
import sys, os, csv, pickle, time
sys.path.insert(0, os.path.dirname(__file__))

from engine.simulation import OffDesignSolver

FLIGHT_PHASES = {
    'Takeoff   (0 ft, Mach 0.25)':        {'altitude_ft': 0,     'mach': 0.25, 'key': 'takeoff'},
    'Climb     (15 000 ft, Mach 0.50)':   {'altitude_ft': 15000, 'mach': 0.50, 'key': 'climb'},
    'Cruise    (35 000 ft, Mach 0.78)':   {'altitude_ft': 35000, 'mach': 0.78, 'key': 'cruise'},
}
THROTTLE_STEPS = list(range(100, -5, -5))  # 100, 95, ... 0 (continuation from full power)


def throttle_to_T4(throttle):
    return 1000.0 + throttle * 7.0


os.makedirs('data', exist_ok=True)
lookup = {}
rows = []
solver = OffDesignSolver()
design = solver.design_results()
t0 = time.time()

for phase_label, fp in FLIGHT_PHASES.items():
    for thr in THROTTLE_STEPS:
        T4 = throttle_to_T4(thr)
        r = solver.solve(fp['altitude_ft'], fp['mach'], T4, fp['key'])
        lookup[(phase_label, thr)] = r
        rows.append({'phase': fp['key'], 'throttle': thr, 'T4_K': T4,
                     'Fn_kN': r.thrust_kN, 'Fg_kN': r.gross_thrust_kN, 'Fram_kN': r.ram_drag_kN,
                     'W_kgs': r.mass_flow, 'BPR': r.bpr, 'OPR': r.opr,
                     'N1_pct': r.N1, 'N2_pct': r.N2, 'fuel_kgs': r.fuel_flow,
                     'SFC_g_kNs': r.sfc * 1000.0,
                     'EGT_C': r.stations['S5_lpt_exit'].T - 273.15,
                     'VBV': r.vbv_frac, 'LPC_Rline': r.lpc_rline,
                     'valid': not r.validity, 'validity': '; '.join(r.validity)})
        print(f"[{time.time() - t0:5.0f}s] {fp['key']:8s} thr={thr:3d}% T4={T4:.0f}K "
              f"Fn={r.thrust_kN:6.1f} kN N1={r.N1:5.1f}% SFC={r.sfc * 1000:5.2f} g/(kN s)",
              flush=True)
    solver.solve(fp['altitude_ft'], fp['mach'], throttle_to_T4(100))

with open('data/lookup.pkl', 'wb') as f:
    pickle.dump(lookup, f)
with open('data/design_point.pkl', 'wb') as f:
    pickle.dump(design, f)
with open('data/results.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)

print(f"\nDone — {len(lookup)} results saved to data/lookup.pkl, data/results.csv")
