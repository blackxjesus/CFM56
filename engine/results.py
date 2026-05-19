# engine/results.py
from dataclasses import dataclass, field
from typing import Dict


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
