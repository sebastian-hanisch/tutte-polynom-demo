"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import tpl_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=340):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=50, b=10), legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_layers(layers: list):
    """Zahl der Zustände nach jeder Kante der Frontier-Rechnung."""
    fig = go.Figure()
    fig.add_trace(go.Bar(x=list(range(1, len(layers) + 1)), y=layers, name="Zustände", marker_color=C.COLOR_MAIN))
    fig.update_xaxes(title_text="Kante (Nummer in der Ordnung)")
    fig.update_yaxes(title_text="Zahl der Zustände")
    return _base(fig, 300)


def build_dc(rows: list):
    """Kantenmengen, Spannbäume (= Blätter), Aufrufe mit Zusammenfassen und Frontier-Zustände je Gitter (logarithmische Achse)."""
    fig = go.Figure()
    xs = [r["Gitter"] for r in rows]
    fig.add_trace(go.Bar(x=xs, y=[r["Mengen"] for r in rows], name="Kantenmengen 2^m", marker_color=C.COLOR_ALL))
    fig.add_trace(go.Bar(x=xs, y=[r["Spannbäume"] for r in rows], name="Blätter = Spannbäume", marker_color=C.COLOR_WARN))
    fig.add_trace(go.Bar(x=xs, y=[r["Aufrufe mit Zusammenfassen"] for r in rows], name="Aufrufe mit Zusammenfassen", marker_color=C.COLOR_LINE))
    fig.add_trace(go.Bar(x=xs, y=[r["Frontier-Zustände"] for r in rows], name="Frontier-Zustände", marker_color=C.COLOR_MAIN))
    fig.update_yaxes(title_text="Zahl", type="log")
    fig.update_layout(barmode="group")
    return _base(fig, 360)


def build_frontier(rows: list):
    """Zustände, größte Schicht und Monome gegen die Seitenlänge der quadratischen Gitter (logarithmische Achse)."""
    sq = [r for r in rows if r["quadratisch"]]
    ns = [int(r["Gitter"].split("×")[0]) for r in sq]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ns, y=[r["Zustände"] for r in sq], mode="lines+markers", name="Zustände (Summe)", line=dict(color=C.COLOR_MAIN)))
    fig.add_trace(go.Scatter(x=ns, y=[r["größte Schicht"] for r in sq], mode="lines+markers", name="größte Schicht (Catalan-Zahl)", line=dict(color=C.COLOR_LINE)))
    fig.add_trace(go.Scatter(x=ns, y=[r["Monome"] for r in sq], mode="lines+markers", name="Monome des Polynoms", line=dict(color=C.COLOR_WARN, dash="dot")))
    fig.update_xaxes(title_text="Seitenlänge n des n×n-Gitters", dtick=1)
    fig.update_yaxes(title_text="Zahl", type="log")
    return _base(fig, 340)


def build_colors(rows: list):
    """Zahl der Färbungen je Graph für zwei bis fünf Farben (logarithmische Achse; Nullen fehlen)."""
    fig = go.Figure()
    for k, color in zip(C.EXP_COLOR_KS, (C.COLOR_ALL, C.COLOR_LINE, C.COLOR_MAIN, C.COLOR_WARN)):
        fig.add_trace(go.Bar(x=[r["Graph"] for r in rows], y=[r["Werte"][k] or None for r in rows], name=f"{k} Farben", marker_color=color))
    fig.update_yaxes(title_text="Färbungen P(k)", type="log")
    fig.update_layout(barmode="group")
    return _base(fig, 360)


def build_reliability(rows: list):
    """Exakte Zuverlässigkeit über p (Linien) mit den Zufallsziehungen (Punkte)."""
    fig = go.Figure()
    for r, color in zip(rows, (C.COLOR_MAIN, C.COLOR_LINE, C.COLOR_WARN)):
        fig.add_trace(go.Scatter(x=[p for p, _ in r["Kurve"]], y=[v for _, v in r["Kurve"]], mode="lines", name=f"{r['Graph']} (exakt)", line=dict(color=color)))
        fig.add_trace(go.Scatter(x=[s["p"] for s in r["Ziehungen"]], y=[s["gezogen"] for s in r["Ziehungen"]], mode="markers", name=f"{r['Graph']} (gezogen)", marker=dict(color=color, size=9, symbol="diamond")))
    fig.update_xaxes(title_text="Wahrscheinlichkeit p, dass eine Kante hält")
    fig.update_yaxes(title_text="Wahrscheinlichkeit, dass der Graph zusammenhängt", range=[0, 1.02])
    return _base(fig, 360)
