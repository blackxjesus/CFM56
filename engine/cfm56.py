"""
CFM56-5B thermodynamic model using pyCycle.

Implements a two-spool high-bypass turbofan cycle representing the
CFM56-5B engine used on the Airbus A320 family.
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


class CFM56Cycle(pyc.Cycle):
    """
    Two-spool high-bypass turbofan cycle for the CFM56-5B.

    Station layout:
        FlightConditions -> Inlet -> Fan -> Splitter
            Core path: LPC -> HPC -> Burner -> HPT -> LPT -> CoreNozzle
            Bypass path: BypassNozzle
        Performance
    """

    def initialize(self):
        self.options.declare('design', default=True)
        super().initialize()

    def setup(self):
        p = CFM56_PARAMS
        design = self.options['design']

        self.add_subsystem('fc', pyc.FlightConditions())
        self.add_subsystem('inlet', pyc.Inlet())
        self.add_subsystem('fan', pyc.Compressor(map_data=pyc.AXI5, design=design,
                                                  map_extrap=True))
        self.add_subsystem('splitter', pyc.Splitter())
        self.add_subsystem('lpc', pyc.Compressor(map_data=pyc.LPCMap, design=design,
                                                  map_extrap=True))
        self.add_subsystem('hpc', pyc.Compressor(map_data=pyc.HPCMap, design=design,
                                                  map_extrap=True))
        self.add_subsystem('burner', pyc.Combustor(fuel_type='Jet-A(g)'))
        self.add_subsystem('hpt', pyc.Turbine(map_data=pyc.HPTMap, design=design,
                                               map_extrap=True))
        self.add_subsystem('lpt', pyc.Turbine(map_data=pyc.LPTMap, design=design,
                                               map_extrap=True))
        self.add_subsystem('core_nozz', pyc.Nozzle(nozzType='CV', lossCoef='Cv'))
        self.add_subsystem('byp_nozz', pyc.Nozzle(nozzType='CV', lossCoef='Cv'))
        self.add_subsystem('lp_shaft', pyc.Shaft(num_ports=3))  # fan + lpc + lpt
        self.add_subsystem('hp_shaft', pyc.Shaft(num_ports=2))  # hpc + hpt
        self.add_subsystem('perf', pyc.Performance(num_nozzles=2, num_burners=1))

        # Flow connections
        self.pyc_connect_flow('fc.Fl_O', 'inlet.Fl_I', connect_w=False)
        self.pyc_connect_flow('inlet.Fl_O', 'fan.Fl_I')
        self.pyc_connect_flow('fan.Fl_O', 'splitter.Fl_I')
        self.pyc_connect_flow('splitter.Fl_O1', 'lpc.Fl_I')
        self.pyc_connect_flow('lpc.Fl_O', 'hpc.Fl_I')
        self.pyc_connect_flow('hpc.Fl_O', 'burner.Fl_I')
        self.pyc_connect_flow('burner.Fl_O', 'hpt.Fl_I')
        self.pyc_connect_flow('hpt.Fl_O', 'lpt.Fl_I')
        self.pyc_connect_flow('lpt.Fl_O', 'core_nozz.Fl_I')
        self.pyc_connect_flow('splitter.Fl_O2', 'byp_nozz.Fl_I')

        # Shaft power connections
        self.connect('fan.trq', 'lp_shaft.trq_0')
        self.connect('lpc.trq', 'lp_shaft.trq_1')
        self.connect('lpt.trq', 'lp_shaft.trq_2')
        self.connect('hpc.trq', 'hp_shaft.trq_0')
        self.connect('hpt.trq', 'hp_shaft.trq_1')
        self.connect('lp_shaft.Nmech', 'fan.Nmech')
        self.connect('lp_shaft.Nmech', 'lpc.Nmech')
        self.connect('lp_shaft.Nmech', 'lpt.Nmech')
        self.connect('hp_shaft.Nmech', 'hpc.Nmech')
        self.connect('hp_shaft.Nmech', 'hpt.Nmech')

        # Performance connections
        self.connect('inlet.Fl_O:tot:P', 'perf.Pt2')
        self.connect('hpc.Fl_O:tot:P', 'perf.Pt3')
        self.connect('burner.Wfuel', 'perf.Wfuel_0')
        self.connect('inlet.F_ram', 'perf.ram_drag')
        self.connect('core_nozz.Fg', 'perf.Fg_0')
        self.connect('byp_nozz.Fg', 'perf.Fg_1')

        # Nozzle loss coefficients
        self.set_input_defaults('core_nozz.Cv', p['core_nozz_Cv'])
        self.set_input_defaults('byp_nozz.Cv', p['byp_nozz_Cv'])

        if design:
            # Design point defaults
            self.set_input_defaults('fc.alt', 0.0, units='ft')
            self.set_input_defaults('fc.MN', 0.0)
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
            self.set_input_defaults('hpc.PR', p['hpc_PR'])
            self.set_input_defaults('hpc.eff', p['hpc_eff'])
            self.set_input_defaults('hpc.MN', p['hpc_MN'])
            self.set_input_defaults('burner.MN', 0.1)
            self.set_input_defaults('burner.dPqP', p['burner_dPqP'])
            self.set_input_defaults('hpt.eff', p['hpt_eff'])
            self.set_input_defaults('hpt.MN', 0.3)
            self.set_input_defaults('hpt.PR', 4.0)
            self.set_input_defaults('lpt.eff', p['lpt_eff'])
            self.set_input_defaults('lpt.MN', 0.4)
            self.set_input_defaults('lpt.PR', 4.0)
            self.set_input_defaults('fc.W', p['mass_flow'] * 2.20462, units='lbm/s')
            self.set_input_defaults('inlet.Fl_I:stat:W', p['mass_flow'] * 2.20462, units='lbm/s')
            self.set_input_defaults('burner.Fl_I:FAR', 0.027)
            self.set_input_defaults('lp_shaft.Nmech', 4000.0, units='rpm')
            self.set_input_defaults('hp_shaft.Nmech', 14000.0, units='rpm')

        super().setup()


def build_design_model() -> om.Problem:
    """Build and set up an OpenMDAO Problem for CFM56-5B design-point analysis."""
    prob = om.Problem()
    prob.model = CFM56Cycle(design=True, thermo_method='CEA')
    prob.setup(check=False)
    return prob


def build_offdesign_model() -> om.Problem:
    """Build and set up an OpenMDAO Problem for CFM56-5B off-design analysis."""
    prob = om.Problem()
    prob.model = CFM56Cycle(design=False, thermo_method='CEA')
    prob.setup(check=False)
    return prob
