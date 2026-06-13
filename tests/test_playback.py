# tests/test_playback.py
import pytest
from engine.playback import step_playback


def test_no_advance_when_not_starting():
    assert step_playback('OFF', 0.0, 100, 10, 0.1, 0.5, 'RUNNING') == ('OFF', 0.0)
    assert step_playback('RUNNING', 5.0, 100, 10, 0.1, 0.5, 'RUNNING') == ('RUNNING', 5.0)


def test_advances_by_speed_factor():
    state, frame = step_playback('STARTING', 0.0, 100, 10, 0.1, 0.5, 'RUNNING')
    assert state == 'STARTING'
    assert frame == pytest.approx(2.0)


def test_speed_one_is_real_time():
    _, frame = step_playback('STARTING', 0.0, 100, 1, 0.1, 0.5, 'RUNNING')
    assert frame == pytest.approx(0.2)


def test_transitions_to_terminal_at_end_running():
    state, frame = step_playback('STARTING', 99.0, 100, 10, 0.1, 0.5, 'RUNNING')
    assert state == 'RUNNING'
    assert frame == pytest.approx(99.0)


def test_transitions_to_fault_at_end():
    state, _ = step_playback('STARTING', 99.0, 100, 10, 0.1, 0.5, 'FAULT')
    assert state == 'FAULT'


def test_crank_holds_at_last_frame_when_terminal_is_starting():
    state, frame = step_playback('STARTING', 99.0, 100, 10, 0.1, 0.5, 'STARTING')
    assert state == 'STARTING'
    assert frame == pytest.approx(99.0)
