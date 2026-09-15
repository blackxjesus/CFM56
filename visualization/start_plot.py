# visualization/start_plot.py
"""
Live engine-start trend chart (N1/N2, EGT, FF against time).

plot_start_transient(sd, i) draws a StartTransient (or a running
engine.trend.TrendHistory, which has the same signals) up to frame i, so the app
can redraw it each tick alongside the E/WD. The time axis spans the whole start
(or the whole history) so the traces grow instead of the axes rescaling; the EGT
start limit and the events reached so far are marked.
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots

EGT_START_LIMIT = 725.0   # °C, matches PlantParams.egt_redline

_GRN, _CYN, _AMB, _RED = '#2bd92b', '#27c3e6', '#ffaa00', '#ff3b30'


def plot_start_transient(sd, i, egt_limit=EGT_START_LIMIT):
    """Plotly figure of the start transient `sd` drawn up to frame index `i`."""
    n = i + 1
    t = sd.t[:n]
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.06,
                        subplot_titles=('N1 / N2 [%]', 'EGT [°C]', 'FF [kg/h]'))

    fig.add_trace(go.Scatter(x=t, y=sd.N2[:n], name='N2', line=dict(color=_GRN, width=2)), 1, 1)
    fig.add_trace(go.Scatter(x=t, y=sd.N1[:n], name='N1', line=dict(color=_CYN, width=2)), 1, 1)
    fig.add_trace(go.Scatter(x=t, y=sd.EGT[:n], name='EGT', line=dict(color=_AMB, width=2)), 2, 1)
    fig.add_trace(go.Scatter(x=t, y=sd.FF[:n], name='FF', line=dict(color=_GRN, width=2)), 3, 1)

    fig.add_hline(y=egt_limit, row=2, col=1, line=dict(color=_RED, dash='dash', width=1),
                  label=dict(text=f'START LIMIT {egt_limit:.0f} °C',
                             textposition='end', font=dict(color=_RED, size=10)))

    # Event markers; labels stack down the top panel so ones close in time
    # (e.g. IGNITION ON / LIGHT-OFF) don't overprint each other.
    now = sd.t[i]
    shown = [(t_ev, label) for t_ev, label in sd.events if t_ev <= now]
    span = max(1e-6, sd.t[-1] - sd.t[0])
    level, last_t = 0, None
    for t_ev, label in shown:
        level = level + 1 if last_t is not None and t_ev - last_t < 0.08 * span else 0
        last_t = t_ev
        for row in (1, 2, 3):
            fig.add_vline(x=t_ev, line=dict(color='#666', dash='dot', width=1), row=row, col=1)
        fig.add_annotation(x=t_ev, y=1 - 0.13 * (level % 4), xref='x', yref='y domain',
                           text=label, showarrow=False, xanchor='left', yanchor='top',
                           xshift=3, font=dict(size=9, color='#aaa'), row=1, col=1)

    # Fixed ranges so the animation grows the traces without rescaling
    fig.update_xaxes(range=(sd.t[0], sd.t[-1]), gridcolor='#222')
    fig.update_xaxes(title_text='t [s]', row=3, col=1)
    fig.update_yaxes(range=(0, max(100.0, max(sd.N2) * 1.1)), row=1, col=1)
    fig.update_yaxes(range=(0, max(egt_limit, max(sd.EGT)) * 1.15), row=2, col=1)
    fig.update_yaxes(range=(0, max(1.0, max(sd.FF)) * 1.15), row=3, col=1)
    fig.update_yaxes(gridcolor='#222')
    fig.update_layout(height=560, margin=dict(l=50, r=20, t=40, b=40),
                      paper_bgcolor='#050505', plot_bgcolor='#050505',
                      font=dict(family='Courier New, monospace', color='#ccc'),
                      legend=dict(orientation='h', y=1.08, x=1, xanchor='right'),
                      uirevision='start')
    return fig
