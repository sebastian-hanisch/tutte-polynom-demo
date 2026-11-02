"""Einheiten des Rechenkerns, jede an einer von Hand gerechneten Mini-Instanz."""

from fractions import Fraction

import pytest

import tpl_algorithm as A


def test_frontier_gives_the_hand_polynomials(triangle, square, k4, tiny):
    for g in (triangle, square, k4):
        T, info = A.frontier_tutte(g["n"], g["edges"])
        assert T == g["T"] and A.spanning_trees(T) == g["trees"] and A.acyclic_orientations(T) == g["acyclic"] and info["components"] == 1
    for n, edges, T in tiny.values():
        assert A.frontier_tutte(n, edges)[0] == T


def test_deletion_contraction_gives_the_same_polynomials(triangle, square, k4, tiny):
    for g in (triangle, square, k4):
        assert A.tutte_dc(g["edges"]) == g["T"] == A.tutte_dc(g["edges"], {}, {"calls": 0, "leaves": 0, "hits": 0})
    for n, edges, T in tiny.values():
        assert A.tutte_dc(edges) == T


def test_deletion_contraction_counts_its_leaves_as_spanning_trees(triangle, k4):
    for g in (triangle, k4):
        st = {"calls": 0, "leaves": 0, "hits": 0}
        A.tutte_dc(g["edges"], None, st)
        assert st["leaves"] == g["trees"]
    st = {"calls": 0, "leaves": 0, "hits": 0}
    A.tutte_dc(triangle["edges"], None, st)
    assert st["calls"] == 9   # Wurzel; Löschen: Weg mit zwei Kanten (Brücke, Brücke, Blatt) = 3 Aufrufe; Zusammenziehen: zwei parallele Kanten, Löschen (Brücke, Blatt) und Zusammenziehen (Schleife, Blatt) = 5 Aufrufe


def test_subsets_sum_matches_hand(triangle, square):
    assert A.tutte_subsets(triangle["n"], triangle["edges"]) == triangle["T"] and A.tutte_subsets(square["n"], square["edges"]) == square["T"]


def test_evaluations_of_the_triangle(triangle):
    T, n = triangle["T"], triangle["n"]
    assert A.spanning_forests(T) == 7 and A.connected_subgraphs(T) == 4 and A.all_subsets(T) == 8
    assert [A.chromatic_value(T, n, 1, k) for k in range(5)] == [0, 0, 0, 6, 24]
    assert A.chromatic_coefficients(T, n, 1) == triangle["coeffs"] and A.coefficient_text(triangle["coeffs"]) == "k³ − 3k² + 2k"
    assert A.reliability_value(T, n, 3, 1, Fraction(1, 3)) == Fraction(*triangle["R_third"])
    assert A.flow_value(T, n, 3, 1, 3) == triangle["flows_3"] and A.flow_value(T, n, 3, 1, 2) == 1 and A.flow_value(T, n, 3, 1, 5) == 4


def test_evaluations_of_square_and_k4(square, k4):
    assert A.chromatic_value(square["T"], 4, 1, 3) == square["P3"] and A.chromatic_value(square["T"], 4, 1, 2) == 2
    assert A.chromatic_value(k4["T"], 4, 1, 4) == k4["P4"] and A.chromatic_value(k4["T"], 4, 1, 3) == 0
    assert A.flow_value(k4["T"], 4, 6, 1, 4) == k4["F4"]
    assert A.coefficient_text(A.chromatic_coefficients(k4["T"], 4, 1)) == "k⁴ − 6k³ + 11k² − 6k"


def test_poly_text_and_padd_pmul():
    assert A.poly_text({(2, 0): 1, (1, 0): 1, (0, 1): 1}) == "x² + x + y" and A.poly_text({(1, 1): 4, (0, 2): 3}) == "4xy + 3y²" and A.poly_text({}) == "0"
    assert A.padd({(1, 0): 1}, {(1, 0): -1}) == {} and A.pmul({(1, 0): 1, (0, 1): 1}, {(1, 0): 1, (0, 1): -1}) == {(2, 0): 1, (0, 2): -1}
    assert A.shifted_power(2, 1) == {(2, 1): 1, (2, 0): -1, (1, 1): -2, (1, 0): 2, (0, 1): 1, (0, 0): -1}
    assert A.peval({(2, 0): 1, (1, 0): 1, (0, 1): 1}, 3, 5) == 17


def test_coefficient_text_signs():
    assert A.coefficient_text([0, -1, 1]) == "k² − k" and A.coefficient_text([-2, 0, 1]) == "k² − 2" and A.coefficient_text([0, 0, 0]) == "0" and A.coefficient_text([0, -3]) == "−3k"


def test_graph_builders():
    assert A.grid_edges(2, 2) == [(0, 1), (0, 2), (1, 3), (2, 3)] and A.grid_edges(2, 2, "spalte") == [(0, 2), (0, 1), (2, 3), (1, 3)]
    assert sorted(A.grid_edges(3, 4)) == sorted(A.grid_edges(3, 4, "spalte")) and len(A.grid_edges(6, 6)) == 60
    assert A.complete_graph(4)[1] == [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)] and A.cycle_graph(4) == (4, [(0, 1), (1, 2), (2, 3), (0, 3)])
    n, e = A.petersen_graph()
    assert n == 10 and len(e) == 15 and all(sum(v in edge for edge in e) == 3 for v in range(10))
    assert A.count_components(4, [(0, 1), (2, 3)]) == 2 and A.count_components(4, [(0, 1), (2, 3)], [0]) == 3


def test_parse_edge_list_hand():
    assert A.parse_edge_list("1-2, 2-3, 1-3") == (3, [(0, 1), (1, 2), (0, 2)])
    assert A.parse_edge_list("1-2;2-3 3-1") == (3, [(0, 1), (1, 2), (2, 0)]) and A.parse_edge_list("1–2") == (2, [(0, 1)])
    assert A.parse_edge_list("1-1, 1-2") == (2, [(0, 0), (0, 1)])


def test_kirchhoff_hand(triangle, k4):
    assert A.kirchhoff(3, triangle["edges"]) == 3 and A.kirchhoff(4, k4["edges"]) == 16 and A.kirchhoff(2, [(0, 1), (0, 1)]) == 2 and A.kirchhoff(1, []) == 1 and A.kirchhoff(3, [(0, 1)]) == 0


def test_brute_force_oracles_hand(triangle, square):
    assert [A.colorings_brute(3, triangle["edges"], k) for k in (1, 2, 3, 4)] == [0, 0, 6, 24] and A.colorings_brute(4, square["edges"], 3) == 18
    assert A.acyclic_orientations_brute(3, triangle["edges"]) == 6 and A.acyclic_orientations_brute(4, square["edges"]) == 14
    assert A.reliability_brute(3, triangle["edges"], Fraction(1, 3)) == Fraction(7, 27)
    assert A.flows_brute(3, triangle["edges"], 3) == 2 and A.flows_brute(3, triangle["edges"], 2) == 1
    assert A.grid_colorings(2, 2, 3) == 18 and A.grid_colorings(3, 3, 2) == 2 and A.grid_valid_rows(4, 6, 3) == 3 * 2 ** 3


def test_catalan_and_sample_helpers():
    assert [A.catalan(n) for n in range(8)] == [1, 1, 2, 5, 14, 42, 132, 429]
    assert A.sample_z(0.5, 0.5, 100) == 0 and A.sample_z(0.6, 0.5, 100) == pytest.approx(2.0) and A.sample_z(0.1, 1.0, 10) == 0.0
    assert A.reliability_sample(2, [(0, 1)], 1.0, 50, 1) == 1.0 and A.reliability_sample(2, [(0, 1)], 0.0, 50, 1) == 0.0


def test_reliability_value_rejects_degenerate_p(triangle):
    for p in (Fraction(0), Fraction(1)):
        with pytest.raises(ValueError):
            A.reliability_value(triangle["T"], 3, 3, 1, p)


def test_builders_reject_bad_sizes():
    for bad in (lambda: A.grid_edges(0, 3), lambda: A.grid_edges(2, 2, "zauber"), lambda: A.complete_graph(0), lambda: A.cycle_graph(2), lambda: A.frontier_tutte(0, [])):
        with pytest.raises(ValueError):
            bad()
