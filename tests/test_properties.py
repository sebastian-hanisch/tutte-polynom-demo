"""Eigenschaften (Schicht 2): Gesetze, die für alle Graphen gelten müssen, unabhängig von einzelnen Zahlen."""

import math
import random
from fractions import Fraction

import pytest

import tpl_algorithm as A
from test_oracle_tpl import graphs


def T_of(n, edges):
    return A.frontier_tutte(n, edges)[0]


def disjoint_union(g1, g2):
    (n1, e1), (n2, e2) = g1, g2
    return n1 + n2, e1 + [(a + n1, b + n1) for a, b in e2]


def test_all_coefficients_are_nonnegative_integers():
    for n, edges in graphs(80):
        assert all(isinstance(v, int) and v > 0 for v in T_of(n, edges).values())


def test_t_at_two_two_is_two_to_the_m_and_t_at_one_one_is_the_leaf_count():
    for n, edges in graphs(60, connected=True):
        T = T_of(n, edges)
        assert A.all_subsets(T) == 2 ** len(edges) and A.spanning_trees(T) == A.kirchhoff(n, edges)


def test_the_polynomial_does_not_depend_on_the_edge_order():
    rng = random.Random(5)
    for n, edges in graphs(40, max_m=9):
        shuffled = list(edges)
        rng.shuffle(shuffled)
        assert T_of(n, shuffled) == T_of(n, edges)


def test_the_polynomial_does_not_depend_on_the_vertex_names():
    rng = random.Random(6)
    for n, edges in graphs(40, max_m=9):
        perm = list(range(n))
        rng.shuffle(perm)
        assert T_of(n, [(perm[a], perm[b]) for a, b in edges]) == T_of(n, edges)


def test_transposed_grids_have_the_same_polynomial():
    for rows, cols in ((2, 5), (3, 4), (2, 7), (3, 5)):
        assert T_of(*A.grid_graph(rows, cols)) == T_of(*A.grid_graph(cols, rows))


def test_polynomial_of_a_disjoint_union_is_the_product():
    tri, sq = A.complete_graph(3), A.cycle_graph(4)
    assert T_of(*disjoint_union(tri, sq)) == A.pmul(T_of(*tri), T_of(*sq))
    assert T_of(*disjoint_union(tri, tri)) == A.pmul(T_of(*tri), T_of(*tri))


def test_polynomial_of_a_one_point_union_is_the_product():
    n1, e1 = A.complete_graph(3)
    n2, e2 = A.cycle_graph(4)
    glued = n1 + n2 - 1, e1 + [(0 if a == 0 else a + n1 - 1, 0 if b == 0 else b + n1 - 1) for a, b in e2]
    assert T_of(*glued) == A.pmul(T_of(n1, e1), T_of(n2, e2))


def test_trees_and_cycles_and_complete_graphs_have_closed_forms():
    for n in range(2, 8):
        path = (n, [(i, i + 1) for i in range(n - 1)])
        T = T_of(*path)
        assert T == {(n - 1, 0): 1} and [A.chromatic_value(T, n, 1, k) for k in range(5)] == [k * (k - 1) ** (n - 1) for k in range(5)]
    for n in range(3, 9):
        T = T_of(*A.cycle_graph(n))
        assert T == {**{(i, 0): 1 for i in range(1, n)}, (0, 1): 1}
        assert [A.chromatic_value(T, n, 1, k) for k in range(6)] == [(k - 1) ** n + (-1) ** n * (k - 1) for k in range(6)]
    for n in range(2, 7):
        T = T_of(*A.complete_graph(n))
        assert A.spanning_trees(T) == n ** (n - 2) and A.acyclic_orientations(T) == math.factorial(n)
        assert [A.chromatic_value(T, n, 1, k) for k in range(8)] == [math.prod(range(k, k - n, -1)) if k >= n else 0 for k in range(8)]


def test_chromatic_polynomial_basics_for_simple_graphs():
    for n, edges in graphs(60, max_n=7, max_m=10, loops=False, connected=True):
        simple = sorted({tuple(sorted(e)) for e in edges if e[0] != e[1]})
        T, info = A.frontier_tutte(n, simple)
        coeffs = A.chromatic_coefficients(T, n, info["components"])
        assert coeffs[0] == 0 and coeffs[n] == 1 and len(coeffs) == n + 1
        assert coeffs[n - 1] == -len(simple)
        assert (sum(coeffs) == 0) == bool(simple) and all(c == 0 or (c > 0) == ((n - i) % 2 == 0) for i, c in enumerate(coeffs))   # Vorzeichen wechseln (Whitney), P(1) = 0 bei mindestens einer Kante


def test_flow_polynomial_of_k4_and_of_cycles():
    T = T_of(*A.complete_graph(4))
    assert [A.flow_value(T, 4, 6, 1, k) for k in range(2, 7)] == [(k - 1) * (k - 2) * (k - 3) for k in range(2, 7)]
    for n in range(3, 8):
        assert [A.flow_value(T_of(*A.cycle_graph(n)), n, n, 1, k) for k in range(2, 6)] == [k - 1 for k in range(2, 6)]


def test_reliability_properties():
    for n, edges in graphs(30, max_n=6, max_m=9, connected=True):
        T = T_of(n, edges)
        values = [A.reliability_value(T, n, len(edges), 1, Fraction(i, 20)) for i in range(1, 20)]
        assert all(0 < v < 1 for v in values) or n == 1
        assert values == sorted(values)
    path = (5, [(i, i + 1) for i in range(4)])
    assert A.reliability_value(T_of(*path), 5, 4, 1, Fraction(7, 10)) == Fraction(7, 10) ** 4
    assert A.reliability_value(T_of(*A.cycle_graph(5)), 5, 5, 1, Fraction(1, 2)) == Fraction(6, 32)   # alle fünf oder genau vier Kanten: (1 + 5) / 32


def test_states_per_layer_are_bounded_by_the_bell_number_of_the_frontier():
    def bell(n):
        row = [1]
        for _ in range(n):
            nxt = [row[-1]]
            for x in row:
                nxt.append(nxt[-1] + x)
            row = nxt
        return row[0]

    for rows, cols in ((3, 3), (4, 4), (3, 6)):
        T, info = A.frontier_tutte(rows * cols, A.grid_edges(rows, cols))
        assert info["max_states"] <= bell(info["frontier"])
    for n in (4, 5, 6):
        T, info = A.frontier_tutte(n, A.complete_graph(n)[1])
        assert info["max_states"] <= bell(n)


def test_largest_layer_of_square_grids_is_the_catalan_number():
    for n in range(2, 7):
        T, info = A.frontier_tutte(n * n, A.grid_edges(n, n))
        assert info["max_states"] == A.catalan(n), n


def test_frontier_states_equal_the_known_spanning_tree_diagram_sizes():
    sums = {n: A.frontier_tutte(n * n, A.grid_edges(n, n))[1]["total_states"] for n in (3, 4, 5, 6)}
    assert sums == {3: 46, 4: 251, 5: 1259, 6: 6001}


def test_the_order_changes_the_size_but_not_the_polynomial():
    narrow = A.frontier_tutte(24, A.grid_edges(8, 3))
    wide = A.frontier_tutte(24, A.grid_edges(3, 8))
    assert narrow[0] == wide[0] and narrow[1]["frontier"] == 4 and wide[1]["frontier"] == 9 and wide[1]["total_states"] > 50 * narrow[1]["total_states"]


def test_memoized_recursion_never_needs_more_calls_than_the_plain_one():
    for rows, cols in ((2, 3), (3, 3), (3, 4)):
        e = A.grid_edges(rows, cols)
        plain = {"calls": 0, "leaves": 0, "hits": 0}
        memo = {"calls": 0, "leaves": 0, "hits": 0}
        A.tutte_dc(e, None, plain)
        A.tutte_dc(e, {}, memo)
        assert memo["calls"] < plain["calls"] and memo["hits"] > 0


def test_pmul_is_commutative_and_padd_is_associative_on_random_polynomials():
    rng = random.Random(9)
    polys = [{(rng.randint(0, 3), rng.randint(0, 3)): rng.randint(-3, 3) for _ in range(4)} for _ in range(6)]
    polys = [{k: v for k, v in p.items() if v} for p in polys]
    a, b, c = polys[:3]
    assert A.pmul(a, b) == A.pmul(b, a) and A.padd(A.padd(a, b), c) == A.padd(a, A.padd(b, c))
    assert A.peval(A.pmul(a, b), 2, 3) == A.peval(a, 2, 3) * A.peval(b, 2, 3)
