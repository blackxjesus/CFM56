"""
Pre-compute simulation results for all flight phase + throttle combinations.
Saves to data/lookup.pkl so the Streamlit app loads instantly.
"""
import sys, os, pickle
sys.path.insert(0, os.path.dirname(__file__))

from engine import run_design_point

FLIGHT_PHASES = {
    'Takeoff   (0 ft, Mach 0.25)':        {'altitude_ft': 0,     'mach': 0.25, 'key': 'takeoff'},
    'Climb     (15 000 ft, Mach 0.50)':   {'altitude_ft': 15000, 'mach': 0.50, 'key': 'climb'},
    'Cruise    (35 000 ft, Mach 0.78)':   {'altitude_ft': 35000, 'mach': 0.78, 'key': 'cruise'},
}
THROTTLE_STEPS = list(range(0, 105, 5))  # 0, 5, 10, ... 100

os.makedirs('data', exist_ok=True)
lookup = {}
total = len(FLIGHT_PHASES) * len(THROTTLE_STEPS)
n = 0

for phase_label, fp in FLIGHT_PHASES.items():
    for thr in THROTTLE_STEPS:
        T4 = 1000.0 + thr * 7.0
        n += 1
        print(f"[{n}/{total}] {fp['key']} throttle={thr}% T4={T4:.0f}K")
        r = run_design_point(fp['key'], fp['altitude_ft'], fp['mach'], T4_override=T4)
        lookup[(phase_label, thr)] = r

with open('data/lookup.pkl', 'wb') as f:
    pickle.dump(lookup, f)

print(f"\nDone — {total} results saved to data/lookup.pkl")
