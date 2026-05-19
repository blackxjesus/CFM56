# visualization/model_3d.py
import numpy as np
import plotly.graph_objects as go
from engine.results import EngineResults

_PROFILE = np.array([
    # x,    r_core, r_bypass
    [0.00,  0.25,   0.55],
    [0.30,  0.25,   0.55],
    [0.30,  0.25,   0.52],
    [0.60,  0.22,   0.48],
    [0.90,  0.18,   0.44],
    [1.20,  0.14,   0.40],
    [1.40,  0.14,   0.38],
    [1.70,  0.16,   0.30],
    [2.00,  0.19,   0.22],
    [2.40,  0.22,   0.22],
    [2.60,  0.18,   0.18],
])

_STATION_ORDER_3D = [
    'S2_inlet_exit', 'S21_fan_exit', 'S21_fan_exit', 'S25_lpc_exit',
    'S25_lpc_exit', 'S3_hpc_exit', 'S3_hpc_exit', 'S4_burner_exit',
    'S45_hpt_exit', 'S5_lpt_exit', 'S8_core_nozz',
]
_STATION_ORDER_3D_ALT = [
    'inlet_in', 'fan_exit', 'fan_exit', 'lpc_exit',
    'lpc_exit', 'hpc_exit', 'hpc_exit', 'burner_exit',
    'hpt_exit', 'lpt_exit', 'core_nozz',
]


def _exhaust_plume(results: EngineResults, n_theta: int = 60):
    """Build exhaust plume Surface traces (core jet + bypass fan stream)."""
    traces = []

    # --- Nozzle exit conditions ---
    core_T  = results.stations.get('S8_core_nozz',  results.stations.get('core_nozz'))
    byp_T   = results.stations.get('S18_byp_nozz',  results.stations.get('byp_nozz'))
    T_core  = core_T.T  if core_T  else 900.0
    T_byp   = byp_T.T   if byp_T   else 330.0

    theta = np.linspace(0, 2 * np.pi, n_theta)

    # ── Core exhaust plume ────────────────────────────────────────────────
    # Starts at x=2.60, r=0.18; expands then contracts like a free jet
    n_x = 40
    x_plume = np.linspace(2.60, 2.60 + 1.80, n_x)     # 1.8 m long plume
    # Radius: slight initial expansion then slow decay
    r_plume = 0.18 * (1.0 + 0.25 * np.exp(-((x_plume - 2.75) ** 2) / 0.15)) \
              * np.exp(-0.6 * (x_plume - 2.60))
    r_plume = np.maximum(r_plume, 0.005)

    # Temperature: exponential decay from T_core to ambient ~280 K
    T_decay = 280.0 + (T_core - 280.0) * np.exp(-2.5 * (x_plume - 2.60))

    X_c = np.outer(x_plume, np.ones(n_theta))
    Y_c = np.outer(r_plume, np.cos(theta))
    Z_c = np.outer(r_plume, np.sin(theta))
    C_c = np.outer(T_decay, np.ones(n_theta))

    traces.append(go.Surface(
        x=X_c, y=Y_c, z=Z_c,
        surfacecolor=C_c,
        colorscale='Hot',
        cmin=280, cmax=max(T_core, 1000),
        colorbar=dict(title='Kipufogó T [K]', x=1.10),
        name='Core kipufogó',
        opacity=0.75,
        showscale=True,
    ))

    # ── Bypass fan stream (cooler, larger radius) ─────────────────────────
    n_x2 = 30
    x_fan = np.linspace(2.60, 2.60 + 1.20, n_x2)
    r_fan_in  = 0.18
    r_fan_out = 0.38   # bypass exit radius at nozzle
    # Annular region — outer surface
    r_fan = r_fan_out * np.exp(-1.2 * (x_fan - 2.60)) + r_fan_in
    r_fan = np.maximum(r_fan, r_fan_in + 0.005)

    T_fan_decay = 280.0 + (T_byp - 280.0) * np.exp(-3.0 * (x_fan - 2.60))

    X_f = np.outer(x_fan, np.ones(n_theta))
    Y_f = np.outer(r_fan, np.cos(theta))
    Z_f = np.outer(r_fan, np.sin(theta))
    C_f = np.outer(T_fan_decay, np.ones(n_theta))

    traces.append(go.Surface(
        x=X_f, y=Y_f, z=Z_f,
        surfacecolor=C_f,
        colorscale='Blues',
        cmin=280, cmax=400,
        showscale=False,
        name='Bypass kipufogó',
        opacity=0.30,
    ))

    return traces


def plot_3d_model(results: EngineResults) -> go.Figure:
    """3D revolution surface model of CFM56 with temperature colormap and exhaust plume."""
    x = _PROFILE[:, 0]
    r_core = _PROFILE[:, 1]
    r_byp  = _PROFILE[:, 2]

    order = _STATION_ORDER_3D if any(s in results.stations for s in _STATION_ORDER_3D) \
            else _STATION_ORDER_3D_ALT
    T_stations = []
    for s in order:
        if s in results.stations:
            T_stations.append(results.stations[s].T)
        else:
            T_stations.append(500.0)
    T_arr = np.array(T_stations)

    n_theta = 60
    theta = np.linspace(0, 2 * np.pi, n_theta)
    T_surface = np.outer(T_arr, np.ones(n_theta))

    X_core = np.outer(x, np.ones(n_theta))
    Y_core = np.outer(r_core, np.cos(theta))
    Z_core = np.outer(r_core, np.sin(theta))

    X_byp = np.outer(x, np.ones(n_theta))
    Y_byp = np.outer(r_byp, np.cos(theta))
    Z_byp = np.outer(r_byp, np.sin(theta))

    fig = go.Figure()

    # Engine body
    fig.add_trace(go.Surface(
        x=X_core, y=Y_core, z=Z_core,
        surfacecolor=T_surface,
        colorscale='RdYlBu_r',
        cmin=280, cmax=1800,
        colorbar=dict(title='Hőmérséklet [K]', x=1.02),
        name='Core',
        opacity=0.95,
    ))
    fig.add_trace(go.Surface(
        x=X_byp, y=Y_byp, z=Z_byp,
        surfacecolor=np.full_like(T_surface, 320.0),
        colorscale='Blues',
        cmin=280, cmax=400,
        showscale=False,
        name='Bypass',
        opacity=0.35,
    ))

    # Exhaust plume
    for trace in _exhaust_plume(results, n_theta=n_theta):
        fig.add_trace(trace)

    fig.update_layout(
        title=dict(
            text=(f'CFM56-5B 3D Modell — {results.flight_phase.upper()}<br>'
                  f'Tolóerő: {results.thrust_kN:.1f} kN | OPR: {results.opr:.1f} | '
                  f'Mach: {results.mach}'),
            x=0.5
        ),
        scene=dict(
            xaxis_title='Tengelyirány [m]',
            yaxis_title='Y [m]',
            zaxis_title='Z [m]',
            aspectmode='data',
            camera=dict(eye=dict(x=1.8, y=1.5, z=0.8)),
        ),
        width=1000, height=650,
    )
    return fig
