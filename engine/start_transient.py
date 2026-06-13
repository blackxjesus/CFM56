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
    inertia: float = 25.0
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
