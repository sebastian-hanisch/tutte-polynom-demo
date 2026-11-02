"""Oberfläche: jeder Graph, jedes Preset, Permalink mit Müll, die Spielwiese und das PDF laufen ohne Ausnahme und zeigen die erwarteten Texte."""

import os
from pathlib import Path

from streamlit.testing.v1 import AppTest

import tpl_constants as C
import tpl_evaluation as ev
import tpl_visualization as V

APP = str(Path(__file__).resolve().parent.parent / "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))


def _run(query=None, **state):
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    for key, value in (query or {}).items():
        at.query_params[key] = value
    at.run()
    for key, value in state.items():
        at.session_state[key] = value
    if state:
        at.run()
    assert not at.exception, [str(e) for e in at.exception]
    return at


def _texts(at):
    return [e.value for e in at.success] + [e.value for e in at.warning] + [e.value for e in at.info] + [e.value for e in at.error]


def test_standard_case_shows_all_five_experiments_and_the_answer():
    at = _run()
    heads = [s.value for s in at.subheader]
    assert [h for h in heads if h.startswith("🔬 Experiment")] == [
        "🔬 Experiment 1: Deletion–Contraction, ohne und mit Zusammenfassen", "🔬 Experiment 2: Ein Polynom, viele Zahlen", "🔬 Experiment 3: Frontier im Polynom-Semiring",
        "🔬 Experiment 4: Das chromatische Polynom", "🔬 Experiment 5: Zuverlässigkeit"]
    assert any(t.startswith("Gitter 6×6: 36 Knoten, 60 Kanten.") for t in _texts(at)) and not at.error


def test_metrics_of_the_standard_case():
    at = _run()
    assert [(m.label, m.value) for m in at.metric] == [("Monome des Polynoms", "430"), ("Frontier-Zustände (Summe)", "6.001"), ("Spannbäume", "32.565.539.635.200"), ("Färbungen mit 3 Farben", "101.596.896")]


def test_every_preset_runs_and_shows_its_graph():
    for name, p in C.PRESETS.items():
        at = _run(graph_select=p["graph"], rows_slider=p["rows"], cols_slider=p["cols"], n_slider=p["n"], order_select=p["order"], k_slider=p["k"], p_slider=p["p"], edges_input=p["edges"])
        assert at.selectbox(key="graph_select").value == p["graph"], name
        assert not at.error, name


def test_every_graph_kind_runs_on_a_small_size():
    for graph in C.GRAPHS:
        at = _run(graph_select=graph, rows_slider=2, cols_slider=3, n_slider=4)
        assert not at.error, graph


def test_polynomial_text_is_shown_for_small_graphs_only():
    small = _run(graph_select="Kreis", n_slider=5)
    assert [c.value for c in small.get("code")] == ["T(x, y) = x⁴ + x³ + x² + x + y", "P(k) = k⁵ − 5k⁴ + 10k³ − 10k² + 4k"]
    big = _run()
    assert not big.get("code") and any("zu viele für die Anzeige" in c.value for c in big.caption)


def test_permalink_garbage_falls_back_to_defaults():
    at = _run(query={"graph": "Unsinn", "order": "Zauber", "rows": "abc", "cols": "99999", "k": "-5", "p": "0", "edges": "x" * 300})
    assert at.selectbox(key="graph_select").value == C.DEFAULT_GRAPH and at.selectbox(key="order_select").value == C.DEFAULT_ORDER
    assert at.slider(key="rows_slider").value == C.DEFAULT_ROWS and at.slider(key="cols_slider").value == C.SIDE_MAX
    assert at.slider(key="k_slider").value == C.K_MIN and at.slider(key="p_slider").value == C.P_MIN and len(at.text_input(key="edges_input").value) <= C.EDGES_MAX_LEN


def test_invalid_custom_list_shows_a_note_and_still_answers():
    at = _run(graph_select="Eigene Kantenliste", edges_input="1-2, 3-4")
    assert any(t.startswith("Die Kantenliste ist nicht brauchbar") for t in _texts(at)) and any(t.startswith("Eigener Graph (Ersatzliste): 4 Knoten") for t in _texts(at))


def test_one_by_one_grid_shows_the_widening_note():
    at = _run(rows_slider=1, cols_slider=1)
    assert any("gerechnet wird mit 1×2" in t for t in _texts(at))


def test_play_ground_answers_and_reports_bad_input():
    at = _run()
    assert any(t.startswith("4 Knoten, 4 Kanten: T(x, y) = x³ + x² + xy") for t in _texts(at))
    bad = _run(play_edges="1-2, 5-6")
    assert any("nicht zusammenhängend" in t for t in [w.value for w in bad.warning])
    big = _run(play_edges="1-2, 2-3, 3-4, 4-1, 1-3")
    assert any(t.startswith("4 Knoten, 5 Kanten") for t in _texts(big))


def test_pdf_button_makes_a_download():
    at = _run()
    at.button(key="pdf_make").click().run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    assert len(at.get("download_button")) == 1


def test_charts_have_unique_keys():
    at = _run()
    keys = [c.key for c in at.get("plotly_chart")]
    assert len(keys) == len(set(keys)) and set(keys) == {"main_chart", "dc_chart", "frontier_chart", "color_chart", "rel_chart"}


def test_pdf_builds_for_every_graph_kind():
    from tpl_pdf_export import build_pdf
    for graph in C.GRAPHS:
        a = ev.analyse(ev.Settings(graph, 3, 3, 5, "Zeile", 3, 90, C.DEFAULT_EDGES))
        assert build_pdf(a)[:4] == b"%PDF", graph
    big = ev.analyse(ev.Settings("Gitter", 6, 6, 5, "Zeile", 3, 90, C.DEFAULT_EDGES))
    assert build_pdf(big)[:4] == b"%PDF"


def test_chart_builders_return_locked_axes():
    a = ev.analyse(ev.Settings("Gitter", 4, 4, 5, "Zeile", 3, 90, C.DEFAULT_EDGES))
    for fig in (V.build_layers(a.layers), V.build_dc(ev.dc_rows()), V.build_frontier(ev.frontier_rows()), V.build_colors(ev.color_rows()), V.build_reliability(ev.reliability_rows())):
        assert fig.layout.xaxis.fixedrange and fig.layout.yaxis.fixedrange
