# tests/test_start_results.py
import pytest
from engine.results import StartTransient


def test_start_transient_defaults_empty():
    st = StartTransient(scenario='NORMAL')
    assert st.scenario == 'NORMAL'
    assert st.t == []
    assert st.N2 == []
    assert st.events == []
    assert st.faults == []


def test_start_transient_append_frame():
    st = StartTransient(scenario='NORMAL')
    st.t.append(0.0)
    st.N2.append(0.0)
    st.EGT.append(15.0)
    assert st.N2[-1] == 0.0
    assert st.EGT[-1] == pytest.approx(15.0)


def test_start_transient_to_dataframe():
    st = StartTransient(scenario='NORMAL')
    st.t.extend([0.0, 0.5])
    st.N1.extend([0.0, 0.1]); st.N2.extend([0.0, 1.0])
    st.EGT.extend([15.0, 15.0]); st.FF.extend([0.0, 0.0])
    st.thrust.extend([0.0, 0.0])
    df = st.to_dataframe()
    assert len(df) == 2
    assert list(df.columns) == ['t', 'N1', 'N2', 'EGT', 'FF', 'thrust']
