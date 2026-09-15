# tests/test_fadec.py
import pytest
from engine.fadec import EngMode, CockpitConfig, fadec_commands
from engine.start_transient import PlantParams

P = PlantParams()


def test_valve_opens_on_norm_master_bleed():
    cfg = CockpitConfig(mode=EngMode.IGN_START, master_on=True, bleed_available=True)
    cmd = fadec_commands(N2=5.0, cfg=cfg, p=P)
    assert cmd['valve_open'] is True
    assert cmd['fuel_cmd'] is False


def test_no_valve_without_bleed():
    cfg = CockpitConfig(mode=EngMode.IGN_START, master_on=True, bleed_available=False)
    cmd = fadec_commands(N2=5.0, cfg=cfg, p=P)
    assert cmd['valve_open'] is False


def test_fuel_and_ignition_at_lightoff_n2():
    cfg = CockpitConfig(mode=EngMode.IGN_START, master_on=True, bleed_available=True)
    cmd = fadec_commands(N2=P.lightoff_N2, cfg=cfg, p=P)
    assert cmd['fuel_cmd'] is True
    assert cmd['ignition_cmd'] is True


def test_valve_closes_at_cutout():
    cfg = CockpitConfig(mode=EngMode.IGN_START, master_on=True, bleed_available=True)
    cmd = fadec_commands(N2=P.starter_cutout, cfg=cfg, p=P)
    assert cmd['valve_open'] is False


def test_crank_motors_without_fuel_or_ignition():
    cfg = CockpitConfig(mode=EngMode.CRANK, master_on=False, bleed_available=True)
    cmd = fadec_commands(N2=30.0, cfg=cfg, p=P)
    assert cmd['valve_open'] is True
    assert cmd['fuel_cmd'] is False
    assert cmd['ignition_cmd'] is False
