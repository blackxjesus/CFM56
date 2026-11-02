# engine/fuel.py
"""Fuel on board (FOB) for the E/WD.

FOB falls by the fuel flow shown on the E/WD, integrated over simulated time:
    dFOB = FF * dt_sim,   FF = SFC * F_N on a running engine.
dt_sim follows the SPEED setting (one wall-clock tick = SPEED * tick seconds),
so a faster playback burns fuel faster in wall-clock time. No Streamlit here.
"""

FOB_INITIAL_KG = 12000.0


def burn_fuel(fob_kg, ff_kg_h, dt_s):
    """FOB after `dt_s` simulated seconds at fuel flow `ff_kg_h` [kg/h]. Never below 0."""
    used = max(0.0, ff_kg_h) * max(0.0, dt_s) / 3600.0
    return max(0.0, fob_kg - used)
