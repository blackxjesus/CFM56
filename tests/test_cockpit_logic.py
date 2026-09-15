# tests/test_cockpit_logic.py
from engine.playback import start_armed, cockpit_action


def test_ign_start_with_master_and_bleed_arms_start():
    assert start_armed('IGN/START', master=True, bleed=True) is True


def test_norm_mode_never_arms_start():
    assert start_armed('NORM', master=True, bleed=True) is False
    assert cockpit_action('OFF', 'NORM', master=True, bleed=True) is None


def test_no_start_without_bleed():
    assert start_armed('IGN/START', master=True, bleed=False) is False


def test_crank_arms_dry_motoring():
    assert start_armed('CRANK', master=False, bleed=True) is True


def test_off_starts_in_ign_start():
    assert cockpit_action('OFF', 'IGN/START', master=True, bleed=True) == 'start'


def test_leaving_ign_start_during_start_aborts():
    assert cockpit_action('STARTING', 'NORM', master=True, bleed=True) == 'shutdown'


def test_running_engine_stays_running_after_return_to_norm():
    assert cockpit_action('RUNNING', 'NORM', master=True, bleed=True) is None
    assert cockpit_action('RUNNING', 'NORM', master=True, bleed=False) is None


def test_master_off_shuts_down_running_engine_in_any_mode():
    for mode in ('NORM', 'IGN/START', 'CRANK'):
        assert cockpit_action('RUNNING', mode, master=False, bleed=True) == 'shutdown'


def test_master_off_clears_fault():
    assert cockpit_action('FAULT', 'IGN/START', master=False, bleed=True) == 'shutdown'


def test_scenario_change_restarts_only_when_armed():
    assert cockpit_action('RUNNING', 'IGN/START', True, True, scenario_changed=True) == 'start'
    assert cockpit_action('RUNNING', 'NORM', True, True, scenario_changed=True) is None
