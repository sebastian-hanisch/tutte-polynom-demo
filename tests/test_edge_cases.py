"""Randfälle: Klemmen der Eingaben, Hinweise, Fehler bei unbekannten Werten, Grenzen der Prüfwege, Kantenlisten mit Müll."""

import pytest

import tpl_algorithm as A
import tpl_constants as C
import tpl_evaluation as ev

S = ev.Settings


def settings(**kw):
    base = dict(graph="Gitter", rows=3, cols=3, n=5, order="Zeile", k=3, p=90, edges=C.DEFAULT_EDGES)
    base.update(kw)
    return S(**base)


def test_one_by_one_grid_is_widened_to_one_by_two_with_a_note():
    a = ev.analyse(settings(rows=1, cols=1))
    assert a.label == "Gitter 1×2" and a.n == 2 and a.m == 1 and a.trees == 1 and any("mindestens zwei Knoten" in n for n in a.notes)


def test_grid_sides_are_clamped_to_the_cap():
    a = ev.analyse(settings(rows=99, cols=1))
    assert a.label == "Gitter 7×1" and a.n == 7


def test_complete_graph_and_cycle_sizes_are_clamped_with_a_note():
    a = ev.analyse(settings(graph="Vollständiger Graph", n=12))
    assert a.label == "K7" and any("bis K7" in n for n in a.notes) and a.trees == 7 ** 5
    b = ev.analyse(settings(graph="Vollständiger Graph", n=2))
    assert b.label == "K2" and b.notes == [] and b.trees == 1 and b.chromatic == 6
    c = ev.analyse(settings(graph="Kreis", n=2))
    assert c.label == "Kreis C3" and any("mindestens 3 Knoten" in n for n in c.notes)


def test_unknown_graph_and_order_raise():
    with pytest.raises(ValueError):
        ev.analyse(settings(graph="Zauber"))
    with pytest.raises(ValueError):
        ev.analyse(settings(order="Schlecht"))


def test_k_and_p_are_clamped_to_the_slider_range():
    low = ev.analyse(settings(k=-4, p=-5))
    high = ev.analyse(settings(k=999, p=999))
    assert low.k == C.K_MIN and float(low.p) == 0.01 and high.k == C.K_MAX and float(high.p) == 0.99


def test_one_color_gives_no_coloring_for_a_graph_with_an_edge():
    a = ev.analyse(settings(k=1))
    assert a.chromatic == 0 and any(w["Größe"].startswith("Färbungen mit 1 Farbe") for w in a.ways)


def test_invalid_custom_lists_fall_back_with_a_note():
    for bad in ("", "abc", "1-2, 3-4", "1-0", "1-10", "1-2-3", ",,,", "1-2, 2-3, " + ", ".join(["1-2"] * 25)):
        a = ev.analyse(settings(graph="Eigene Kantenliste", edges=bad))
        assert a.label == "Eigener Graph (Ersatzliste)" and a.m == 4 and a.notes and a.notes[0].startswith("Die Kantenliste ist nicht brauchbar"), bad


def test_parse_errors_have_german_messages():
    for text, part in (("", "leer"), ("x", "keine Kante"), ("1-12", "zwischen 1 und 9"), ("1-2, 3-4", "nicht zusammenhängend"), (", ".join(["1-2"] * 21), "Höchstens 20")):
        with pytest.raises(ValueError, match=part):
            A.parse_edge_list(text)


def test_custom_list_with_loop_and_parallel_edges_is_accepted():
    a = ev.analyse(settings(graph="Eigene Kantenliste", edges="1-1, 1-2, 1-2"))
    assert a.label == "Eigener Graph" and a.m == 3 and a.chromatic == 0 and a.trees == 2 and not a.problems
    assert a.tutte_text == "xy + y²"


def test_only_small_graphs_get_the_slow_checks():
    big = ev.analyse(settings(rows=6, cols=6))
    assert {w["Prüfung"] for w in big.ways if w["Prüfweg"] == "Teilmengensumme"} == {"nur bis 15 Kanten"}
    assert not any(w["Prüfweg"].startswith("Deletion") for w in big.ways)
    small = ev.analyse(settings(rows=2, cols=3))
    assert any(w["Prüfweg"].startswith("Deletion") for w in small.ways) and any(w["Prüfweg"].startswith("Teilmengensumme (alle") for w in small.ways)


def test_reliability_is_checked_by_sampling_above_twelve_edges():
    big = ev.analyse(settings(rows=4, cols=4))
    row = next(w for w in big.ways if w["Größe"].startswith("Zuverlässigkeit"))
    assert row["Prüfweg"].startswith("Zufallsziehen") and row["Prüfung"].startswith("z = ")
    small = ev.analyse(settings(rows=2, cols=3))
    assert next(w for w in small.ways if w["Größe"].startswith("Zuverlässigkeit"))["Prüfung"] == "gleich"


def test_orientation_check_switches_to_stanley_above_twelve_edges():
    big = ev.analyse(settings(rows=3, cols=5))
    assert next(w for w in big.ways if w["Größe"].startswith("Azyklische"))["Prüfweg"].startswith("Stanley")
    small = ev.analyse(settings(rows=2, cols=2))
    assert next(w for w in small.ways if w["Größe"].startswith("Azyklische"))["Prüfweg"].startswith("Aufzählen")


def test_coloring_check_picks_the_first_available_way():
    assert ev.check_chromatic(3, A.complete_graph(3)[1], "K3", 3, 6, {}, 1)[0] == "Zählen aller Färbungen"
    n, e = A.grid_graph(6, 6)
    assert ev.check_chromatic(n, e, "Gitter 6×6", 3, 101596896, {}, 1)[0] == "Zeilen-Transfermatrix"
    assert ev.check_chromatic(n, e, "Gitter 6×6", 6, 0, {}, 1)[2].startswith("nur bis")
    assert ev.check_chromatic(10, A.petersen_graph()[1], "Petersen-Graph", 5, 332880, {}, 1)[0].startswith("Stück 12")
    assert ev.check_chromatic(10, A.petersen_graph()[1], "Petersen-Graph", 9, 0, {}, 1)[1] == "–"


def test_tutte_text_is_hidden_for_large_polynomials_and_chromatic_text_for_high_degree():
    a = ev.analyse(settings(rows=6, cols=6))
    assert a.tutte_text is None and a.chromatic_text is None
    b = ev.analyse(settings(graph="Kreis", n=5))
    assert b.tutte_text == "x⁴ + x³ + x² + x + y" and b.chromatic_text == "k⁵ − 5k⁴ + 10k³ − 10k² + 4k"


def test_formatting_helpers():
    assert ev.de(1.5, 2) == "1,50" and ev.de(-0.25, 1) == "−0,2"
    assert ev.big_text(999999999999999) == "999.999.999.999.999" and ev.big_text(10 ** 15) == "1,00·10¹⁵ (16 Stellen)" and ev.big_text(-1234) == "−1.234"
    assert ev.plural(1, "Monom", "Monomen") == "1 Monom" and ev.plural(1234, "Monom", "Monomen") == "1.234 Monomen" and ev.plural(0, "Färbung", "Färbungen") == "0 Färbungen"
    from fractions import Fraction
    assert ev.prob_text(Fraction(7, 27)) == "0,259259" and ev.prob_text(Fraction(0)) == "0" and ev.prob_text(Fraction(1, 10 ** 6)) == "1,00·10⁻⁶"


def test_play_graph_reports_errors_instead_of_raising():
    assert ev.play_graph("")["error"].startswith("Die Kantenliste ist leer") and "nicht zusammenhängend" in ev.play_graph("1-2, 3-4")["error"]
    ok = ev.play_graph("1-2, 2-3, 3-1, 3-4")
    assert ok["trees"] == 3 and ok["ok"] is True and ok["tutte_text"] == "x³ + x² + xy"
    big = ev.play_graph(", ".join(f"{a}-{b}" for a, b in [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9), (1, 9), (1, 5), (2, 6), (3, 7), (4, 8), (1, 3), (2, 4), (5, 7)]))
    assert big["ok"] is None and ev.verdict_play(big)[0] == "success"
    assert ev.verdict_play({"error": "kaputt"}) == ("warning", "kaputt")
