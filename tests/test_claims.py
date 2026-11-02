"""Jede Zahl aus der README und aus den Texten der App, nachgerechnet (DEMO-PLAYBOOK §4). Alles ist deterministisch bis auf das Zufallsziehen mit festem Seed; Zeiten kommen nicht vor."""

from fractions import Fraction
from pathlib import Path

import tpl_algorithm as A
import tpl_constants as C
import tpl_evaluation as ev

README = (Path(__file__).resolve().parent.parent / "README.md").read_text(encoding="utf-8")
S = ev.Settings


def grid_T(rows, cols):
    n, e = A.grid_graph(rows, cols)
    return n, e, A.frontier_tutte(n, e)


def test_readme_hand_instances(triangle, square, k4):
    T = triangle["T"]
    assert A.poly_text(T) == "x² + x + y" and A.spanning_trees(T) == 3 and A.coefficient_text(A.chromatic_coefficients(T, 3, 1)) == "k³ − 3k² + 2k" and A.acyclic_orientations(T) == 6
    assert A.reliability_value(T, 3, 3, 1, Fraction(1, 3)) == Fraction(7, 27) and [A.flow_value(T, 3, 3, 1, k) for k in (2, 3, 4)] == [1, 2, 3]
    assert A.poly_text(square["T"]) == "x³ + x² + x + y" and A.spanning_trees(square["T"]) == 4 and A.chromatic_value(square["T"], 4, 1, 3) == 18 and A.acyclic_orientations(square["T"]) == 14
    assert A.poly_text(k4["T"]) == "x³ + y³ + 3x² + 4xy + 3y² + 2x + 2y"
    assert A.frontier_tutte(4, k4["edges"])[0] == k4["T"] and A.spanning_trees(k4["T"]) == 16 and A.chromatic_value(k4["T"], 4, 1, 4) == 24 and A.acyclic_orientations(k4["T"]) == 24 and A.flow_value(k4["T"], 4, 6, 1, 4) == 6


def test_readme_deletion_contraction_rows():
    rows = {r["Gitter"]: r for r in ev.dc_rows()}
    expected = {"2×2": (4, 4, 14, 11, 7), "2×3": (7, 15, 66, 33, 21), "3×3": (12, 192, 851, 132, 46), "2×5": (13, 209, 1214, 141, 151), "3×4": (17, 2415, 12065, 574, 153), "4×4": (24, 100352, 497030, 3418, 251)}
    for g, (m, trees, plain, memo, states) in expected.items():
        r = rows[g]
        assert (r["Kanten"], r["Spannbäume"], r["Aufrufe"], r["Aufrufe mit Zusammenfassen"], r["Frontier-Zustände"]) == (m, trees, plain, memo, states) and r["Blätter"] == trees and r["Mengen"] == 2 ** m, g
    for g, (m, trees, memo, states) in {"3×6": (27, 380160, 5992, 1649), "5×5": (40, 557568000, 242898, 1259)}.items():
        r = rows[g]
        assert (r["Kanten"], r["Spannbäume"], r["Aufrufe"], r["Aufrufe mit Zusammenfassen"], r["Frontier-Zustände"]) == (m, trees, None, memo, states), g
    assert all(r["gleich"] for r in rows.values()) and rows["4×4"]["Mengen"] == 16777216


def test_readme_frontier_rows():
    rows = {r["Gitter"]: r for r in ev.frontier_rows()}
    expected = {"3×3": (5, 46, 21), "4×4": (14, 251, 73), "5×5": (42, 1259, 194), "6×6": (132, 6001, 430), "7×7": (429, 27645, 839), "3×8": (1341, 17657, 171), "8×3": (5, 171, 171)}
    for g, (layer, states, mono) in expected.items():
        assert (rows[g]["größte Schicht"], rows[g]["Zustände"], rows[g]["Monome"]) == (layer, states, mono), g
    assert [rows[f"{n}×{n}"]["Catalan"] for n in range(3, 8)] == [5, 14, 42, 132, 429] and A.catalan(8) == 1430
    assert (rows["3×8"]["Frontier"], rows["8×3"]["Frontier"]) == (9, 4) and rows["3×8"]["Spannbäume"] == rows["8×3"]["Spannbäume"] == 59817135


def test_readme_grid_value_rows():
    rows = {r["Graph"]: r for r in ev.value_rows()}
    for g, vals in {"Gitter 3×3": (192, 3102, 431, 2398, 246, 9612), "Gitter 4×4": (100352, 8790016, 555195, 5015972, 7812, 6000732),
                    "Gitter 6×6": (32565539635200, 181075508242067552, 2692324030864335, 39931856138212664, 101596896, 380053267505964)}.items():
        r = rows[g]
        assert (r["Spannbäume"], r["Wälder"], r["Teilgraphen"], r["Orientierungen"], r["P3"], r["P4"]) == vals, g
    assert rows["Gitter 6×6"]["Monome"] == 430 and rows["Gitter 6×6"]["Kanten"] == 60 and 2 ** 60 == 1152921504606846976


def test_readme_other_graph_rows():
    rows = {r["Graph"]: r for r in ev.value_rows()}
    for g, vals in {"K4": (16, 38, 38, 24), "K5": (125, 291, 728, 120), "Kreis C6": (6, 63, 7, 62), "Petersen-Graph": (2000, 22292, 5968, 16680)}.items():
        r = rows[g]
        assert (r["Spannbäume"], r["Wälder"], r["Teilgraphen"], r["Orientierungen"]) == vals, g
    assert (rows["Kreis C6"]["P3"], rows["Kreis C6"]["P4"]) == (66, 732) and rows["Petersen-Graph"]["Monome"] == 26 and rows["Dreieck"]["P3"] == 6 and rows["K4"]["P4"] == 24
    assert all(r["gleich"] == r["Prüfungen"] and not r["Probleme"] for r in rows.values()) and sum(r["Prüfungen"] for r in rows.values()) == 71


def test_readme_petersen_row():
    n, e = A.petersen_graph()
    T, info = A.frontier_tutte(n, e)
    assert A.coefficient_text(A.chromatic_coefficients(T, n, 1)) == "k¹⁰ − 15k⁹ + 105k⁸ − 455k⁷ + 1353k⁶ − 2861k⁵ + 4275k⁴ − 4305k³ + 2606k² − 704k"
    assert [A.chromatic_value(T, n, 1, k) for k in (3, 4, 5)] == [120, 12960, 332880] == [C.PETERSEN_COLORINGS[k] for k in (3, 4, 5)]
    assert [A.flow_value(T, n, 15, 1, k) for k in (2, 3, 4, 5)] == [0, 0, 0, 240] == [0, 0, 0, C.PETERSEN_FLOW_5]


def test_readme_color_rows():
    rows = {r["Graph"]: r for r in ev.color_rows()}
    expected = {"Dreieck": [0, 6, 24, 60], "K4": [0, 0, 24, 120], "Kreis C6": [2, 66, 732, 4100], "Petersen-Graph": [0, 120, 12960, 332880], "Gitter 3×3": [2, 246, 9612, 142820], "Gitter 4×4": [2, 7812, 6000732, 828850160]}
    for g, vals in expected.items():
        assert [rows[g]["Werte"][k] for k in C.EXP_COLOR_KS] == vals, g
    assert [rows[g]["chromatische Zahl"] for g in expected] == [3, 4, 2, 3, 2, 2]
    assert all(c == "gleich" for r in rows.values() for _, c in r["Prüfung"].values())


def test_readme_reliability_rows():
    rows = {r["Graph"]: r for r in ev.reliability_rows()}
    expected = {"Gitter 4×4": [(0.033092, 0.0333), (0.944085, 0.9443), (0.999584, 0.9996)], "Gitter 6×6": [(0.002335, 0.00237), (0.935088, 0.9355), (0.999576, 0.99933)], "Petersen-Graph": [(0.182129, 0.18), (0.988567, 0.9891), (0.99999, 1.0)]}
    for g, vals in expected.items():
        got = [(round(s["exakt"], 6), round(s["gezogen"], 5)) for s in rows[g]["Ziehungen"]]
        assert got == [(round(a, 6), round(b, 5)) for a, b in vals], g
    assert f"{max(abs(s['z']) for r in rows.values() for s in r['Ziehungen']):.2f}" == "2.04"
    assert A.reliability_value(A.frontier_tutte(*A.cycle_graph(5))[0], 5, 5, 1, Fraction(1, 2)) == Fraction(6, 32)


def test_readme_play_row():
    res = ev.play_graph(C.PLAY_EDGES_DEFAULT)
    assert (res["tutte_text"], res["trees"], res["acyclic"], res["chromatic_text"], res["ok"]) == ("x³ + x² + xy", 3, 12, "k⁴ − 4k³ + 5k² − 2k", True)


def test_preset_help_numbers_match_the_computation():
    h = C.PRESET_HELP
    std = ev.analyse(S(**C.PRESETS["Standardfall: Gitter 6×6"]))
    assert (std.m, std.states, std.monomials, std.trees, std.chromatic) == (60, 6001, 430, 32565539635200, 101596896)
    assert all(x in h["Standardfall: Gitter 6×6"] for x in ("60 Kanten", "2^60", "6.001", "430 Monomen", "32.565.539.635.200", "101.596.896"))
    pet = ev.analyse(S(**C.PRESETS["Petersen-Graph: Färbungen und Fluss"]))
    assert (pet.trees, pet.chromatic) == (2000, 332880) and all(x in h["Petersen-Graph: Färbungen und Fluss"] for x in ("2.000", "332.880", "240", "Z₅"))
    assert next(w for w in pet.ways if w["Größe"].startswith("Nirgends"))["Wert"] == "240"
    k5 = ev.analyse(S(**C.PRESETS["Vollständiger Graph K5"]))
    assert (k5.monomials, k5.chromatic, k5.acyclic) == (14, 0, 120) and all(x in h["Vollständiger Graph K5"] for x in ("P(4) = 0", "120", "14 Monomen"))
    g4 = ev.analyse(S(**C.PRESETS["Gitter 4×4: Färbungen und Zuverlässigkeit"]))
    assert A.chromatic_value(g4.T, g4.n, 1, 3) == 7812 and g4.chromatic == 6000732 and prob_equal(g4.reliability, "0,944085")
    assert all(x in h["Gitter 4×4: Färbungen und Zuverlässigkeit"] for x in ("7.812", "6.000.732", "0,9", "0,944085"))
    c6 = ev.analyse(S(**C.PRESETS["Kreis C6"]))
    assert (c6.trees, c6.chromatic) == (6, 66) and all(x in h["Kreis C6"] for x in ("sechs Spannbäume", "(k−1)⁶ + (k−1)", "66"))
    own = ev.analyse(S(**C.PRESETS["Eigene Kantenliste: Dreieck mit Anhang"]))
    assert (own.tutte_text, own.chromatic) == ("x³ + x² + xy", 12) and all(x in h["Eigene Kantenliste: Dreieck mit Anhang"] for x in ("x³ + x² + xy", "12 Färbungen"))


def prob_equal(r, text):
    return ev.prob_text(r) == text


def test_limits_table_numbers():
    assert A.catalan(8) == 1430 and C.SIDE_MAX == 7 and C.COMPLETE_CAP == 7 and (C.CUSTOM_MAX_VERTICES, C.CUSTOM_MAX_EDGES) == (9, 20)
    n3, n8 = A.frontier_tutte(24, A.grid_edges(3, 8))[1], A.frontier_tutte(24, A.grid_edges(8, 3))[1]
    assert (n3["total_states"], n8["total_states"], n3["frontier"], n8["frontier"]) == (17657, 171, 9, 4)


def test_readme_mentions_every_module_file():
    root = Path(__file__).resolve().parent.parent
    for f in root.glob("tpl_*.py"):
        assert f"`{f.name}`" in README, f.name
    assert "`app.py`" in README and "Stück 14 von 16" in README
