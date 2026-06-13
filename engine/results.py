# engine/results.py
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class StationData:
    station: str
    T: float      # K
    P: float      # kPa
    h: float      # kJ/kg


@dataclass
class EngineResults:
    flight_phase: str
    altitude_ft: float
    mach: float
    stations: Dict[str, StationData] = field(default_factory=dict)
    thrust_kN: float = 0.0
    sfc: float = 0.0        # kg/(kN·s)
    fan_eff: float = 0.0
    lpc_eff: float = 0.0
    hpc_eff: float = 0.0
    hpt_eff: float = 0.0
    lpt_eff: float = 0.0
    opr: float = 0.0
    bpr: float = 0.0
    fuel_flow: float = 0.0  # kg/s

    def to_dataframe(self):
        import pandas as pd
        rows = [
            {'station': name, 'T_K': s.T, 'P_kPa': s.P, 'h_kJkg': s.h}
            for name, s in self.stations.items()
        ]
        return pd.DataFrame(rows)

    def summary(self):
        print(f"=== {self.flight_phase} | Alt: {self.altitude_ft} ft | Mach: {self.mach} ===")
        print(f"  Tolóerő  : {self.thrust_kN:.1f} kN")
        print(f"  SFC      : {self.sfc:.5f} kg/(kN·s)")
        print(f"  OPR      : {self.opr:.2f}")
        print(f"  BPR      : {self.bpr:.2f}")
        print(f"  Tüzelőanyag: {self.fuel_flow:.2f} kg/s")
        print(f"  Állomások: {len(self.stations)}")


@dataclass
class StartTransient:
    """Recorded data from a single engine-start simulation run.

    The six signal lists (``t``, ``N1``, ``N2``, ``EGT``, ``FF``, ``thrust``)
    and the system-state lists (``start_valve``, ``igniter``, ``eng_mode``,
    ``master``) are populated in lockstep — one entry is appended per
    simulation timestep — so they always remain equal length.
    ``events`` and ``faults`` are independent logs and may have any length.

    Note: ``FF`` is in kg/h (display units), which is distinct from
    ``EngineResults.fuel_flow`` that is expressed in kg/s.
    """

    scenario: str
    t: List[float] = field(default_factory=list)        # s
    N1: List[float] = field(default_factory=list)       # %
    N2: List[float] = field(default_factory=list)       # %
    EGT: List[float] = field(default_factory=list)      # °C
    FF: List[float] = field(default_factory=list)       # kg/h
    thrust: List[float] = field(default_factory=list)   # kN
    start_valve: List[bool] = field(default_factory=list)
    igniter: List[bool] = field(default_factory=list)
    eng_mode: List[str] = field(default_factory=list)
    master: List[bool] = field(default_factory=list)
    events: List[Tuple[float, str]] = field(default_factory=list)
    faults: List[str] = field(default_factory=list)

    def to_dataframe(self):
        import pandas as pd
        n = len(self.t)
        assert all(len(x) == n for x in (self.N1, self.N2, self.EGT, self.FF, self.thrust)), \
            "StartTransient signal lists must be equal length"
        return pd.DataFrame({
            't': self.t, 'N1': self.N1, 'N2': self.N2,
            'EGT': self.EGT, 'FF': self.FF, 'thrust': self.thrust,
        })
