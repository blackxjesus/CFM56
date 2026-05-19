"""
CFM56-5B simulation wrapper.

Provides run_design_point() and run_off_design() using the pyCycle model
defined in engine/cfm56.py. All outputs are converted to SI/metric units.
"""

import numpy as np
from typing import List

from engine.cfm56 import build_design_model, CFM56_PARAMS
from engine.results import EngineResults, StationData

# Unit conversion constants
_LBF_TO_KN = 0.00444822
_LBMS_TO_KGS = 0.453592
_DEGR_TO_K = 5.0 / 9.0        # degR * (5/9) = K
_PSI_TO_KPA = 6.89476          # psi * 6.89476 = kPa
_BTU_LBM_TO_KJ_KG = 2.326     # Btu/lbm * 2.326 = kJ/kg


def run_design_point(flight_phase: str, altitude_ft: float, mach: float,
                     T4_override: float = None) -> EngineResults:
    """Run CFM56-5B design-point simulation.

    Parameters
    ----------
    flight_phase : str
        Label for the flight phase (e.g. 'takeoff', 'cruise').
    altitude_ft : float
        Pressure altitude in feet.
    mach : float
        Flight Mach number.
    T4_override : float, optional
        Turbine inlet temperature in K. If None, uses CFM56_PARAMS['T4_design'].
        Use this to simulate throttle position (e.g. 1000K = idle, 1700K = full).

    Returns
    -------
    EngineResults
        Solved engine results with station data and performance metrics.
    """
    p = CFM56_PARAMS
    prob = build_design_model()

    # Override flight conditions from design defaults
    prob.set_val('fc.alt', altitude_ft, units='ft')
    prob.set_val('fc.MN', mach)

    # Apply throttle (T4 override)
    if T4_override is not None:
        T4_R = T4_override * (9.0 / 5.0)  # K → degR
        prob.set_val('burner.Fl_I:FAR', T4_R / 3060.0 * 0.027)

    prob.run_model()

    # --- Performance scalars ---
    fn_lbf    = float(prob.get_val('perf.Fn', units='lbf')[0])
    wfuel_lbs = float(prob.get_val('perf.Wfuel', units='lbm/s')[0])
    opr       = float(prob.get_val('perf.OPR')[0])

    thrust_kN = fn_lbf * _LBF_TO_KN
    fuel_flow = wfuel_lbs * _LBMS_TO_KGS  # kg/s

    # When T4_override is used the design-point model keeps mass flow fixed.
    # Correct fuel_flow for altitude: scale by inlet (P/√T) ratio relative to
    # the sea-level design point (P0=105.8 kPa, T0=291.8 K).
    if T4_override is not None:
        try:
            P_in_psi = float(prob.get_val('inlet.real_flow.flow.Fl_O:tot:P',
                                          units='lbf/inch**2')[0])
            T_in_R   = float(prob.get_val('inlet.real_flow.flow.Fl_O:tot:T',
                                          units='degR')[0])
            P_design_psi = 15.338   # psi ≈ 105.8 kPa  (sea level, Mach 0.25)
            T_design_R   = 525.2    # degR ≈ 291.8 K
            mass_flow_ratio = (P_in_psi / P_design_psi) * (T_design_R / T_in_R) ** 0.5
            fuel_flow *= mass_flow_ratio
        except Exception:
            pass  # fall back to uncorrected value

    sfc = fuel_flow / thrust_kN if thrust_kN > 0 else 0.0

    # --- Station data (pyCycle outputs are in imperial units) ---
    station_map = {
        'S0_freestream': 'fc.conv.fs.totals.flow.Fl_O',
        'S2_inlet_exit': 'inlet.real_flow.flow.Fl_O',
        'S21_fan_exit':  'fan.real_flow.flow.Fl_O',
        'S25_lpc_exit':  'lpc.real_flow.flow.Fl_O',
        'S3_hpc_exit':   'hpc.real_flow.flow.Fl_O',
        'S4_burner_exit':'burner.vitiated_flow.flow.Fl_O',
        'S45_hpt_exit':  'hpt.real_flow.flow.Fl_O',
        'S5_lpt_exit':   'lpt.real_flow.flow.Fl_O',
        'S8_core_nozz':  'core_nozz.throat_total.flow.Fl_O',
        'S18_byp_nozz':  'byp_nozz.throat_total.flow.Fl_O',
    }

    stations = {}
    for label, path in station_map.items():
        try:
            T_R = float(prob.get_val(f'{path}:tot:T', units='degR')[0])
            P_psi = float(prob.get_val(f'{path}:tot:P', units='lbf/inch**2')[0])
            h_btu = float(prob.get_val(f'{path}:tot:h', units='Btu/lbm')[0])
            stations[label] = StationData(
                station=label,
                T=T_R * _DEGR_TO_K,
                P=P_psi * _PSI_TO_KPA,
                h=h_btu * _BTU_LBM_TO_KJ_KG,
            )
        except Exception:
            pass  # skip stations that failed to converge or have bad paths

    result = EngineResults(
        flight_phase=flight_phase,
        altitude_ft=altitude_ft,
        mach=mach,
        thrust_kN=thrust_kN,
        sfc=sfc,
        opr=opr,
        bpr=p['bpr'],
        fuel_flow=fuel_flow,
        stations=stations,
    )
    return result


def run_off_design(flight_phases: List[dict]) -> List[EngineResults]:
    """Run design-point analysis for each of the given flight phases.

    Each entry in *flight_phases* must be a dict with keys:
    ``flight_phase``, ``altitude_ft``, ``mach``.

    Note: pyCycle design-point models are self-contained, so we simply
    rebuild and solve for each condition independently.
    """
    return [run_design_point(**phase) for phase in flight_phases]
