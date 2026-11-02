"""Rechenkern: Tutte-Polynom durch Frontier-Rechnung im Polynom-Semiring, Deletion–Contraction, Auswertungen (Spannbäume, Färbungen, Flüsse, Orientierungen, Zuverlässigkeit) und unabhängige Prüfwege.

Ein Graph ist (n, edges) mit Knoten 0 bis n−1 und einer Liste von Kanten (a, b); Mehrfachkanten und Schleifen sind erlaubt. Polynome in zwei Veränderlichen sind Wörterbücher {(i, j): Koeffizient} für x^i y^j.
Alles mit `int` und `Fraction`."""

from __future__ import annotations

import itertools
import math
import random
import re
from fractions import Fraction

ORDERS = ("zeile", "spalte")


# ---------------------------------------------------------------- Graphen
def grid_edges(rows: int, cols: int, order: str = "zeile") -> list:
    """Kanten des rows×cols-Gitters (Knoten r·cols + c) in Zeilen- oder Spaltenordnung."""
    if rows < 1 or cols < 1:
        raise ValueError("Das Gitter braucht mindestens eine Zeile und eine Spalte.")
    right = lambda r, c: (r * cols + c, r * cols + c + 1)
    down = lambda r, c: (r * cols + c, (r + 1) * cols + c)
    if order == "zeile":
        return [e for r in range(rows) for c in range(cols) for e in ((right(r, c),) if c + 1 < cols else ()) + ((down(r, c),) if r + 1 < rows else ())]
    if order == "spalte":
        return [e for c in range(cols) for r in range(rows) for e in ((down(r, c),) if r + 1 < rows else ()) + ((right(r, c),) if c + 1 < cols else ())]
    raise ValueError(f"unbekannte Ordnung {order!r}")


def grid_graph(rows: int, cols: int, order: str = "zeile") -> tuple:
    return rows * cols, grid_edges(rows, cols, order)


def complete_graph(n: int) -> tuple:
    if n < 1:
        raise ValueError("Ein vollständiger Graph braucht mindestens einen Knoten.")
    return n, list(itertools.combinations(range(n), 2))


def cycle_graph(n: int) -> tuple:
    if n < 3:
        raise ValueError("Ein Kreis braucht mindestens drei Knoten.")
    return n, [(i, i + 1) for i in range(n - 1)] + [(0, n - 1)]


def petersen_graph() -> tuple:
    outer = [(i, (i + 1) % 5) for i in range(5)]
    spokes = [(i, i + 5) for i in range(5)]
    inner = [(5 + i, 5 + (i + 2) % 5) for i in range(5)]
    return 10, outer + spokes + inner


def count_components(n: int, edges, subset=None) -> int:
    """Zusammenhangskomponenten des Graphen (nur die Kanten aus `subset`, falls angegeben; Knoten ohne Kante zählen mit)."""
    parent = list(range(n))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    c = n
    for i in (range(len(edges)) if subset is None else subset):
        a, b = find(edges[i][0]), find(edges[i][1])
        if a != b:
            parent[a] = b
            c -= 1
    return c


def parse_edge_list(text: str, max_vertices: int = 9, max_edges: int = 20) -> tuple:
    """Kantenliste wie „1-2, 2-3, 1-3“ (Knoten 1 bis 9; Trennzeichen Komma, Semikolon oder Leerzeichen); gibt (n, Kanten mit Knoten ab 0) zurück. Wirft ValueError mit einer deutschen Meldung."""
    tokens = [t for t in re.split(r"[,;\s]+", text.strip()) if t]
    if not tokens:
        raise ValueError("Die Kantenliste ist leer: zum Beispiel 1-2, 2-3, 1-3.")
    edges = []
    for t in tokens:
        m = re.fullmatch(r"(\d+)\s*[-–]\s*(\d+)", t)
        if not m:
            raise ValueError(f"„{t[:20]}“ ist keine Kante: erwartet wird die Form 1-2.")
        a, b = int(m.group(1)), int(m.group(2))
        if not (1 <= a <= max_vertices and 1 <= b <= max_vertices):
            raise ValueError(f"Knoten müssen zwischen 1 und {max_vertices} liegen (gelesen: {a}-{b}).")
        edges.append((a - 1, b - 1))
    if len(edges) > max_edges:
        raise ValueError(f"Höchstens {max_edges} Kanten (gelesen: {len(edges)}).")
    n = max(max(e) for e in edges) + 1
    if count_components(n, edges) != 1:
        raise ValueError("Der Graph ist nicht zusammenhängend: jeder Knoten von 1 bis zum größten muss über Kanten erreichbar sein.")
    return n, edges


# ---------------------------------------------------------------- Polynome in zwei Veränderlichen
def padd(a: dict, b: dict) -> dict:
    out = dict(a)
    for k, v in b.items():
        out[k] = out.get(k, 0) + v
        if out[k] == 0:
            del out[k]
    return out


def pmul(a: dict, b: dict) -> dict:
    out: dict = {}
    for (i, j), v in a.items():
        for (k, l), w in b.items():
            out[(i + k, j + l)] = out.get((i + k, j + l), 0) + v * w
    return {k: v for k, v in out.items() if v}


def shifted_power(i: int, j: int) -> dict:
    """(x − 1)^i (y − 1)^j ausmultipliziert."""
    px = {(a, 0): math.comb(i, a) * (-1) ** (i - a) for a in range(i + 1)}
    py = {(0, b): math.comb(j, b) * (-1) ** (j - b) for b in range(j + 1)}
    return pmul(px, py)


def peval(p: dict, x, y):
    return sum(v * x ** i * y ** j for (i, j), v in p.items())


_SUP = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")


def _mono(var: str, e: int) -> str:
    return "" if e == 0 else var if e == 1 else var + str(e).translate(_SUP)


def poly_text(p: dict) -> str:
    """Tutte-Polynom als Text: x² + x + y."""
    if not p:
        return "0"
    parts = []
    for (i, j), v in sorted(p.items(), key=lambda t: (-(t[0][0] + t[0][1]), -t[0][0])):
        mon = _mono("x", i) + _mono("y", j)
        parts.append(mon if (v == 1 and mon) else f"{v}{mon}")
    return " + ".join(parts)


def tutte_from_counts(counts: dict, rank_total: int) -> dict:
    """T = Σ Zahl · (x−1)^(Rang(E) − k) (y−1)^e über {(k, e): Zahl der Teilmengen mit Rang k und Nullität e}."""
    out: dict = {}
    for (k, e), c in counts.items():
        out = padd(out, {m: c * v for m, v in shifted_power(rank_total - k, e).items()})
    return out


# ---------------------------------------------------------------- Frontier-Rechnung im Polynom-Semiring
def frontier_tutte(n: int, edges) -> tuple:
    """Kante für Kante; Zustand = Zusammenhangsklassen der Frontier-Knoten, Wert = {(Verschmelzungen k, Kreiskanten e): Zahl der Teilmengen}.
    Gibt (T, info) zurück; info: layers (Zustände nach jeder Kante), max_states, total_states, max_coeffs, frontier (größte Frontier)."""
    if n < 1:
        raise ValueError("Der Graph braucht mindestens einen Knoten.")
    last: dict = {}
    for i, (a, b) in enumerate(edges):
        last[a] = i
        last[b] = i
    first: dict = {}
    for i, (a, b) in enumerate(edges):
        first.setdefault(a, i)
        first.setdefault(b, i)
    states = {((), ()): {(0, 0): 1}}
    layers, max_coeffs, frontier = [], 1, 0
    for i, (a, b) in enumerate(edges):
        new: dict = {}
        for (front, lab), val in states.items():
            front, lab = list(front), list(lab)
            for v in (a, b):
                if v not in front:
                    front.append(v)
                    lab.append(max(lab, default=-1) + 1)
            order = sorted(range(len(front)), key=lambda t: front[t])
            front = [front[t] for t in order]
            lab = [lab[t] for t in order]
            frontier = max(frontier, len(front))
            la, lb = lab[front.index(a)], lab[front.index(b)]
            options = [(lab, 0, 0), ([la if x == lb else x for x in lab], 1, 0) if la != lb else (lab, 0, 1)]
            keep = [t for t in range(len(front)) if last[front[t]] > i]
            kf = tuple(front[t] for t in keep)
            for newlab, dk, de in options:
                remap: dict = {}
                canon = tuple(remap.setdefault(newlab[t], len(remap)) for t in keep)
                tgt = new.setdefault((kf, canon), {})
                for (k, e), c in val.items():
                    key = (k + dk, e + de)
                    tgt[key] = tgt.get(key, 0) + c
        states = new
        layers.append(len(states))
        max_coeffs = max(max_coeffs, max((len(v) for v in states.values()), default=1))
    counts: dict = {}
    for val in states.values():
        for k, c in val.items():
            counts[k] = counts.get(k, 0) + c
    comps = count_components(n, edges)
    T = tutte_from_counts(counts, n - comps)
    return T, {"layers": layers, "max_states": max(layers, default=1), "total_states": sum(layers) if layers else 1, "max_coeffs": max_coeffs, "frontier": frontier, "components": comps}


# ---------------------------------------------------------------- Deletion–Contraction
def _normalize(edges) -> tuple:
    verts = sorted({v for e in edges for v in e})
    idx = {v: i for i, v in enumerate(verts)}
    return tuple(sorted(tuple(sorted((idx[a], idx[b]))) for a, b in edges))


def _connected_without(edges, skip: int, u: int, v: int) -> bool:
    adj: dict = {}
    for i, (a, b) in enumerate(edges):
        if i != skip:
            adj.setdefault(a, []).append(b)
            adj.setdefault(b, []).append(a)
    seen, stack = {u}, [u]
    while stack:
        a = stack.pop()
        if a == v:
            return True
        for b in adj.get(a, ()):
            if b not in seen:
                seen.add(b)
                stack.append(b)
    return False


def tutte_dc(edges, memo: dict | None = None, stats: dict | None = None) -> dict:
    """Deletion–Contraction mit Schleifen- und Brückenregel. Mit `memo` werden gleiche Teilgraphen (nach Umbenennung der Knoten, ohne Isomorphietest) zusammengefasst.
    `stats` zählt "calls" (Aufrufe), "leaves" (Blätter ohne Kanten) und "hits" (Treffer im Speicher)."""
    edges = list(edges)
    if stats is not None:
        stats["calls"] += 1
    if not edges:
        if stats is not None:
            stats["leaves"] += 1
        return {(0, 0): 1}
    key = None
    if memo is not None:
        key = _normalize(edges)
        if key in memo:
            if stats is not None:
                stats["hits"] += 1
            return memo[key]
        edges = list(key)
    u, v = edges[0]
    rest = edges[1:]
    if u == v:
        res = pmul({(0, 1): 1}, tutte_dc(rest, memo, stats))
    else:
        contracted = [(u if a == v else a, u if b == v else b) for a, b in rest]
        if not _connected_without(edges, 0, u, v):
            res = pmul({(1, 0): 1}, tutte_dc(contracted, memo, stats))
        else:
            res = padd(tutte_dc(rest, memo, stats), tutte_dc(contracted, memo, stats))
    if memo is not None:
        memo[key] = res
    return res


# ---------------------------------------------------------------- Auswertungen des Tutte-Polynoms
def spanning_trees(T: dict) -> int:
    return peval(T, 1, 1)


def spanning_forests(T: dict) -> int:
    return peval(T, 2, 1)


def connected_subgraphs(T: dict) -> int:
    return peval(T, 1, 2)


def acyclic_orientations(T: dict) -> int:
    return peval(T, 2, 0)


def all_subsets(T: dict) -> int:
    return peval(T, 2, 2)


def chromatic_value(T: dict, n: int, comps: int, k: int):
    """P(G, k) = (−1)^(n−c) k^c T(1−k, 0)."""
    return (-1) ** (n - comps) * k ** comps * peval(T, 1 - k, 0)


def chromatic_coefficients(T: dict, n: int, comps: int) -> list:
    """Koeffizienten von P(G, k) in k, vom niedrigsten Grad an: P = (−1)^(n−c) k^c Σ a_i (1−k)^i mit T(x, 0) = Σ a_i x^i."""
    a: dict = {}
    for (i, j), v in T.items():
        if j == 0:
            a[i] = a.get(i, 0) + v
    deg = max(a, default=0)
    poly = [0] * (deg + 1)
    for i, v in a.items():
        for t in range(i + 1):
            poly[t] += v * math.comb(i, t) * (-1) ** t
    sign = (-1) ** (n - comps)
    return [0] * comps + [sign * c for c in poly]


def flow_value(T: dict, n: int, m: int, comps: int, k: int):
    """Zahl der nirgends verschwindenden Z_k-Flüsse: F(G, k) = (−1)^(m−n+c) T(0, 1−k)."""
    return (-1) ** (m - n + comps) * peval(T, 0, 1 - k)


def reliability_value(T: dict, n: int, m: int, comps: int, p: Fraction):
    """Wahrscheinlichkeit, dass der Graph verbunden bleibt (bleibt er so zusammenhängend wie ursprünglich), wenn jede Kante unabhängig mit Wahrscheinlichkeit p hält: p^(n−c) (1−p)^(m−n+c) T(1, 1/(1−p))."""
    if not (0 < p < 1):
        raise ValueError("p muss zwischen 0 und 1 liegen.")
    return p ** (n - comps) * (1 - p) ** (m - n + comps) * peval(T, Fraction(1), 1 / (1 - p))


def coefficient_text(coeffs: list) -> str:
    """P(k) als Text: k⁴ − 6k³ + 11k² − 6k."""
    parts = []
    for e in range(len(coeffs) - 1, -1, -1):
        c = coeffs[e]
        if c == 0:
            continue
        mon = _mono("k", e)
        mag = "" if (abs(c) == 1 and mon) else str(abs(c))
        parts.append((" − " if c < 0 else " + ") + mag + mon)
    if not parts:
        return "0"
    text = "".join(parts)
    return ("−" + text[3:]) if text.startswith(" − ") else text[3:]


def catalan(n: int) -> int:
    return math.comb(2 * n, n) // (n + 1)


# ---------------------------------------------------------------- unabhängige Prüfwege
def tutte_subsets(n: int, edges) -> dict:
    """Teilmengensumme nach Whitney über alle 2^m Kantenmengen (Union-Find je Menge)."""
    m = len(edges)
    comps = count_components(n, edges)
    counts: dict = {}
    for mask in range(1 << m):
        subset = [i for i in range(m) if mask >> i & 1]
        r = n - count_components(n, edges, subset)
        key = (r, len(subset) - r)
        counts[key] = counts.get(key, 0) + 1
    return tutte_from_counts(counts, n - comps)


def kirchhoff(n: int, edges) -> int:
    """Zahl der Spannbäume als Hauptunterdeterminante der Laplace-Matrix, in Brüchen (Schleifen zählen nicht, Mehrfachkanten mehrfach)."""
    if n == 1:
        return 1
    L = [[Fraction(0)] * n for _ in range(n)]
    for a, b in edges:
        if a != b:
            L[a][a] += 1
            L[b][b] += 1
            L[a][b] -= 1
            L[b][a] -= 1
    M = [row[1:] for row in L[1:]]
    size, det = n - 1, Fraction(1)
    for c in range(size):
        pivot = next((r for r in range(c, size) if M[r][c] != 0), None)
        if pivot is None:
            return 0
        if pivot != c:
            M[c], M[pivot] = M[pivot], M[c]
            det = -det
        det *= M[c][c]
        for r in range(c + 1, size):
            f = M[r][c] / M[c][c]
            for k in range(c, size):
                M[r][k] -= f * M[c][k]
    return int(det)


def colorings_brute(n: int, edges, k: int) -> int:
    return sum(all(col[a] != col[b] for a, b in edges) for col in itertools.product(range(k), repeat=n))


def grid_colorings(rows: int, cols: int, k: int) -> int:
    """Färbungen des Gitters durch Zeilen-Transfermatrix (unabhängig vom Tutte-Polynom)."""
    if rows > cols:
        rows, cols = cols, rows
    valid = [r for r in itertools.product(range(k), repeat=cols) if all(r[i] != r[i + 1] for i in range(cols - 1))]
    vec = {r: 1 for r in valid}
    for _ in range(rows - 1):
        vec = {r2: sum(c for r1, c in vec.items() if all(a != b for a, b in zip(r1, r2))) for r2 in valid}
    return sum(vec.values())


def grid_valid_rows(rows: int, cols: int, k: int) -> int:
    """Zahl der Zeilenfärbungen, die die Transfermatrix durchlaufen muss (k (k−1)^(Breite−1), Breite = kürzere Seite)."""
    w = min(rows, cols)
    return k * (k - 1) ** (w - 1) if k >= 1 else 0


def acyclic_orientations_brute(n: int, edges) -> int:
    count = 0
    for mask in range(1 << len(edges)):
        adj = [[] for _ in range(n)]
        indeg = [0] * n
        for i, (a, b) in enumerate(edges):
            u, v = (a, b) if mask >> i & 1 else (b, a)
            adj[u].append(v)
            indeg[v] += 1
        stack = [v for v in range(n) if indeg[v] == 0]
        seen = 0
        while stack:
            v = stack.pop()
            seen += 1
            for w in adj[v]:
                indeg[w] -= 1
                if indeg[w] == 0:
                    stack.append(w)
        count += seen == n
    return count


def reliability_brute(n: int, edges, p: Fraction) -> Fraction:
    comps = count_components(n, edges)
    total = Fraction(0)
    for mask in range(1 << len(edges)):
        subset = [i for i in range(len(edges)) if mask >> i & 1]
        if count_components(n, edges, subset) == comps:
            total += p ** len(subset) * (1 - p) ** (len(edges) - len(subset))
    return total


def reliability_sample(n: int, edges, p: float, draws: int, seed: int) -> float:
    """Anteil der Ziehungen, in denen der Graph verbunden bleibt (Union-Find je Ziehung)."""
    rng = random.Random(seed)
    comps0 = count_components(n, edges)
    ok = 0
    for _ in range(draws):
        parent = list(range(n))

        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a

        c = n
        for a, b in edges:
            if rng.random() < p:
                x, y = find(a), find(b)
                if x != y:
                    parent[x] = y
                    c -= 1
        ok += c == comps0
    return ok / draws


def flows_brute(n: int, edges, k: int) -> int:
    """Nirgends verschwindende Z_k-Flüsse durch Aufzählen aller Zuweisungen 1 bis k−1 an die Kanten (Erhaltung modulo k an jedem Knoten); Kanten in der gegebenen Richtung a → b."""
    count = 0
    for vals in itertools.product(range(1, k), repeat=len(edges)):
        net = [0] * n
        for (a, b), v in zip(edges, vals):
            net[a] = (net[a] + v) % k
            net[b] = (net[b] - v) % k
        count += not any(net)
    return count


def sample_z(estimate: float, exact: float, draws: int) -> float:
    sd = (exact * (1 - exact) / draws) ** 0.5
    return (estimate - exact) / sd if sd > 0 else 0.0
