# tests/test_start_anchor.py
from engine.start_transient import idle_anchor_from_results


class _Stub:
    def __init__(self, thrust_kN, fuel_flow):
        self.thrust_kN = thrust_kN
        self.fuel_flow = fuel_flow   # kg/s


def test_idle_anchor_from_results_converts_units():
    r = _Stub(thrust_kN=4.2, fuel_flow=0.15)   # 0.15 kg/s -> 540 kg/h
    anchor = idle_anchor_from_results(r)
    assert anchor['idle_thrust'] == 4.2
    assert anchor['idle_FF'] == 540.0


def test_package_exports_start_symbols():
    import engine
    assert hasattr(engine, 'simulate_start')
    assert hasattr(engine, 'StartScenario')
    assert hasattr(engine, 'StartTransient')
