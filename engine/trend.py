# engine/trend.py
"""
Continuous engine trend (N1/N2, EGT, FF against time) across start and run.

The start transient seeds the history; once RUNNING, step_trend appends one
sample per tick, easing each parameter toward the steady operating point of the
current throttle with a first-order spool lag. The trace therefore continues
from idle through every throttle change instead of jumping. No Streamlit here.
"""
import math
from dataclasses import dataclass, field
from typing import List, Tuple

SPOOL_TAU = 4.0       # s, first-order spool-up/down time constant
WINDOW = 600.0        # s of sim time kept in the history

SIGNALS = ('N1', 'N2', 'EGT', 'FF')


@dataclass
class TrendHistory:
    t: List[float] = field(default_factory=list)
    N1: List[float] = field(default_factory=list)
    N2: List[float] = field(default_factory=list)
    EGT: List[float] = field(default_factory=list)
    FF: List[float] = field(default_factory=list)
    events: List[Tuple[float, str]] = field(default_factory=list)

    def current(self):
        return {k: getattr(self, k)[-1] for k in SIGNALS}


def history_from_start(sd):
    """Seed a trend history with a (completed) start transient."""
    return TrendHistory(t=list(sd.t), N1=list(sd.N1), N2=list(sd.N2),
                        EGT=list(sd.EGT), FF=list(sd.FF), events=list(sd.events))


def step_trend(h, target, dt, label=None, tau=SPOOL_TAU, window=WINDOW):
    """Append one sample `dt` seconds on, lagging toward `target` {signal: value}.

    `label` (e.g. 'THR 45%') is logged as an event at the new sample. Samples
    older than `window` seconds are dropped. Returns the new current values.
    """
    a = 1.0 - math.exp(-dt / tau)
    t_new = round(h.t[-1] + dt, 3)
    h.t.append(t_new)
    for k in SIGNALS:
        x = getattr(h, k)[-1]
        getattr(h, k).append(x + (target[k] - x) * a)
    if label:
        h.events.append((t_new, label))

    t_min = t_new - window
    drop = 0
    while drop < len(h.t) - 1 and h.t[drop] < t_min:
        drop += 1
    if drop:
        for k in ('t',) + SIGNALS:
            del getattr(h, k)[:drop]
        h.events = [e for e in h.events if e[0] >= h.t[0]]
    return h.current()
