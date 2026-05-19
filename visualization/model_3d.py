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
    'inlet_in', 'fan_exit', 'fan_exit', 'lpc_exit',
    'lpc_exit', 'hpc_exit', 'hpc_exit', 'burner_exit',
    'hpt_exit', 'lpt_exit', 'core_nozz',
]


def plot_3d_model(results: EngineResults) -> go.Figure:
    """3D revolution surface model of CFM56 with temperature colormap."""
    x = _PROFILE[:, 0]
    r_core = _PROFILE[:, 1]
    r_byp = _PROFILE[:, 2]

    T_stations = []
    for s in _STATION_ORDER_3D:
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
            camera=dict(eye=dict(x=1.5, y=1.5, z=0.8)),
        ),
        width=900, height=600,
    )
    return fig
