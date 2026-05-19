# tests/test_cfm56.py
import pytest
from engine.cfm56 import CFM56_PARAMS, build_design_model, build_offdesign_model


def test_cfm56_params_physical_bounds():
    p = CFM56_PARAMS
    assert 5.0 < p['bpr'] < 7.0
    assert 20.0 < p['opr'] < 35.0
    assert 1500.0 < p['T4_design'] < 2000.0
    assert 100.0 < p['max_thrust_kN'] < 200.0


def test_cfm56_opr_matches_stage_prs():
    p = CFM56_PARAMS
    computed_opr = p['fan_PR'] * p['lpc_PR'] * p['hpc_PR']
    assert computed_opr == pytest.approx(p['opr'], rel=0.05)


def test_build_design_model_returns_problem():
    import openmdao.api as om
    prob = build_design_model()
    assert isinstance(prob, om.Problem)


def test_build_offdesign_model_returns_problem():
    import openmdao.api as om
    prob = build_offdesign_model()
    assert isinstance(prob, om.Problem)
