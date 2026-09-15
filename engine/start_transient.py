# engine/start_transient.py
"""
CFM56-5B transient engine-start plant model (pure Python, no pyCycle).

Reduced-order HP-spool inertia ODE + empirical EGT/fuel correlations.
See docs/superpowers/specs/2026-06-13-engine-start-fadec-design.md.
"""
import math
from dataclasses import dataclass
from enum import Enum


class StartScenario(Enum):
    NORMAL = 'NORMAL'
    HUNG = 'HUNG'
    HOT = 'HOT'
    NO_FUEL = 'NO_FUEL'
    NO_IGNITION = 'NO_IGNITION'


@dataclass
class PlantParams:
    inertia: float = 10.0
    k_drag: float = 1.0
    starter_torque: float = 40.0
    starter_cutout: float = 50.0
    lightoff_N2: float = 18.0
    idle_N2: float = 60.0
    idle_N1: float = 19.0
    idle_EGT: float = 450.0
    idle_FF: float = 600.0
    idle_thrust: float = 5.0
    ambient_EGT: float = 15.0
    egt_redline: float = 725.0
    egt_bump: float = 435.0
    bump_peak_N2: float = 25.0
    bump_width: float = 9.0
    ff_min: float = 0.35

    @property
    def turbine_gain(self) -> float:
        return self.k_drag * self.idle_N2


def scenario_params(scenario: StartScenario) -> dict:
    table = {
        StartScenario.NORMAL:      dict(ff_cap=1.0, fuel_mult=1.0, fuel_valve_ok=True,  igniter_ok=True,  bleed_factor=1.0),
        StartScenario.HUNG:        dict(ff_cap=0.7, fuel_mult=1.0, fuel_valve_ok=True,  igniter_ok=True,  bleed_factor=1.0),
        StartScenario.HOT:         dict(ff_cap=1.0, fuel_mult=1.8, fuel_valve_ok=True,  igniter_ok=True,  bleed_factor=1.0),
        StartScenario.NO_FUEL:     dict(ff_cap=1.0, fuel_mult=1.0, fuel_valve_ok=False, igniter_ok=True,  bleed_factor=1.0),
        StartScenario.NO_IGNITION: dict(ff_cap=1.0, fuel_mult=1.0, fuel_valve_ok=True,  igniter_ok=False, bleed_factor=1.0),
    }
    return table[scenario]


def _clamp(x, lo, hi):
    return max(lo, min(hi, x))


def ff_frac(N2: float, ff_cap: float, p: PlantParams) -> float:
    if N2 < p.lightoff_N2:
        return 0.0
    span = 0.9 * p.idle_N2 - p.lightoff_N2
    raw = p.ff_min + (1.0 - p.ff_min) * (N2 - p.lightoff_N2) / span
    return _clamp(raw, 0.0, ff_cap)


def dN2_dt(N2, lit, valve_open, p, ff_cap, bleed_factor):
    if valve_open and N2 < p.starter_cutout:
        q_starter = p.starter_torque * bleed_factor * (1.0 - N2 / p.starter_cutout)
    else:
        q_starter = 0.0
    q_turbine = p.turbine_gain * ff_frac(N2, ff_cap, p) if lit else 0.0
    q_drag = p.k_drag * N2
    return (q_starter + q_turbine - q_drag) / p.inertia


def egt(N2, lit, fuel_mult, p):
    if not lit:
        return p.ambient_EGT
    base = p.ambient_EGT + (p.idle_EGT - p.ambient_EGT) * _clamp(N2 / p.idle_N2, 0.0, 1.0)
    bump = p.egt_bump * fuel_mult * math.exp(-((N2 - p.bump_peak_N2) / p.bump_width) ** 2)
    return base + bump


def derived_outputs(N2, lit, fuel_flowing, ff_cap, p):
    frac = _clamp(N2 / p.idle_N2, 0.0, 1.0)
    n1 = p.idle_N1 * frac ** 1.5
    thrust = p.idle_thrust * frac ** 3
    ff = ff_frac(N2, ff_cap, p) * p.idle_FF if (lit or fuel_flowing) else 0.0
    return n1, thrust, ff


def _idle_defaults(p):
    return {'idle_N2': p.idle_N2, 'idle_N1': p.idle_N1, 'idle_EGT': p.idle_EGT,
            'idle_FF': p.idle_FF, 'idle_thrust': p.idle_thrust}


def simulate_start(scenario, cockpit, idle_anchor=None, dt=0.5, t_max=180.0,
                   params=None):
    from engine.results import StartTransient
    from engine.fadec import fadec_commands

    p = params or PlantParams()
    if idle_anchor:
        for k, v in idle_anchor.items():
            if hasattr(p, k):
                setattr(p, k, v)
    sp = scenario_params(scenario)

    st = StartTransient(scenario=scenario.value)
    N2 = 0.0
    lit = False
    t = 0.0
    seen = set()
    hung_timer = 0.0
    nolight_timer = 0.0

    def log(label):
        if label not in seen:
            seen.add(label)
            st.events.append((round(t, 1), label))

    while t <= t_max:
        cmd = fadec_commands(N2, cockpit, p)
        valve, fuel_cmd, ign_cmd = cmd['valve_open'], cmd['fuel_cmd'], cmd['ignition_cmd']

        if valve:
            log('STARTER ON')
        if ign_cmd:
            log('IGNITION ON')

        can_light = (N2 >= p.lightoff_N2 and fuel_cmd and ign_cmd
                     and sp['fuel_valve_ok'] and sp['igniter_ok'])
        if can_light and not lit:
            lit = True
            log('LIGHT-OFF')

        fuel_flowing = fuel_cmd and sp['fuel_valve_ok']
        n1, thrust, ff = derived_outputs(N2, lit, fuel_flowing, sp['ff_cap'], p)
        if not sp['fuel_valve_ok']:
            ff = 0.0
        egt_v = egt(N2, lit, sp['fuel_mult'], p)

        st.t.append(round(t, 3)); st.N1.append(n1); st.N2.append(N2)
        st.EGT.append(egt_v); st.FF.append(ff); st.thrust.append(thrust)
        st.start_valve.append(valve); st.igniter.append(bool(ign_cmd))
        st.eng_mode.append(cockpit.mode.value); st.master.append(cockpit.master_on)

        if 'STARTER ON' in seen and not valve and N2 >= p.lightoff_N2:
            log('STARTER CUTOUT')

        rate = dN2_dt(N2, lit, valve, p, sp['ff_cap'], sp['bleed_factor'])

        # --- fault detection (detect-only) ---
        if egt_v > p.egt_redline and 'EGT EXCEEDANCE' not in st.faults:
            st.faults.append('EGT EXCEEDANCE')
            log('EGT EXCEEDANCE')

        if lit and N2 < 0.95 * p.idle_N2 and abs(rate) < 0.05:
            hung_timer += dt
            if hung_timer >= 8.0 and 'HUNG START' not in st.faults:
                st.faults.append('HUNG START')
                log('HUNG START')
        else:
            hung_timer = 0.0

        if fuel_cmd and not lit:
            nolight_timer += dt
            if nolight_timer >= 10.0:
                if ff > 1e-6 and 'WET START' not in st.faults:
                    st.faults.append('WET START')
                    log('WET START')
                elif ff <= 1e-6 and 'NO LIGHT-OFF' not in st.faults:
                    st.faults.append('NO LIGHT-OFF')
                    log('NO LIGHT-OFF')
        else:
            nolight_timer = 0.0

        # stop if a stable fault has been latched and spool is settled
        stuck = abs(rate) < 0.02 and N2 < 0.95 * p.idle_N2
        if st.faults and stuck and t > 20.0:
            break

        if N2 >= 0.99 * p.idle_N2:
            log('IDLE')
            break

        N2 = max(0.0, N2 + rate * dt)
        t += dt

    return st


def idle_anchor_from_results(result):
    """Build an idle-anchor dict from an EngineResults idle point.

    Only thrust and fuel flow are reliably transferable; N2/N1/EGT idle
    targets stay at PlantParams defaults unless explicitly provided.
    """
    return {'idle_thrust': float(result.thrust_kN),
            'idle_FF': float(result.fuel_flow) * 3600.0}
