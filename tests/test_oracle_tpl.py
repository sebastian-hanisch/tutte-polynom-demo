"""Unabhängige Orakel: jede Zahl und jedes Polynom gegen einen zweiten Rechenweg (Teilmengensumme, Deletion–Contraction, Kirchhoff, Zählen, Aufzählen, Transfermatrix)."""

import random
from fractions import Fraction

import pytest

import tpl_algorithm as A


def random_multigraph(rng, max_n=6, max_m=10, loops=True, connected=False):
    n = rng.randint(1, max_n)
    m = rng.randint(0 if n == 1 else 1, max_m)
    edges = []
    for _ in range(m):
        a, b = rng.randrange(n), rng.randrange(n)
        if a == b and not loops:
            b = (a + 1) % n if n > 1 else a
        edges.append((a, b))
    if connected and A.count_components(n, edges) != 1:
        edges += [(i, i + 1) for i in range(n - 1)]
    return n, edges


def graphs(count=60, **kw):
    rng = random.Random(20261102)
    return [random_multigraph(rng, **kw) for _ in range(count)]


def test_frontier_equals_the_subset_sum_on_random_multigraphs():
    for n, edges in graphs(80):
        T, info = A.frontier_tutte(n, edges)
        assert T == A.tutte_subsets(n, edges), (n, edges)
        assert info["components"] == A.count_components(n, edges)


def test_deletion_contraction_equals_frontier_with_and_without_memo():
    for n, edges in graphs(60, max_m=9):
        T = A.frontier_tutte(n, edges)[0]
        assert A.tutte_dc(edges) == T and A.tutte_dc(edges, {}, {"calls": 0, "leaves": 0, "hits": 0}) == T, (n, edges)


def test_leaves_of_deletion_contraction_are_the_spanning_trees():
    for n, edges in graphs(40, max_m=9, connected=True):
        st = {"calls": 0, "leaves": 0, "hits": 0}
        A.tutte_dc(edges, None, st)
        assert st["leaves"] == A.kirchhoff(n, edges) == A.spanning_trees(A.tutte_subsets(n, edges)), (n, edges)


def test_spanning_trees_against_kirchhoff_for_connected_graphs():
    for n, edges in graphs(60, connected=True):
        assert A.spanning_trees(A.frontier_tutte(n, edges)[0]) == A.kirchhoff(n, edges)


def test_chromatic_values_against_counting_all_colorings():
    for n, edges in graphs(50, max_n=6, max_m=9):
        T, info = A.frontier_tutte(n, edges)
        for k in range(1, 5):
            assert A.chromatic_value(T, n, info["components"], k) == A.colorings_brute(n, edges, k), (n, edges, k)


def test_chromatic_coefficients_evaluate_to_the_same_values():
    for n, edges in graphs(40, max_n=6, max_m=9):
        T, info = A.frontier_tutte(n, edges)
        coeffs = A.chromatic_coefficients(T, n, info["components"])
        for k in range(0, 6):
            assert sum(c * k ** i for i, c in enumerate(coeffs)) == A.chromatic_value(T, n, info["components"], k)


def test_acyclic_orientations_against_enumeration():
    for n, edges in graphs(40, max_n=6, max_m=9):
        T = A.frontier_tutte(n, edges)[0]
        assert A.acyclic_orientations(T) == A.acyclic_orientations_brute(n, edges), (n, edges)


def test_stanley_identity_orientations_equal_the_absolute_value_of_p_minus_one():
    for n, edges in graphs(40, max_n=6, max_m=10):
        T, info = A.frontier_tutte(n, edges)
        assert A.acyclic_orientations(T) == abs(A.chromatic_value(T, n, info["components"], -1))


def test_flows_against_enumeration():
    for n, edges in graphs(40, max_n=5, max_m=7):
        T, info = A.frontier_tutte(n, edges)
        for k in (2, 3, 4):
            assert A.flow_value(T, n, len(edges), info["components"], k) == A.flows_brute(n, edges, k), (n, edges, k)


def test_reliability_against_enumeration_in_fractions():
    for n, edges in graphs(40, max_n=5, max_m=8, connected=True):
        T, info = A.frontier_tutte(n, edges)
        for p in (Fraction(1, 2), Fraction(1, 3), Fraction(9, 10)):
            assert A.reliability_value(T, n, len(edges), info["components"], p) == A.reliability_brute(n, edges, p), (n, edges, p)


def test_forests_and_connected_subgraphs_against_enumeration():
    for n, edges in graphs(30, max_n=5, max_m=8, connected=True):
        T = A.frontier_tutte(n, edges)[0]
        forests = connected = 0
        for mask in range(1 << len(edges)):
            subset = [i for i in range(len(edges)) if mask >> i & 1]
            comps = A.count_components(n, edges, subset)
            forests += len(subset) == n - comps
            connected += comps == 1
        assert A.spanning_forests(T) == forests and A.connected_subgraphs(T) == connected


@pytest.mark.parametrize("rows,cols", [(1, 3), (2, 2), (2, 3), (3, 3), (2, 5), (3, 4)])
def test_grid_polynomial_equals_the_subset_sum_in_both_orders(rows, cols):
    n = rows * cols
    base = A.frontier_tutte(n, A.grid_edges(rows, cols))[0]
    assert A.frontier_tutte(n, A.grid_edges(rows, cols, "spalte"))[0] == base
    if len(A.grid_edges(rows, cols)) <= 15:
        assert A.tutte_subsets(n, A.grid_edges(rows, cols)) == base


def test_grid_colorings_against_the_transfer_matrix():
    for rows, cols in ((2, 2), (2, 5), (3, 3), (3, 4), (4, 4), (5, 3)):
        n, e = A.grid_graph(rows, cols)
        T, info = A.frontier_tutte(n, e)
        for k in (2, 3, 4):
            assert A.chromatic_value(T, n, 1, k) == A.grid_colorings(rows, cols, k), (rows, cols, k)


def test_grid_spanning_trees_and_orientations_against_independent_values():
    n, e = A.grid_graph(4, 4)
    T = A.frontier_tutte(n, e)[0]
    assert A.spanning_trees(T) == A.kirchhoff(n, e) == 100352 and A.all_subsets(T) == 2 ** 24


def test_petersen_against_independent_values():
    n, e = A.petersen_graph()
    T, info = A.frontier_tutte(n, e)
    assert T == A.tutte_subsets(n, e) == A.tutte_dc(e, {})
    assert A.spanning_trees(T) == A.kirchhoff(n, e) == 2000
    assert A.chromatic_value(T, n, 1, 3) == A.colorings_brute(n, e, 3) == 120
    assert A.flow_value(T, n, 15, 1, 2) == A.flows_brute(n, e, 2) == 0 and A.flow_value(T, n, 15, 1, 3) == A.flows_brute(n, e, 3) == 0


def test_sampled_reliability_stays_inside_the_band_on_a_fixed_seed():
    n, e = A.grid_graph(4, 4)
    T, info = A.frontier_tutte(n, e)
    for p in (0.5, 0.9):
        exact = float(A.reliability_value(T, n, len(e), 1, Fraction(p).limit_denominator(100)))
        est = A.reliability_sample(n, e, p, 20000, 7)
        assert abs(A.sample_z(est, exact, 20000)) < 4
