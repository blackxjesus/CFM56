"""
CFM56-5B simulation wrapper.

Provides run_design_point() and run_off_design() using the pyCycle model
defined in engine/cfm56.py. All outputs are converted to SI/metric units.
"""

import contextlib
import math
import os
import warnings
from typing import List

from engine.cfm56 import (build_design_model, CFM56_PARAMS, vbv_schedule, N1_100_RPM,
                          N2_100_RPM, N1_REDLINE_PCT, N2_REDLINE_PCT, MAP_RLINE_RANGE)
from engine.results import EngineResults, StationData

STATION_MAP = {
    'S0_freestream': 'fc.Fl_O',
    'S2_inlet_exit': 'inlet.Fl_O',
    'S21_fan_exit':  'fan.Fl_O',
    'S25_lpc_exit':  'lpc.Fl_O',
    'S3_hpc_exit':   'hpc.Fl_O',
    'S4_burner_exit': 'burner.Fl_O',
    'S45_hpt_exit':  'hpt.Fl_O',
    'S5_lpt_exit':   'lpt.Fl_O',
    'S8_core_nozz':  'core_nozz.Fl_O',
    'S18_byp_nozz':  'byp_nozz.Fl_O',
}


def check_converged(prob, T4_target, prefix=''):
    """Raise if the cycle balances are not satisfied or the core nozzle is dead.

    Newton does not raise on non-convergence (reraise_child_analysiserror is
    False), so a silently unconverged point would otherwise be reported.
    """
    def val(name, units=None):
        return float(prob.get_val(prefix + name, units=units)[0])

    problems = []
    if abs(val('burner.Fl_O:tot:T', 'K') - T4_target) > 1.0:
        problems.append('T4 target not reached')
    for shaft, comp in (('hp_shaft', 'hpc'), ('lp_shaft', 'fan')):
        if abs(val(f'{shaft}.pwr_net', 'kW')) > 1e-3 * abs(val(f'{comp}.power', 'kW')):
            problems.append(f'{shaft} power not balanced')
    if val('core_nozz.Fl_O:tot:P', 'kPa') <= val('fc.Fl_O:stat:P', 'kPa'):
        problems.append('core nozzle total pressure below ambient (no core thrust)')
    if problems:
        raise RuntimeError(f'Unphysical/unconverged cycle point (T4={T4_target} K): '
                           + '; '.join(problems))


def validity_notes(prob, prefix='') -> List[str]:
    """Why a converged point is not physically trustworthy (empty list = valid)."""
    def val(name, units=None):
        return float(prob.get_val(prefix + name, units=units)[0])

    notes = []
    for comp, (lo, hi) in (('fan', (1.0, 2.6)), ('lpc', MAP_RLINE_RANGE), ('hpc', MAP_RLINE_RANGE)):
        rline = val(f'{comp}.map.RlineMap')
        if not lo <= rline <= hi:
            notes.append(f'{comp.upper()} off map (R-line {rline:.2f})')
    n1 = 100.0 * val('LP_Nmech', 'rpm') / N1_100_RPM
    n2 = 100.0 * val('HP_Nmech', 'rpm') / N2_100_RPM
    if n1 > N1_REDLINE_PCT:
        notes.append(f'N1 {n1:.1f}% above {N1_REDLINE_PCT:.0f}% limit')
    if n2 > N2_REDLINE_PCT:
        notes.append(f'N2 {n2:.1f}% above {N2_REDLINE_PCT:.0f}% limit')
    return notes


def extract_results(prob, flight_phase, altitude_ft, mach, prefix='') -> EngineResults:
    """Read a solved cycle point (optionally inside a multipoint model)."""
    def val(name, units=None):
        return float(prob.get_val(prefix + name, units=units)[0])

    thrust_kN = val('perf.Fn', 'kN')
    fuel_flow = val('perf.Wfuel', 'kg/s')

    stations = {}
    for label, path in STATION_MAP.items():
        stations[label] = StationData(
            station=label,
            T=val(f'{path}:tot:T', 'K'),
            P=val(f'{path}:tot:P', 'kPa'),
            h=val(f'{path}:tot:h', 'kJ/kg'),
        )

    return EngineResults(
        flight_phase=flight_phase,
        altitude_ft=altitude_ft,
        mach=mach,
        thrust_kN=thrust_kN,
        sfc=fuel_flow / thrust_kN if thrust_kN > 0 else 0.0,
        opr=val('perf.OPR'),
        bpr=val('splitter.BPR'),
        fuel_flow=fuel_flow,
        mass_flow=val('inlet.Fl_O:stat:W', 'kg/s'),
        T4=val('burner.Fl_O:tot:T', 'K'),
        far=val('burner.Fl_I:FAR'),
        hpt_PR=val('hpt.PR'),
        lpt_PR=val('lpt.PR'),
        gross_thrust_kN=val('perf.Fg', 'kN'),
        ram_drag_kN=val('inlet.F_ram', 'kN'),
        LP_Nmech=val('LP_Nmech', 'rpm'),
        HP_Nmech=val('HP_Nmech', 'rpm'),
        N1=100.0 * val('LP_Nmech', 'rpm') / N1_100_RPM,
        N2=100.0 * val('HP_Nmech', 'rpm') / N2_100_RPM,
        vbv_frac=val('vbv.vbv:frac_W'),
        lpc_rline=val('lpc.map.RlineMap'),
        validity=validity_notes(prob, prefix) if prefix == 'OD.' else [],
        fan_eff=val('fan.eff'), lpc_eff=val('lpc.eff'), hpc_eff=val('hpc.eff'),
        hpt_eff=val('hpt.eff'), lpt_eff=val('lpt.eff'),
        stations=stations,
    )


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
        Turbine inlet temperature target in K. If None, uses
        CFM56_PARAMS['T4_design']. The FAR balance drives the burner exit
        temperature to exactly this value.

    Returns
    -------
    EngineResults
        Solved engine results with station data and performance metrics.
    """
    prob = build_design_model()
    prob.set_val('fc.alt', altitude_ft, units='ft')
    prob.set_val('fc.MN', mach)
    T4 = CFM56_PARAMS['T4_design'] if T4_override is None else T4_override
    prob.set_val('T4_target', T4, units='K')

    prob.run_model()
    check_converged(prob, T4)
    return extract_results(prob, flight_phase, altitude_ft, mach)


class OffDesignSolver:
    """Off-design CFM56-5B cycle (geometry frozen at the SLS design point).

    Newton converges only from a nearby starting point, so every request is
    reached by continuation: altitude, Mach and T4 are walked from the last
    converged state in small steps.
    """

    MAX_STEP = {'alt': 2500.0, 'mach': 0.05, 'T4': 50.0}
    RETRIES = 4

    def __init__(self):
        from engine.cfm56 import build_offdesign_model, DESIGN_ALT_FT, DESIGN_MN
        self.prob = build_offdesign_model()
        self.state = {'alt': DESIGN_ALT_FT, 'mach': DESIGN_MN,
                      'T4': CFM56_PARAMS['T4_design']}
        self._solve(**self.state)

    def _run_quiet(self):
        with open(os.devnull, 'w') as null, \
                contextlib.redirect_stdout(null), contextlib.redirect_stderr(null), \
                warnings.catch_warnings():
            warnings.simplefilter('ignore')
            self.prob.run_model()

    def _solve(self, alt, mach, T4):
        self.prob.set_val('OD.fc.alt', alt, units='ft')
        self.prob.set_val('OD.fc.MN', mach)
        self.prob.set_val('OD.T4_target', T4, units='K')
        self.prob.set_val('OD.vbv.vbv:frac_W', vbv_schedule(T4))
        for _ in range(self.RETRIES):
            self._run_quiet()
            try:
                check_converged(self.prob, T4, prefix='OD.')
                return
            except RuntimeError as err:
                last = err
        raise last

    def solve(self, altitude_ft: float, mach: float, T4: float, flight_phase: str = ''):
        start = dict(self.state)
        target = {'alt': altitude_ft, 'mach': mach, 'T4': T4}
        n = max(1, max(math.ceil(abs(target[k] - start[k]) / self.MAX_STEP[k])
                       for k in target))
        for i in range(1, n + 1):
            f = i / n
            step = {k: start[k] + f * (target[k] - start[k]) for k in target}
            self._solve(**step)
            self.state = step
        return extract_results(self.prob, flight_phase, altitude_ft, mach, prefix='OD.')

    def design_results(self) -> EngineResults:
        from engine.cfm56 import DESIGN_ALT_FT, DESIGN_MN
        return extract_results(self.prob, 'design (SLS)', DESIGN_ALT_FT, DESIGN_MN,
                               prefix='DESIGN.')


def run_off_design(flight_phases: List[dict]) -> List[EngineResults]:
    """True off-design analysis for each of the given flight phases.

    Each entry in *flight_phases* must be a dict with keys ``flight_phase``,
    ``altitude_ft``, ``mach`` and optionally ``T4`` (K, default T4_design).
    The engine geometry is sized once at sea-level static take-off; mass
    flow, BPR, OPR and spool speeds then follow from the component maps.
    """
    solver = OffDesignSolver()
    return [solver.solve(ph['altitude_ft'], ph['mach'],
                         ph.get('T4', CFM56_PARAMS['T4_design']), ph['flight_phase'])
            for ph in flight_phases]
