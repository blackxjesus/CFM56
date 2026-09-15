# visualization/start_plot.py
"""
Live engine-start trend chart (N1/N2, EGT, FF against time).

plot_start_transient(sd, i) draws a StartTransient up to frame i, so the app
can redraw it each animation tick alongside the E/WD. The time axis is fixed to
the whole start so the traces grow instead of the axes rescaling; the EGT start
limit and the sequence events reached so far are marked.
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

    now = sd.t[i]
    for t_ev, label in sd.events:
        if t_ev <= now:
            fig.add_vline(x=t_ev, line=dict(color='#666', dash='dot', width=1),
                          annotation_text=label, annotation_position='top left',
                          annotation_font=dict(size=9, color='#aaa'))

    # Fixed ranges so the animation grows the traces without rescaling
    fig.update_xaxes(range=(0, sd.t[-1]), gridcolor='#222')
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
