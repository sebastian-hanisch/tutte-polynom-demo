"""Auswertung: der eingestellte Graph mit Tutte-Polynom, Prüfwegen und Urteilstext, fünf Experimente, die Spielwiese. Gewichte gibt es nicht; nur das Zufallsziehen der Zuverlässigkeit nutzt einen festen Seed."""

import functools
import math
from dataclasses import dataclass
from fractions import Fraction

import tpl_algorithm as A
import tpl_constants as C

_SUPER = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")
STUECK13_TREE_STATES = {3: 46, 4: 251, 5: 1259, 6: 6001, 7: 27645}   # Summe der Zustände der Spannbaum-Diagramme in Stück 13 (frontier-diagramm-demo), nicht neu gerechnet


@dataclass(frozen=True)
class Settings:
    graph: str
    rows: int
    cols: int
    n: int
    order: str
    k: int
    p: int
    edges: str


@dataclass
class Analysis:
    settings: Settings
    label: str
    n: int
    m: int
    comps: int
    order_key: str
    frontier: int
    layers: list
    states: int
    max_layer: int
    monomials: int
    T: dict
    tutte_text: str | None
    chromatic_text: str | None
    k: int
    p: Fraction
    trees: int
    chromatic: int
    acyclic: int
    reliability: Fraction
    ways: list
    problems: list
    notes: list


# ----------------------------------------------------------------------------- Formatierung
def de(x: float, digits: int = 2) -> str:
    return f"{x:.{digits}f}".replace(".", ",").replace("-", "−")


def big_text(x: int) -> str:
    """Ganze Zahl lesbar: bis 15 Stellen mit Tausenderpunkt, darüber Mantisse mal Zehnerpotenz mit Stellenzahl (ohne Stringumwandlung der ganzen Zahl)."""
    if x < 0:
        return "−" + big_text(-x)
    if x < 10 ** 15:
        return f"{x:,}".replace(",", ".")
    d = len(str(x)) if x < 10 ** 4000 else int(math.log10(x)) + 1
    s = str(x // 10 ** (d - 3))
    return f"{s[0]},{s[1:3]}·10{str(d - 1).translate(_SUPER)} ({d} Stellen)"


def plural(n: int, one: str, many: str) -> str:
    return f"{big_text(n)} {one if n == 1 else many}"


def prob_text(r: Fraction) -> str:
    """Wahrscheinlichkeit als Dezimalzahl mit sechs Stellen; sehr kleine Werte als Zehnerpotenz."""
    x = float(r)
    if x == 0:
        return "0"
    if x < 1e-4:
        mant, exp = f"{x:.2e}".split("e")
        return f"{mant.replace('.', ',')}·10{str(int(exp)).translate(_SUPER)}"
    return de(x, 6)


def factor_text(x: float) -> str:
    if x < 10:
        return de(x, 2)
    if x < 1000:
        return de(x, 1)
    return f"{round(x):,}".replace(",", ".")


# ----------------------------------------------------------------------------- Eingaben
def effective_graph(s: Settings) -> tuple:
    """(Bezeichnung, n, Kanten, Schlüssel der Kantenordnung, Hinweise) für die Einstellung."""
    if s.graph not in C.GRAPHS:
        raise ValueError(f"unbekannter Graph {s.graph!r}")
    if s.order not in C.ORDER_KEYS:
        raise ValueError(f"unbekannte Ordnung {s.order!r}")
    notes: list = []
    order_key = C.ORDER_KEYS[s.order]
    if s.graph == "Gitter":
        rows = max(C.SIDE_MIN, min(s.rows, C.SIDE_MAX))
        cols = max(C.SIDE_MIN, min(s.cols, C.SIDE_MAX))
        if rows * cols < 2:
            cols = 2
            notes.append("Ein Gitter braucht mindestens zwei Knoten: gerechnet wird mit 1×2.")
        n, edges = A.grid_graph(rows, cols, order_key)
        return f"Gitter {rows}×{cols}", n, edges, order_key, notes
    if s.graph == "Petersen-Graph":
        n, edges = A.petersen_graph()
        return "Petersen-Graph", n, edges, "fest", notes
    if s.graph == "Vollständiger Graph":
        size = max(2, min(s.n, C.COMPLETE_CAP))
        if size != s.n:
            notes.append(f"Vollständige Graphen gibt es hier bis K{C.COMPLETE_CAP}: gerechnet wird mit K{size}.")
        n, edges = A.complete_graph(size)
        return f"K{size}", n, edges, "fest", notes
    if s.graph == "Kreis":
        size = max(C.CYCLE_MIN, s.n)
        if size != s.n:
            notes.append(f"Ein Kreis braucht mindestens {C.CYCLE_MIN} Knoten: gerechnet wird mit C{size}.")
        n, edges = A.cycle_graph(size)
        return f"Kreis C{size}", n, edges, "fest", notes
    try:
        n, edges = A.parse_edge_list(s.edges, C.CUSTOM_MAX_VERTICES, C.CUSTOM_MAX_EDGES)
        label = "Eigener Graph"
    except ValueError as err:
        notes.append(f"Die Kantenliste ist nicht brauchbar ({err}) Gerechnet wird mit {C.DEFAULT_EDGES}.")
        n, edges = A.parse_edge_list(C.DEFAULT_EDGES)
        label = "Eigener Graph (Ersatzliste)"
    return label, n, edges, "liste", notes


# ----------------------------------------------------------------------------- die eingestellte Aufgabe
def _row(size, value, way="", check_value="", check=""):
    return {"Größe": size, "Wert": value, "Prüfweg": way, "Prüfwert": check_value, "Prüfung": check}


def _cmp(a, b):
    return "gleich" if a == b else "weicht ab"


def check_chromatic(n: int, edges, label: str, k: int, value: int, T: dict, comps: int):
    """(Prüfweg, Prüfwert, Prüfung) für P(G, k) mit dem ersten passenden unabhängigen Weg."""
    if k ** n <= C.COLORING_BRUTE_LIMIT:
        b = A.colorings_brute(n, edges, k)
        return "Zählen aller Färbungen", big_text(b), _cmp(b, value)
    if label.startswith("Gitter"):
        r, c = (int(x) for x in label.split(" ")[1].split("×"))
        if A.grid_valid_rows(r, c, k) <= C.TRANSFER_ROWS_LIMIT:
            g = A.grid_colorings(r, c, k)
            return "Zeilen-Transfermatrix", big_text(g), _cmp(g, value)
    if label == "Petersen-Graph" and k in C.PETERSEN_COLORINGS:
        return "Stück 12 (Zählen und Burnside)", big_text(C.PETERSEN_COLORINGS[k]), _cmp(C.PETERSEN_COLORINGS[k], value)
    return "–", "–", f"nur bis {big_text(C.COLORING_BRUTE_LIMIT)} Zuordnungen (k hoch n) oder Gitter mit wenigen Zeilenfärbungen"


def analyse(s: Settings) -> Analysis:
    label, n, edges, order_key, notes = effective_graph(s)
    m = len(edges)
    k = max(C.K_MIN, min(s.k, C.K_MAX))
    pp = max(C.P_MIN, min(s.p, C.P_MAX))
    p = Fraction(pp, 100)
    T, info = A.frontier_tutte(n, edges)
    comps = info["components"]
    problems: list = []
    ways: list = []

    trees = A.spanning_trees(T)
    kt = A.kirchhoff(n, edges)
    ways.append(_row("Spannbäume T(1,1)", big_text(trees), "Kirchhoff (Determinante der Laplace-Matrix)", big_text(kt), _cmp(kt, trees)))
    if kt != trees:
        problems.append("Spannbäume weichen von Kirchhoff ab")

    P = A.chromatic_value(T, n, comps, k)
    way, val, chk = check_chromatic(n, edges, label, k, P, T, comps)
    ways.append(_row(f"Färbungen mit {k} {'Farbe' if k == 1 else 'Farben'}: P({k})", big_text(P), way, val, chk))
    if chk == "weicht ab":
        problems.append("Färbungen weichen vom Prüfweg ab")

    acyc = A.acyclic_orientations(T)
    if m <= C.ORIENTATION_EDGE_LIMIT:
        ao = A.acyclic_orientations_brute(n, edges)
        ways.append(_row("Azyklische Orientierungen T(2,0)", big_text(acyc), "Aufzählen aller 2^m Orientierungen", big_text(ao), _cmp(ao, acyc)))
        if ao != acyc:
            problems.append("Orientierungen weichen vom Aufzählen ab")
    else:
        st = abs(A.chromatic_value(T, n, comps, -1))
        ways.append(_row("Azyklische Orientierungen T(2,0)", big_text(acyc), "Stanley: |P(−1)| (ein anderer Auswertungspunkt desselben Polynoms)", big_text(st), _cmp(st, acyc)))
        if st != acyc:
            problems.append("Orientierungen weichen von |P(−1)| ab")

    subset_T = A.tutte_subsets(n, edges) if m <= C.SUBSETS_EDGE_LIMIT else None
    for name, value in (("Wälder T(2,1)", A.spanning_forests(T)), ("Zusammenhängende Teilgraphen T(1,2)", A.connected_subgraphs(T))):
        if subset_T is not None:
            x, y = (2, 1) if "2,1" in name else (1, 2)
            c = A.peval(subset_T, x, y)
            ways.append(_row(name, big_text(value), "Teilmengensumme (alle 2^m Kantenmengen)", big_text(c), _cmp(c, value)))
            if c != value:
                problems.append(f"{name.split(' T')[0]} weichen von der Teilmengensumme ab")
        else:
            ways.append(_row(name, big_text(value), "Teilmengensumme", "–", f"nur bis {C.SUBSETS_EDGE_LIMIT} Kanten"))
    ways.append(_row("Alle Kantenmengen T(2,2)", big_text(A.all_subsets(T)), "2^m", big_text(2 ** m), _cmp(2 ** m, A.all_subsets(T))))
    if A.all_subsets(T) != 2 ** m:
        problems.append("T(2,2) ist nicht 2^m")

    if subset_T is not None:
        ways.append(_row("Ganzes Polynom", f"{len(T)} Monome", "Teilmengensumme", f"{len(subset_T)} Monome", _cmp(subset_T, T)))
        if subset_T != T:
            problems.append("Polynom weicht von der Teilmengensumme ab")
    if m <= C.DC_EDGE_LIMIT:
        dc = A.tutte_dc(edges, {}, {"calls": 0, "leaves": 0, "hits": 0})
        ways.append(_row("Ganzes Polynom", f"{len(T)} Monome", "Deletion–Contraction mit Zusammenfassen", f"{len(dc)} Monome", _cmp(dc, T)))
        if dc != T:
            problems.append("Polynom weicht von Deletion–Contraction ab")

    F = A.flow_value(T, n, m, comps, k)
    if (k - 1) ** m <= C.FLOW_BRUTE_LIMIT:
        fb = A.flows_brute(n, edges, k)
        ways.append(_row(f"Nirgends verschwindende Flüsse mit Werten aus Z{k}: F({k})", big_text(F), "Aufzählen aller Zuweisungen", big_text(fb), _cmp(fb, F)))
        if fb != F:
            problems.append("Flüsse weichen vom Aufzählen ab")
    elif label == "Petersen-Graph" and k == 5:
        ways.append(_row("Nirgends verschwindende Flüsse mit Werten aus Z5: F(5)", big_text(F), "aus dem Gedächtnis (Flusspolynom des Petersen-Graphen)", big_text(C.PETERSEN_FLOW_5), _cmp(C.PETERSEN_FLOW_5, F)))
        if F != C.PETERSEN_FLOW_5:
            problems.append("Fluss weicht vom Literaturwert ab")
    else:
        ways.append(_row(f"Nirgends verschwindende Flüsse mit Werten aus Z{k}: F({k})", big_text(F), "Aufzählen", "–", f"nur bis {big_text(C.FLOW_BRUTE_LIMIT)} Zuweisungen"))

    R = A.reliability_value(T, n, m, comps, p)
    if m <= C.ORIENTATION_EDGE_LIMIT:
        rb = A.reliability_brute(n, edges, p)
        ways.append(_row(f"Zuverlässigkeit bei p = {de(float(p), 2)}", prob_text(R), "Aufzählen aller 2^m Kantenzustände (Brüche)", prob_text(rb), _cmp(rb, R)))
        if rb != R:
            problems.append("Zuverlässigkeit weicht vom Aufzählen ab")
    else:
        est = A.reliability_sample(n, edges, float(p), C.SAMPLE_DRAWS, C.SAMPLE_SEED)
        z = A.sample_z(est, float(R), C.SAMPLE_DRAWS)
        ok = abs(z) <= 4
        ways.append(_row(f"Zuverlässigkeit bei p = {de(float(p), 2)}", prob_text(R), f"Zufallsziehen ({big_text(C.SAMPLE_DRAWS)} Ziehungen, fester Seed)", de(est, 5), f"z = {de(z, 2)}" if ok else f"weicht ab (z = {de(z, 2)})"))
        if not ok:
            problems.append("Zuverlässigkeit weicht vom Zufallsziehen ab")

    mono = len(T)
    coeffs = A.chromatic_coefficients(T, n, comps)
    return Analysis(s, label, n, m, comps, order_key, info["frontier"], info["layers"], info["total_states"], info["max_states"], mono, T,
                    A.poly_text(T) if mono <= 40 else None, A.coefficient_text(coeffs) if len(coeffs) <= 13 else None, k, p, trees, P, acyc, R, ways, problems, notes)


def verdict_answers(a: Analysis):
    if a.problems:
        return "error", "Die Rechenwege widersprechen sich: " + "; ".join(a.problems)
    order = {"zeile": "Zeile", "spalte": "Spalte", "liste": "wie in der Liste", "fest": "vorgegeben"}[a.order_key]
    text = (f"{a.label}: {a.n} Knoten, {a.m} {'Kante' if a.m == 1 else 'Kanten'}. Die Frontier-Rechnung (Kantenordnung: {order}, Frontier {a.frontier}) braucht {plural(a.states, 'Zustand', 'Zustände')} (größte Schicht {big_text(a.max_layer)}) "
            f"statt der {big_text(2 ** a.m)} Kantenmengen und liefert ein Tutte-Polynom mit {plural(a.monomials, 'Monom', 'Monomen')}. Daraus: {plural(a.trees, 'Spannbaum', 'Spannbäume')}, "
            f"{plural(a.chromatic, 'Färbung', 'Färbungen')} mit {plural(a.k, 'Farbe', 'Farben')}, {plural(a.acyclic, 'azyklische Orientierung', 'azyklische Orientierungen')}; "
            f"hält jede Kante mit Wahrscheinlichkeit {de(float(a.p), 2)}, bleibt der Graph mit Wahrscheinlichkeit {prob_text(a.reliability)} zusammenhängend. Alle Prüfwege stimmen überein.")
    return "success", text


# ----------------------------------------------------------------------------- Experiment 1: Deletion–Contraction
@functools.cache
def dc_rows() -> list:
    rows = []
    for grids, plain in ((C.EXP_DC_PLAIN, True), (C.EXP_DC_MEMO_ONLY, False)):
        for r, c in grids:
            n, e = A.grid_graph(r, c)
            trees = A.kirchhoff(n, e)
            row = {"Gitter": f"{r}×{c}", "Kanten": len(e), "Mengen": 2 ** len(e), "Spannbäume": trees, "Aufrufe": None, "Blätter": None}
            if plain:
                st = {"calls": 0, "leaves": 0, "hits": 0}
                A.tutte_dc(e, None, st)
                row["Aufrufe"], row["Blätter"] = st["calls"], st["leaves"]
            st2 = {"calls": 0, "leaves": 0, "hits": 0}
            T_memo = A.tutte_dc(e, {}, st2)
            T_front, info = A.frontier_tutte(n, e)
            row.update({"Aufrufe mit Zusammenfassen": st2["calls"], "Treffer": st2["hits"], "Frontier-Zustände": info["total_states"], "gleich": T_memo == T_front})
            rows.append(row)
    return rows


def verdict_dc(rows: list):
    ok = all(r["gleich"] and (r["Blätter"] is None or r["Blätter"] == r["Spannbäume"]) for r in rows)
    big = next(r for r in rows if r["Gitter"] == "5×5")
    four = next(r for r in rows if r["Gitter"] == "4×4")
    return ("success" if ok else "error"), (f"Deletion–Contraction hat genau so viele Blätter wie der Graph Spannbäume (bei allen {sum(1 for r in rows if r['Blätter'] is not None)} gerechneten Gittern gleich; 4×4: {big_text(four['Blätter'])} Blätter in {big_text(four['Aufrufe'])} Aufrufen, "
                                            f"nicht {big_text(four['Mengen'])} Kantenmengen). Fasst man gleiche Teilgraphen zusammen, braucht das 5×5-Gitter {big_text(big['Aufrufe mit Zusammenfassen'])} Aufrufe statt {big_text(big['Spannbäume'])} Blättern; "
                                            f"die Frontier-Rechnung kommt mit {big_text(big['Frontier-Zustände'])} Zuständen aus, und Deletion–Contraction mit Zusammenfassen und die Frontier-Rechnung liefern dasselbe Polynom.")


# ----------------------------------------------------------------------------- Experiment 2: ein Polynom, viele Zahlen
def named_graph(name: str) -> tuple:
    """(n, Kanten, Bezeichnung) für die Namen aus EXP_VALUE_GRAPHS."""
    if name == "Dreieck":
        n, e = A.complete_graph(3)
    elif name.startswith("Kreis C"):
        n, e = A.cycle_graph(int(name[7:]))
    elif name.startswith("K"):
        n, e = A.complete_graph(int(name[1:]))
    elif name == "Petersen-Graph":
        n, e = A.petersen_graph()
    elif name.startswith("Gitter "):
        r, c = (int(x) for x in name.split(" ")[1].split("×"))
        n, e = A.grid_graph(r, c)
    else:
        raise ValueError(name)
    return n, e, name


def _settings_for(name: str, k: int = 3, p: int = 90) -> Settings:
    if name == "Dreieck":
        return Settings("Vollständiger Graph", 6, 6, 3, "Zeile", k, p, C.DEFAULT_EDGES)
    if name.startswith("Kreis C"):
        return Settings("Kreis", 6, 6, int(name[7:]), "Zeile", k, p, C.DEFAULT_EDGES)
    if name.startswith("K"):
        return Settings("Vollständiger Graph", 6, 6, int(name[1:]), "Zeile", k, p, C.DEFAULT_EDGES)
    if name == "Petersen-Graph":
        return Settings("Petersen-Graph", 6, 6, 5, "Zeile", k, p, C.DEFAULT_EDGES)
    r, c = (int(x) for x in name.split(" ")[1].split("×"))
    return Settings("Gitter", r, c, 5, "Zeile", k, p, C.DEFAULT_EDGES)


@functools.cache
def value_rows() -> list:
    rows = []
    for name in C.EXP_VALUE_GRAPHS:
        a = analyse(_settings_for(name))
        checks = [w["Prüfung"] for w in a.ways if w["Prüfung"] in ("gleich", "weicht ab") or w["Prüfung"].startswith("z =")]
        good = sum(1 for c in checks if c == "gleich" or c.startswith("z ="))
        rows.append({"Graph": name, "Knoten": a.n, "Kanten": a.m, "Monome": a.monomials, "Spannbäume": a.trees, "Wälder": A.spanning_forests(a.T), "Teilgraphen": A.connected_subgraphs(a.T), "Orientierungen": a.acyclic,
                     "P3": A.chromatic_value(a.T, a.n, a.comps, 3), "P4": A.chromatic_value(a.T, a.n, a.comps, 4), "Prüfungen": len(checks), "gleich": good, "Probleme": a.problems})
    return rows


def verdict_values(rows: list):
    ok = all(r["gleich"] == r["Prüfungen"] and not r["Probleme"] for r in rows)
    total = sum(r["Prüfungen"] for r in rows)
    g6 = next(r for r in rows if r["Graph"] == "Gitter 6×6")
    return ("success" if ok else "error"), (f"Aus einem Polynom je Graph folgen alle diese Zahlen; von {total} Prüfungen gegen unabhängige Wege stimmen {sum(r['gleich'] for r in rows)}. "
                                            f"Beim 6×6-Gitter ({g6['Kanten']} Kanten, {g6['Monome']} Monome): {big_text(g6['Spannbäume'])} Spannbäume, {big_text(g6['P3'])} Dreifärbungen, {big_text(g6['Orientierungen'])} azyklische Orientierungen. "
                                            f"Beim Dreieck gibt es mit drei Farben {next(r for r in rows if r['Graph'] == 'Dreieck')['P3']} Färbungen (3! = 6), bei K4 mit vier Farben {next(r for r in rows if r['Graph'] == 'K4')['P4']}.")


# ----------------------------------------------------------------------------- Experiment 3: Frontier im Polynom-Semiring
@functools.cache
def frontier_rows() -> list:
    rows = []
    for n in C.EXP_FRONTIER_SQUARES:
        nv, e = A.grid_graph(n, n)
        T, info = A.frontier_tutte(nv, e)
        rows.append({"Gitter": f"{n}×{n}", "Kanten": len(e), "Frontier": info["frontier"], "größte Schicht": info["max_states"], "Catalan": A.catalan(n), "Zustände": info["total_states"], "Stück 13": STUECK13_TREE_STATES[n],
                     "Monome": len(T), "Spannbäume": A.spanning_trees(T), "quadratisch": True})
    for r, c in C.EXP_ORDER_PAIR:
        nv, e = A.grid_graph(r, c)
        T, info = A.frontier_tutte(nv, e)
        rows.append({"Gitter": f"{r}×{c}", "Kanten": len(e), "Frontier": info["frontier"], "größte Schicht": info["max_states"], "Catalan": None, "Zustände": info["total_states"], "Stück 13": None,
                     "Monome": len(T), "Spannbäume": A.spanning_trees(T), "quadratisch": False})
    return rows


def verdict_frontier(rows: list):
    sq = [r for r in rows if r["quadratisch"]]
    same = all(r["Zustände"] == r["Stück 13"] for r in sq)
    cat = all(r["größte Schicht"] == r["Catalan"] for r in sq)
    wide, narrow = (next(r for r in rows if r["Gitter"] == g) for g in ("3×8", "8×3"))
    ok = same and cat and wide["Monome"] == narrow["Monome"] and wide["Spannbäume"] == narrow["Spannbäume"]
    last = sq[-1]
    return ("success" if ok else "error"), (f"Dieselben Zustände wie die Spannbäume in Stück 13 (Summen {', '.join(big_text(r['Zustände']) for r in sq)} für n = {sq[0]['Gitter'][0]} bis {last['Gitter'][0]}), nur ist der Wert ein Polynom: beim {last['Gitter']}-Gitter {big_text(last['Monome'])} Monome. "
                                            f"Die größte Schicht ist bei den quadratischen Gittern {sq[0]['Gitter']} bis {last['Gitter']} die Catalan-Zahl ({', '.join(big_text(r['größte Schicht']) for r in sq)}; gemessen, nicht bewiesen, in Phase 0 auch beim 8×8-Gitter). "
                                            f"Die Ordnung entscheidet wie in Stück 13: das 3×8-Gitter hat in Zeilenordnung (Frontier {wide['Frontier']}) {big_text(wide['Zustände'])} Zustände, dasselbe Gitter als 8×3 (Frontier {narrow['Frontier']}) nur {big_text(narrow['Zustände'])}, beide mit {big_text(wide['Spannbäume'])} Spannbäumen.")


# ----------------------------------------------------------------------------- Experiment 4: chromatisches Polynom
@functools.cache
def color_rows() -> list:
    rows = []
    for name in C.EXP_COLOR_GRAPHS:
        n, e, _ = named_graph(name)
        T, info = A.frontier_tutte(n, e)
        coeffs = A.chromatic_coefficients(T, n, info["components"])
        chi = next(k for k in range(1, 20) if A.chromatic_value(T, n, info["components"], k) > 0)
        values, checks = {}, {}
        for k in C.EXP_COLOR_KS:
            v = A.chromatic_value(T, n, info["components"], k)
            values[k] = v
            way, val, chk = check_chromatic(n, e, name, k, v, T, info["components"])
            checks[k] = (way, chk)
        rows.append({"Graph": name, "Knoten": n, "Kanten": len(e), "Polynom": A.coefficient_text(coeffs) if len(coeffs) <= 13 else None, "Werte": values, "Prüfung": checks, "chromatische Zahl": chi})
    return rows


def verdict_colors(rows: list):
    flat = [chk for r in rows for _, chk in r["Prüfung"].values()]
    ok = all(c in ("gleich",) or c.startswith("nur bis") for c in flat)
    checked = sum(c == "gleich" for c in flat)
    rest = "" if checked == len(flat) else " (der Rest liegt über den Grenzen der Prüfwege)"
    chi = ", ".join(f"{r['Graph']} {r['chromatische Zahl']}" for r in rows)
    pet = next(r for r in rows if r["Graph"] == "Petersen-Graph")["Werte"]
    return ("success" if ok else "error"), (f"Das chromatische Polynom P(G, k) zählt die Färbungen für jede Farbenzahl auf einmal; {checked} von {len(flat)} Werten sind gegen Zählen, Transfermatrix oder Stück 12 geprüft und gleich{rest}. "
                                           f"Kleinste Farbenzahl mit mindestens einer Färbung: {chi}. Petersen-Graph: {big_text(pet[3])}, {big_text(pet[4])}, {big_text(pet[5])} Färbungen mit drei, vier und fünf Farben (Stück 12).")


# ----------------------------------------------------------------------------- Experiment 5: Zuverlässigkeit
@functools.cache
def reliability_rows() -> list:
    out = []
    for name in C.EXP_REL_GRAPHS:
        n, e, _ = named_graph(name)
        T, info = A.frontier_tutte(n, e)
        curve = [(p, float(A.reliability_value(T, n, len(e), info["components"], Fraction(p).limit_denominator(1000)))) for p in C.EXP_REL_PS]
        samples = []
        for p in C.EXP_REL_SAMPLE_PS:
            exact = float(A.reliability_value(T, n, len(e), info["components"], Fraction(p).limit_denominator(1000)))
            est = A.reliability_sample(n, e, p, C.SAMPLE_DRAWS, C.SAMPLE_SEED)
            samples.append({"p": p, "exakt": exact, "gezogen": est, "z": A.sample_z(est, exact, C.SAMPLE_DRAWS)})
        out.append({"Graph": name, "Kanten": len(e), "Kurve": curve, "Ziehungen": samples})
    return out


def verdict_reliability(rows: list):
    zs = [s["z"] for r in rows for s in r["Ziehungen"]]
    ok = max(abs(z) for z in zs) <= 4
    g6 = next(r for r in rows if r["Graph"] == "Gitter 6×6")
    s9 = next(s for s in g6["Ziehungen"] if s["p"] == 0.9)
    mono = all(r["Kurve"][i][1] < r["Kurve"][i + 1][1] for r in rows for i in range(len(r["Kurve"]) - 1))
    return ("success" if ok and mono else "error"), (f"Die exakte Zuverlässigkeit steigt mit p und liegt bei allen {len(zs)} Zufallsziehungen im Rahmen (Schwelle: Betrag von z höchstens 4; größter Betrag von z: {de(max(abs(z) for z in zs), 2)}). "
                                                     f"Beim 6×6-Gitter mit p = 0,9: exakt {prob_text(Fraction(s9['exakt']).limit_denominator(10 ** 9))}, in {big_text(C.SAMPLE_DRAWS)} Ziehungen {de(s9['gezogen'], 5)}. Das Ziehen ist der Schätzer (Stück 15), das Polynom die Wahrheit.")


# ----------------------------------------------------------------------------- Spielwiese: eigene Kantenliste
def play_graph(text: str) -> dict:
    try:
        n, edges = A.parse_edge_list(text, C.CUSTOM_MAX_VERTICES, C.CUSTOM_MAX_EDGES)
    except ValueError as err:
        return {"error": str(err)}
    T, info = A.frontier_tutte(n, edges)
    comps = info["components"]
    coeffs = A.chromatic_coefficients(T, n, comps)
    out = {"n": n, "m": len(edges), "T": T, "tutte_text": A.poly_text(T), "chromatic_text": A.coefficient_text(coeffs), "trees": A.spanning_trees(T), "acyclic": A.acyclic_orientations(T), "layers": info["layers"], "ok": None}
    if len(edges) <= C.SUBSETS_EDGE_LIMIT:
        out["ok"] = A.tutte_subsets(n, edges) == T
    return out


def verdict_play(res: dict):
    if "error" in res:
        return "warning", res["error"]
    check = "" if res["ok"] is None else (" Gleich der Teilmengensumme über alle Kantenmengen." if res["ok"] else " Weicht von der Teilmengensumme ab.")
    kind = "success" if res["ok"] is not False else "error"
    return kind, (f"{res['n']} Knoten, {res['m']} Kanten: T(x, y) = {res['tutte_text']}; {plural(res['trees'], 'Spannbaum', 'Spannbäume')}, {plural(res['acyclic'], 'azyklische Orientierung', 'azyklische Orientierungen')}; "
                  f"P(k) = {res['chromatic_text']}.{check}")
