"""
CFM56-5B thermodynamic model using pyCycle.

Implements a two-spool high-bypass turbofan cycle representing the
CFM56-5B engine used on the Airbus A320 family. Structure follows the
pyCycle ``high_bypass_turbofan`` example (Hendricks & Gray, 2019).
"""

import openmdao.api as om
import pycycle.api as pyc

# CFM56-5B approximate design parameters
CFM56_PARAMS = {
    'bpr': 5.5,
    'opr': 27.0,
    'T4_design': 1700.0,      # K
    'max_thrust_kN': 133.4,
    'mass_flow': 370.0,        # kg/s
    'fan_PR': 1.685,
    'lpc_PR': 2.0,
    'hpc_PR': 8.0,             # fan*lpc*hpc ≈ 27
    'fan_eff': 0.89,
    'lpc_eff': 0.89,
    'hpc_eff': 0.87,
    'hpt_eff': 0.89,
    'lpt_eff': 0.90,
    'inlet_MN': 0.60,
    'fan_MN': 0.45,
    'hpc_MN': 0.20,
    'burner_dPqP': 0.03,
    'core_nozz_Cv': 0.9999,
    'byp_nozz_Cv': 0.9975,
}


# 100 % reference speeds and maximum rotor speeds, EASA TCDS E.003 Issue 06,
# IV.2.1: N1 5200 rpm (104 %), N2 15183 rpm (105 %) for all CFM56-5B models.
N1_100_RPM = 5000.0
N2_100_RPM = 14460.0
N1_REDLINE_PCT = 104.0
N2_REDLINE_PCT = 105.0
MAP_RLINE_RANGE = (1.0, 3.0)   # R-line span of the LPC/HPC maps (AXI5 fan: 1.0-2.6)

# Engine is sized at sea-level static take-off (MN 0.001 avoids the MN=0
# singularity in the flight-condition solver, as in the pyCycle examples).
DESIGN_ALT_FT = 0.0
DESIGN_MN = 0.001


# VBV schedule: closed at high power, opening linearly as T4 drops, so the
# booster operating point stays away from the surge line. On the real engine
# the FADEC schedules VBV from corrected N2; here T4 stands in for it.
VBV_CLOSED_T4 = 1650.0   # K
VBV_FULL_T4 = 1000.0     # K
VBV_MAX_FRAC = 0.30      # fraction of booster flow bled


def vbv_schedule(T4: float) -> float:
    """Bleed fraction of LPC exit flow for a given T4 [K]."""
    x = (VBV_CLOSED_T4 - T4) / (VBV_CLOSED_T4 - VBV_FULL_T4)
    return VBV_MAX_FRAC * min(1.0, max(0.0, x))


class CFM56Cycle(pyc.Cycle):
    """
    Two-spool high-bypass turbofan cycle for the CFM56-5B.

    Station layout:
        FlightConditions -> Inlet -> Fan -> Splitter
            Core path: LPC -> HPC -> Burner -> HPT -> LPT -> CoreNozzle
            Bypass path: BypassNozzle
        Performance

    Implicit balances (design mode):
        FAR     -> burner exit Tt equals ``T4_target``
        hpt_PR  -> HP shaft net power is zero (HPT drives HPC)
        lpt_PR  -> LP shaft net power is zero (LPT drives fan + LPC)
    """

    def initialize(self):
        self.options.declare('design', default=True)
        super().initialize()

    def setup(self):
        p = CFM56_PARAMS
        design = self.options['design']

        self.add_subsystem('fc', pyc.FlightConditions())
        self.add_subsystem('inlet', pyc.Inlet())
        self.add_subsystem('fan', pyc.Compressor(map_data=pyc.AXI5, map_extrap=True),
                           promotes_inputs=[('Nmech', 'LP_Nmech')])
        self.add_subsystem('splitter', pyc.Splitter())
        self.add_subsystem('lpc', pyc.Compressor(map_data=pyc.LPCMap, map_extrap=True),
                           promotes_inputs=[('Nmech', 'LP_Nmech')])
        # Variable bleed valves (VBV): booster exit bleed, open at part power
        self.add_subsystem('vbv', pyc.BleedOut(bleed_names=['vbv']))
        self.add_subsystem('hpc', pyc.Compressor(map_data=pyc.HPCMap, map_extrap=True),
                           promotes_inputs=[('Nmech', 'HP_Nmech')])
        self.add_subsystem('burner', pyc.Combustor(fuel_type='Jet-A(g)'))
        self.add_subsystem('hpt', pyc.Turbine(map_data=pyc.HPTMap, map_extrap=True),
                           promotes_inputs=[('Nmech', 'HP_Nmech')])
        self.add_subsystem('lpt', pyc.Turbine(map_data=pyc.LPTMap, map_extrap=True),
                           promotes_inputs=[('Nmech', 'LP_Nmech')])
        self.add_subsystem('core_nozz', pyc.Nozzle(nozzType='CV', lossCoef='Cv'))
        self.add_subsystem('byp_nozz', pyc.Nozzle(nozzType='CV', lossCoef='Cv'))
        self.add_subsystem('lp_shaft', pyc.Shaft(num_ports=3),  # fan + lpc + lpt
                           promotes_inputs=[('Nmech', 'LP_Nmech')])
        self.add_subsystem('hp_shaft', pyc.Shaft(num_ports=2),  # hpc + hpt
                           promotes_inputs=[('Nmech', 'HP_Nmech')])
        self.add_subsystem('perf', pyc.Performance(num_nozzles=2, num_burners=1))

        # Shaft torque connections
        self.connect('fan.trq', 'lp_shaft.trq_0')
        self.connect('lpc.trq', 'lp_shaft.trq_1')
        self.connect('lpt.trq', 'lp_shaft.trq_2')
        self.connect('hpc.trq', 'hp_shaft.trq_0')
        self.connect('hpt.trq', 'hp_shaft.trq_1')

        # Performance connections
        self.connect('inlet.Fl_O:tot:P', 'perf.Pt2')
        self.connect('hpc.Fl_O:tot:P', 'perf.Pt3')
        self.connect('burner.Wfuel', 'perf.Wfuel_0')
        self.connect('inlet.F_ram', 'perf.ram_drag')
        self.connect('core_nozz.Fg', 'perf.Fg_0')
        self.connect('byp_nozz.Fg', 'perf.Fg_1')

        # Nozzles expand to the ambient static pressure
        self.connect('fc.Fl_O:stat:P', 'core_nozz.Ps_exhaust')
        self.connect('fc.Fl_O:stat:P', 'byp_nozz.Ps_exhaust')

        balance = self.add_subsystem('balance', om.BalanceComp())
        if design:
            # FAR -> Tt4 target (throttle is set as turbine inlet temperature)
            balance.add_balance('FAR', eq_units='degR', lower=1e-4, upper=0.06, val=0.027)
            self.connect('balance.FAR', 'burner.Fl_I:FAR')
            self.connect('burner.Fl_O:tot:T', 'balance.lhs:FAR')
            self.promotes('balance', inputs=[('rhs:FAR', 'T4_target')])

            # Turbine PRs -> zero net shaft power (mult -1: pwr_in == pwr_out)
            balance.add_balance('lpt_PR', val=4.0, lower=1.001, upper=12.0,
                                eq_units='hp', use_mult=True, mult_val=-1)
            self.connect('balance.lpt_PR', 'lpt.PR')
            self.connect('lp_shaft.pwr_in_real', 'balance.lhs:lpt_PR')
            self.connect('lp_shaft.pwr_out_real', 'balance.rhs:lpt_PR')

            balance.add_balance('hpt_PR', val=3.0, lower=1.001, upper=12.0,
                                eq_units='hp', use_mult=True, mult_val=-1)
            self.connect('balance.hpt_PR', 'hpt.PR')
            self.connect('hp_shaft.pwr_in_real', 'balance.lhs:hpt_PR')
            self.connect('hp_shaft.pwr_out_real', 'balance.rhs:hpt_PR')

        else:
            # Off-design: geometry (nozzle areas, map scalars) frozen at design.
            # FAR -> Tt4 target (throttle)
            balance.add_balance('FAR', eq_units='degR', lower=1e-4, upper=0.06, val=0.02)
            self.connect('balance.FAR', 'burner.Fl_I:FAR')
            self.connect('burner.Fl_O:tot:T', 'balance.lhs:FAR')
            self.promotes('balance', inputs=[('rhs:FAR', 'T4_target')])

            # W -> core nozzle throat area equals design area
            balance.add_balance('W', units='lbm/s', lower=10., upper=2000., eq_units='inch**2')
            self.connect('balance.W', 'fc.W')
            self.connect('core_nozz.Throat:stat:area', 'balance.lhs:W')

            # BPR -> bypass nozzle throat area equals design area
            balance.add_balance('BPR', lower=1., upper=15., eq_units='inch**2')
            self.connect('balance.BPR', 'splitter.BPR')
            self.connect('byp_nozz.Throat:stat:area', 'balance.lhs:BPR')

            # Spool speeds -> zero net shaft power
            balance.add_balance('lp_Nmech', val=5000., units='rpm', lower=300., eq_units='hp',
                                use_mult=True, mult_val=-1)
            self.connect('balance.lp_Nmech', 'LP_Nmech')
            self.connect('lp_shaft.pwr_in_real', 'balance.lhs:lp_Nmech')
            self.connect('lp_shaft.pwr_out_real', 'balance.rhs:lp_Nmech')

            balance.add_balance('hp_Nmech', val=14460., units='rpm', lower=1000., eq_units='hp',
                                use_mult=True, mult_val=-1)
            self.connect('balance.hp_Nmech', 'HP_Nmech')
            self.connect('hp_shaft.pwr_in_real', 'balance.lhs:hp_Nmech')
            self.connect('hp_shaft.pwr_out_real', 'balance.rhs:hp_Nmech')

        # Flow connections
        self.pyc_connect_flow('fc.Fl_O', 'inlet.Fl_I')
        self.pyc_connect_flow('inlet.Fl_O', 'fan.Fl_I')
        self.pyc_connect_flow('fan.Fl_O', 'splitter.Fl_I')
        self.pyc_connect_flow('splitter.Fl_O1', 'lpc.Fl_I')
        self.pyc_connect_flow('lpc.Fl_O', 'vbv.Fl_I')
        self.pyc_connect_flow('vbv.Fl_O', 'hpc.Fl_I')
        self.pyc_connect_flow('hpc.Fl_O', 'burner.Fl_I')
        self.pyc_connect_flow('burner.Fl_O', 'hpt.Fl_I')
        self.pyc_connect_flow('hpt.Fl_O', 'lpt.Fl_I')
        self.pyc_connect_flow('lpt.Fl_O', 'core_nozz.Fl_I')
        self.pyc_connect_flow('splitter.Fl_O2', 'byp_nozz.Fl_I')

        # Nozzle loss coefficients
        self.set_input_defaults('core_nozz.Cv', p['core_nozz_Cv'])
        self.set_input_defaults('byp_nozz.Cv', p['byp_nozz_Cv'])

        if design:
            self.set_input_defaults('fc.alt', 0.0, units='ft')
            self.set_input_defaults('fc.MN', 0.0)
            self.set_input_defaults('fc.W', p['mass_flow'], units='kg/s')
            self.set_input_defaults('T4_target', p['T4_design'], units='K')
            self.set_input_defaults('inlet.MN', p['inlet_MN'])
            self.set_input_defaults('fan.PR', p['fan_PR'])
            self.set_input_defaults('fan.eff', p['fan_eff'])
            self.set_input_defaults('fan.MN', p['fan_MN'])
            self.set_input_defaults('splitter.BPR', p['bpr'])
            self.set_input_defaults('splitter.MN1', 0.3)
            self.set_input_defaults('splitter.MN2', 0.45)
            self.set_input_defaults('lpc.PR', p['lpc_PR'])
            self.set_input_defaults('lpc.eff', p['lpc_eff'])
            self.set_input_defaults('lpc.MN', 0.3)
            self.set_input_defaults('vbv.MN', 0.3)
            self.set_input_defaults('vbv.vbv:frac_W', 0.0)
            self.set_input_defaults('hpc.PR', p['hpc_PR'])
            self.set_input_defaults('hpc.eff', p['hpc_eff'])
            self.set_input_defaults('hpc.MN', p['hpc_MN'])
            self.set_input_defaults('burner.MN', 0.1)
            self.set_input_defaults('burner.dPqP', p['burner_dPqP'])
            self.set_input_defaults('hpt.eff', p['hpt_eff'])
            self.set_input_defaults('hpt.MN', 0.3)
            self.set_input_defaults('lpt.eff', p['lpt_eff'])
            self.set_input_defaults('lpt.MN', 0.4)
            # 100 % N1 / N2 reference speeds (EASA TCDS E.003)
            self.set_input_defaults('LP_Nmech', N1_100_RPM, units='rpm')
            self.set_input_defaults('HP_Nmech', N2_100_RPM, units='rpm')

        # Solver (as in the pyCycle HBTF example)
        newton = self.nonlinear_solver = om.NewtonSolver()
        newton.options['atol'] = 1e-8
        newton.options['rtol'] = 1e-99
        newton.options['iprint'] = -1
        newton.options['maxiter'] = 50
        newton.options['solve_subsystems'] = True
        newton.options['max_sub_solves'] = 1000
        newton.options['reraise_child_analysiserror'] = False
        ls = newton.linesearch = om.ArmijoGoldsteinLS()
        ls.options['maxiter'] = 3
        ls.options['rho'] = 0.75
        self.linear_solver = om.DirectSolver()

        super().setup()


def _set_design_guesses(prob):
    prob['balance.FAR'] = 0.027
    prob['balance.hpt_PR'] = 3.0
    prob['balance.lpt_PR'] = 4.0


def build_design_model() -> om.Problem:
    """Build and set up an OpenMDAO Problem for CFM56-5B design-point analysis."""
    prob = om.Problem(reports=False)
    prob.model = CFM56Cycle(design=True, thermo_method='CEA')
    prob.setup(check=False)
    prob.set_solver_print(level=-1)
    _set_design_guesses(prob)
    return prob


class CFM56MultiPoint(pyc.MPCycle):
    """Design point (SLS take-off) + one off-design point 'OD'.

    The design point fixes nozzle throat areas and component map scalars;
    the OD point then finds mass flow, BPR and spool speeds from those.
    """

    def setup(self):
        p = CFM56_PARAMS
        self.pyc_add_pnt('DESIGN', CFM56Cycle(design=True, thermo_method='CEA'))
        self.pyc_add_pnt('OD', CFM56Cycle(design=False, thermo_method='CEA'))

        self.pyc_add_cycle_param('burner.dPqP', p['burner_dPqP'])
        self.pyc_add_cycle_param('core_nozz.Cv', p['core_nozz_Cv'])
        self.pyc_add_cycle_param('byp_nozz.Cv', p['byp_nozz_Cv'])

        self.set_input_defaults('OD.fc.alt', DESIGN_ALT_FT, units='ft')
        self.set_input_defaults('OD.fc.MN', DESIGN_MN)
        self.set_input_defaults('OD.T4_target', p['T4_design'], units='K')

        self.pyc_use_default_des_od_conns()
        self.pyc_connect_des_od('core_nozz.Throat:stat:area', 'balance.rhs:W')
        self.pyc_connect_des_od('byp_nozz.Throat:stat:area', 'balance.rhs:BPR')

        super().setup()


def set_offdesign_guesses(prob, point='OD'):
    """Initial guesses near the design solution (used before the first solve)."""
    p = CFM56_PARAMS
    prob[f'{point}.balance.FAR'] = 0.027
    prob[f'{point}.balance.W'] = p['mass_flow'] * 2.20462
    prob[f'{point}.balance.BPR'] = p['bpr']
    prob[f'{point}.balance.lp_Nmech'] = N1_100_RPM
    prob[f'{point}.balance.hp_Nmech'] = N2_100_RPM
    prob[f'{point}.hpt.PR'] = 2.7
    prob[f'{point}.lpt.PR'] = 3.7
    for comp in ('fan', 'lpc', 'hpc'):
        prob[f'{point}.{comp}.map.RlineMap'] = 2.0


def build_offdesign_model() -> om.Problem:
    """Build a design + off-design multipoint Problem for the CFM56-5B."""
    prob = om.Problem(reports=False)
    prob.model = CFM56MultiPoint()
    prob.setup(check=False)
    prob.set_solver_print(level=-1)
    prob.set_val('DESIGN.fc.alt', DESIGN_ALT_FT, units='ft')
    prob.set_val('DESIGN.fc.MN', DESIGN_MN)
    prob['DESIGN.balance.FAR'] = 0.027
    prob['DESIGN.balance.hpt_PR'] = 2.7
    prob['DESIGN.balance.lpt_PR'] = 3.7
    set_offdesign_guesses(prob)
    return prob
