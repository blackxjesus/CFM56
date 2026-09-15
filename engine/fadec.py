# engine/fadec.py
"""
A320 / CFM56-5B FADEC + cockpit control logic (detect-only, no auto-abort).

Holds the cockpit panel state and turns it (plus N2 feedback) into plant
control commands. See docs/superpowers/specs/2026-06-13-engine-start-fadec-design.md.
"""
from dataclasses import dataclass
from enum import Enum


class EngMode(Enum):
    NORM = 'NORM'
    IGN_START = 'IGN_START'
    CRANK = 'CRANK'


@dataclass
class CockpitConfig:
    mode: EngMode = EngMode.IGN_START
    master_on: bool = True
    bleed_available: bool = True


def fadec_commands(N2, cfg, p):
    norm_start = cfg.mode in (EngMode.NORM, EngMode.IGN_START) and cfg.master_on and cfg.bleed_available
    crank = cfg.mode == EngMode.CRANK and cfg.bleed_available
    valve_open = (norm_start or crank) and N2 < p.starter_cutout
    fuel_cmd = norm_start and N2 >= p.lightoff_N2
    ignition_cmd = norm_start and N2 >= p.lightoff_N2
    return {'valve_open': valve_open, 'fuel_cmd': fuel_cmd, 'ignition_cmd': ignition_cmd}
