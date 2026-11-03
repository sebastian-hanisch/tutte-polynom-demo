"""Tutte- und chromatisches Polynom – ein Polynom, viele Zahlen - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 14 der Reihe „Abzählen und erzeugende Funktionen“: Das Tutte-Polynom fasst Spannbäume, Färbungen, Flüsse, Orientierungen und die Zuverlässigkeit eines Graphen in einer Rechnung zusammen.
Deletion–Contraction definiert es; die Frontier-Rechnung aus Stück 13 mit einem Polynom als Wert berechnet es für Gitter bis 7×7.
Aufbau und Regeln: DEMO-PLAYBOOK.md (§2).

Lauffähig mit: streamlit run app.py
"""

from fractions import Fraction

import streamlit as st

import tpl_constants as C
from tpl_evaluation import (
    Settings,
    analyse,
    big_text,
    color_rows,
    dc_rows,
    de,
    frontier_rows,
    play_graph,
    prob_text,
    reliability_rows,
    value_rows,
    verdict_answers,
    verdict_colors,
    verdict_dc,
    verdict_frontier,
    verdict_play,
    verdict_reliability,
    verdict_values,
)
from tpl_layout import dunkles_design, kopf_css
from tpl_pdf_export import build_pdf
from tpl_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    sidebar_presets,
    sync_query_params,
)
from tpl_visualization import build_colors, build_dc, build_frontier, build_layers, build_reliability

st.set_page_config(page_title="Tutte-Polynom – Sebastian Hanisch", layout="wide")

SPINNER = "Die Experimente werden einmal gerechnet …"


@st.cache_data(show_spinner="Das Polynom wird gerechnet …")
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=SPINNER)
def _dc():
    return dc_rows()


@st.cache_data(show_spinner=SPINNER)
def _values():
    return value_rows()


@st.cache_data(show_spinner=SPINNER)
def _frontier():
    return frontier_rows()


@st.cache_data(show_spinner=SPINNER)
def _colors():
    return color_rows()


@st.cache_data(show_spinner=SPINNER)
def _reliability():
    return reliability_rows()


@st.cache_data(show_spinner=False)
def _play(text):
    return play_graph(text)


def verdict(pair):
    kind, text = pair
    getattr(st, kind)(text)


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in tpl_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🧮 Tutte- und chromatisches Polynom – ein Polynom, viele Zahlen")
st.markdown(
    """
**Wie viele Spannbäume, Färbungen, Orientierungen hat ein Graph, und wie zuverlässig ist er?** Das **Tutte-Polynom** T(x, y) beantwortet alle diese Fragen auf einmal: aus **einem** Polynom folgen die **Spannbäume** T(1, 1), die **azyklischen Orientierungen** T(2, 0),
die **Färbungen** mit k Farben (das chromatische Polynom), die **Flüsse** und die **Zuverlässigkeit** (bleibt der Graph zusammenhängend, wenn jede Kante nur mit Wahrscheinlichkeit p hält). **Deletion–Contraction** (Kante löschen oder zusammenziehen) definiert es;
die **Frontier-Rechnung** aus Stück 13 mit einem **Polynom als Wert** statt einer Zahl berechnet es, und ihre Zustände sind **dieselben** wie bei den Spannbäumen. Fast jede Zahl wird gegen einen unabhängigen Weg geprüft; wo die Prüfwege zu langsam sind, bleibt die Zahl ungeprüft.

Weiter unten: **fünf Experimente** (**🔬**), eine **🎲 Spielwiese** für eigene Kantenlisten, **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktioniert die Rechnung", expanded=True):
    st.markdown(
        """
1. **Teilmengen:** T(x, y) ist eine Summe über alle Kantenmengen A: jedes A trägt (x−1)^(r(E)−r(A)) · (y−1)^(Zahl der Kreise in A) bei; r ist der Rang (Knoten minus Komponenten). Bei m Kanten sind das 2^m Mengen.
2. **Frontier:** Wie in Stück 13 werden die Kanten der Reihe nach entschieden. Der **Zustand** ist, welche Frontier-Knoten schon verbunden sind; der **Wert** zählt, wie viele Teilmengen mit welcher Zahl von Verschmelzungen und Kreiskanten zu diesem Zustand führen.
3. **Auswerten:** Am Ende wird aus den Zählungen das Polynom. Spannbäume, Färbungen, Flüsse und Zuverlässigkeit sind **Einsetzungen** (x, y) in dasselbe Polynom.
4. **Deletion–Contraction:** T(G) = T(G − e) + T(G / e) für eine Kante e, die weder Schleife noch Brücke ist; Brücke: x · T(G / e), Schleife: y · T(G − e). Die Blätter dieser Rekursion sind genau die Spannbäume.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Graph**")
    graph = st.selectbox("Graph", list(C.GRAPHS), key="graph_select", help="Gitter, Petersen-Graph, vollständiger Graph, Kreis oder eine eigene Kantenliste.")
    rows = st.slider("Zeilen (Gitter)", *bounds("rows_slider"), key="rows_slider", help=f"Knoten je Spalte, höchstens {C.SIDE_MAX}.")
    cols = st.slider("Spalten (Gitter)", *bounds("cols_slider"), key="cols_slider", help=f"Knoten je Zeile, höchstens {C.SIDE_MAX}.")
    n = st.slider("Knoten (vollständiger Graph, Kreis)", *bounds("n_slider"), key="n_slider", help=f"Vollständige Graphen bis K{C.COMPLETE_CAP}, Kreise ab {C.CYCLE_MIN} Knoten.")
    order = st.selectbox("Kantenordnung (Gitter)", list(C.ORDERS), key="order_select", help="Zeilenordnung oder Spaltenordnung; sie bestimmt die Frontier und damit die Zahl der Zustände. Bei den anderen Graphen ist die Ordnung vorgegeben.")
    edges = st.text_input("Eigene Kantenliste", key="edges_input", max_chars=C.EDGES_MAX_LEN,
                          help=f"Zum Beispiel 1-2, 2-3, 1-3: Knoten 1 bis {C.CUSTOM_MAX_VERTICES}, höchstens {C.CUSTOM_MAX_EDGES} Kanten, zusammenhängend; Mehrfachkanten und Schleifen sind erlaubt. Gilt nur bei „Eigene Kantenliste“.")
    st.markdown("**Auswertungspunkte**")
    k = st.slider("Farben k", *bounds("k_slider"), key="k_slider", help="Wie viele Färbungen mit k Farben und wie viele nirgends verschwindende Flüsse mit Werten aus Z_k.")
    p = st.slider("Kante hält mit Wahrscheinlichkeit p (%)", *bounds("p_slider"), key="p_slider", help="Wahrscheinlichkeit, dass der Graph zusammenhängend bleibt, wenn jede Kante unabhängig mit dieser Wahrscheinlichkeit hält.")

sync_query_params({"graph_select": graph, "rows_slider": int(rows), "cols_slider": int(cols), "n_slider": int(n), "order_select": order, "k_slider": int(k), "p_slider": int(p), "edges_input": edges})

settings = Settings(graph, int(rows), int(cols), int(n), order, int(k), int(p), edges)
a = _analysis(settings)
for note in a.notes:
    st.info(note)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Monome des Polynoms", big_text(a.monomials), help="Zahl der Terme x^i y^j von T(x, y) mit Koeffizient ungleich null.")
m2.metric("Frontier-Zustände (Summe)", big_text(a.states), help=f"Zustände über alle {a.m} Kanten; die größte Schicht hat {big_text(a.max_layer)}. Eine Summe über alle 2^m Kantenmengen wären {big_text(2 ** a.m)} Mengen.")
m3.metric("Spannbäume", big_text(a.trees), help="T(1, 1).")
m4.metric(f"Färbungen mit {a.k} {'Farbe' if a.k == 1 else 'Farben'}", big_text(a.chromatic), help="Das chromatische Polynom P(G, k) = (−1)^(n−c) k^c T(1−k, 0).")
st.plotly_chart(build_layers(a.layers), width="stretch", key="main_chart")
st.caption("Zahl der Zustände nach jeder Kante: die Frontier-Rechnung wächst, bis die Frontier voll ist, und schrumpft am Ende.")
if a.tutte_text:
    st.markdown("**Tutte-Polynom**")
    st.code(f"T(x, y) = {a.tutte_text}", language=None)
if a.chromatic_text:
    st.markdown("**Chromatisches Polynom**")
    st.code(f"P(k) = {a.chromatic_text}", language=None)
if not a.tutte_text:
    st.caption(f"Das Polynom hat {a.monomials} Monome, zu viele für die Anzeige.")
st.dataframe(a.ways, hide_index=True, width="stretch")

if st.button("📄 PDF des aktuellen Graphen erstellen", key="pdf_make"):
    st.session_state["pdf_made"] = (settings, build_pdf(a))
made = st.session_state.get("pdf_made")
if made and made[0] == settings:
    st.download_button("⬇️ PDF herunterladen", data=made[1], file_name="tutte-polynom.pdf", mime="application/pdf", key="pdf_download")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Wie rechnet man viele Zahlen eines Graphen in einer Rechnung?")
verdict(verdict_answers(a))

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 1: Deletion–Contraction, ohne und mit Zusammenfassen")
st.caption("Die Rekursion hat genau so viele Blätter wie der Graph Spannbäume, nicht 2^m. Fasst man gleiche Teilgraphen zusammen (nach Umbenennung der Knoten), schrumpft die Zahl der Aufrufe stark; die Frontier-Rechnung braucht noch weniger.")
dc = _dc()
st.plotly_chart(build_dc(dc), width="stretch", key="dc_chart")
st.dataframe([{"Gitter": r["Gitter"], "Kanten": r["Kanten"], "Kantenmengen 2^m": big_text(r["Mengen"]), "Spannbäume": big_text(r["Spannbäume"]), "Blätter (ohne Zusammenfassen)": "–" if r["Blätter"] is None else big_text(r["Blätter"]),
               "Aufrufe ohne": "–" if r["Aufrufe"] is None else big_text(r["Aufrufe"]), "Aufrufe mit Zusammenfassen": big_text(r["Aufrufe mit Zusammenfassen"]), "Treffer": big_text(r["Treffer"]),
               "Frontier-Zustände": big_text(r["Frontier-Zustände"]), "Polynom gleich": "ja" if r["gleich"] else "nein"} for r in dc], hide_index=True, width="stretch")
verdict(verdict_dc(dc))

st.markdown("---")

st.subheader("🔬 Experiment 2: Ein Polynom, viele Zahlen")
st.caption("Je Graph ein Polynom; daraus Spannbäume, Wälder, zusammenhängende Teilgraphen, azyklische Orientierungen und Färbungen mit drei und vier Farben. Fast jede Zahl ist gegen einen unabhängigen Weg geprüft (Kirchhoff, Zählen, Transfermatrix, Aufzählen, Teilmengensumme); wo die Prüfwege zu langsam sind, steht „nur bis …“ und die Zahl bleibt ungeprüft.")
values = _values()
st.dataframe([{"Graph": r["Graph"], "Knoten": r["Knoten"], "Kanten": r["Kanten"], "Monome": r["Monome"], "Spannbäume": big_text(r["Spannbäume"]), "Wälder": big_text(r["Wälder"]), "zusammenhängende Teilgraphen": big_text(r["Teilgraphen"]),
               "azyklische Orientierungen": big_text(r["Orientierungen"]), "Färbungen k = 3": big_text(r["P3"]), "Färbungen k = 4": big_text(r["P4"]), "Prüfungen gleich": f"{r['gleich']} von {r['Prüfungen']}"} for r in values], hide_index=True, width="stretch")
verdict(verdict_values(values))

st.markdown("---")

st.subheader("🔬 Experiment 3: Frontier im Polynom-Semiring")
st.caption("Dieselbe Frontier-Rechnung wie bei den Spannbäumen in Stück 13, mit einem Polynom statt einer Zahl als Wert: Zustände, größte Schicht und Monome für quadratische Gitter, dazu die Kantenordnung beim 3×8-Gitter gegen 8×3.")
fr = _frontier()
st.plotly_chart(build_frontier(fr), width="stretch", key="frontier_chart")
st.dataframe([{"Gitter": r["Gitter"], "Kanten": r["Kanten"], "Frontier": r["Frontier"], "größte Schicht": big_text(r["größte Schicht"]), "Catalan-Zahl": "–" if r["Catalan"] is None else big_text(r["Catalan"]),
               "Zustände (Summe)": big_text(r["Zustände"]), "Stück 13 (Spannbäume)": "–" if r["Stück 13"] is None else big_text(r["Stück 13"]), "Monome": big_text(r["Monome"]), "Spannbäume": big_text(r["Spannbäume"])} for r in fr], hide_index=True, width="stretch")
verdict(verdict_frontier(fr))

st.markdown("---")

st.subheader("🔬 Experiment 4: Das chromatische Polynom")
st.caption("Das chromatische Polynom P(G, k) zählt die Färbungen für jede Farbenzahl k auf einmal; die Prüfwege sind Zählen aller Färbungen, die Zeilen-Transfermatrix (Gitter) und die Zahlen aus Stück 12 (Petersen-Graph).")
colors = _colors()
st.plotly_chart(build_colors(colors), width="stretch", key="color_chart")
st.dataframe([{"Graph": r["Graph"], "Knoten": r["Knoten"], "Kanten": r["Kanten"], "P(k)": r["Polynom"] or "zu lang", **{f"k = {k_}": big_text(r["Werte"][k_]) for k_ in C.EXP_COLOR_KS},
               "Prüfweg": ", ".join(sorted({w for w, c in r["Prüfung"].values() if w != "–"})) or "–", "chromatische Zahl": r["chromatische Zahl"]} for r in colors], hide_index=True, width="stretch")
verdict(verdict_colors(colors))

st.markdown("---")

st.subheader("🔬 Experiment 5: Zuverlässigkeit")
st.caption("Hält jede Kante unabhängig mit Wahrscheinlichkeit p, bleibt der Graph mit Wahrscheinlichkeit R(p) zusammenhängend: R(p) = p^(n−1) (1−p)^(m−n+1) T(1, 1/(1−p)), exakt als Bruch. Die Punkte sind Zufallsziehungen mit festem Seed.")
rel = _reliability()
st.plotly_chart(build_reliability(rel), width="stretch", key="rel_chart")
st.dataframe([{"Graph": r["Graph"], "p": de(s["p"], 2), "exakt": prob_text(Fraction(s["exakt"]).limit_denominator(10 ** 9)), "gezogen": de(s["gezogen"], 5), "z": de(s["z"], 2)} for r in rel for s in r["Ziehungen"]], hide_index=True, width="stretch")
verdict(verdict_reliability(rel))

st.markdown("---")

# --- Spielwiese ----------------------------------------------------------------------------------------------------------------------------

st.subheader("🎲 Spielwiese: eine eigene Kantenliste")
st.caption(f"Knoten 1 bis {C.CUSTOM_MAX_VERTICES}, höchstens {C.CUSTOM_MAX_EDGES} Kanten, zusammenhängend, zum Beispiel 1-2, 2-3, 3-1, 3-4. Mehrfachkanten und Schleifen sind erlaubt.")
play_text = st.text_input("Kanten", value=C.PLAY_EDGES_DEFAULT, max_chars=C.EDGES_MAX_LEN, key="play_edges", help="Kanten als a-b, getrennt durch Komma.")
play = _play(play_text)
verdict(verdict_play(play))

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    f"""
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Die Frontier bleibt schmal** | Die Rechnung ist exponentiell in der Frontierbreite: bei quadratischen Gittern wächst die größte Schicht wie die Catalan-Zahl C(n) (gemessen bis 8×8, dort 1.430), bei dichten Graphen höchstens wie die Bell-Zahl der Frontierbreite. Das Tutte-Polynom ist im Allgemeinen #P-schwer. | Experiment 3 |
| **Die Kantenordnung ist gut** | Dasselbe Gitter hat als 3×8 (Frontier 9) 17.657 Zustände, als 8×3 (Frontier 4) nur 171; die beste Ordnung zu finden ist selbst schwer, die App kennt nur Zeile und Spalte. | Experiment 3 |
| **Der Graph ist zusammenhängend** | Die Formeln für Färbungen und Zuverlässigkeit sind für mehrere Komponenten angepasst, aber die App prüft die Kantenliste auf Zusammenhang und lehnt andere Listen ab. | Spielwiese |
| **Zusammenfassen gleicher Teilgraphen ist einfach** | Es fasst nur zusammen, was nach Umbenennung gleich ist, nicht isomorphe Graphen; ein Isomorphietest würde mehr sparen, kostet aber selbst. | Experiment 1 |
| **Die Prüfwege sind klein** | Zählen aller Färbungen, Aufzählen der Orientierungen und der Kantenzustände gibt es nur bis {big_text(C.COLORING_BRUTE_LIMIT)} Zuordnungen und {C.ORIENTATION_EDGE_LIMIT} Kanten; die Teilmengensumme bis {C.SUBSETS_EDGE_LIMIT} Kanten. Darüber prüfen Kirchhoff, Transfermatrix, Stanleys Betrag von P(−1) und Zufallsziehen. | Experiment 2 |
| **Unabhängige Kanten** | Die Zuverlässigkeit nimmt an, dass jede Kante unabhängig mit derselben Wahrscheinlichkeit hält; bei gemeinsamen Ausfällen oder ungleichen Wahrscheinlichkeiten gilt die Formel nicht. | Experiment 5 |
| **Die Größe ist begrenzt** | Gitter bis {C.SIDE_MAX}×{C.SIDE_MAX} (8×8 braucht in Python etwa 26 Sekunden), vollständige Graphen bis K{C.COMPLETE_CAP}, eigene Listen bis {C.CUSTOM_MAX_VERTICES} Knoten und {C.CUSTOM_MAX_EDGES} Kanten. | – |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Tutte-Polynom.** Für einen Graphen $G = (V, E)$ mit $c(A)$ Komponenten des Teilgraphen $(V, A)$ und Rang $r(A) = |V| - c(A)$ ist
$$T(G; x, y) = \sum_{A \subseteq E} (x - 1)^{r(E) - r(A)} \, (y - 1)^{|A| - r(A)}.$$
**Deletion–Contraction.** Für eine Kante $e$, die weder Schleife noch Brücke ist: $T(G) = T(G - e) + T(G / e)$; für eine Brücke $T(G) = x \, T(G / e)$, für eine Schleife $T(G) = y \, T(G - e)$; für einen Graphen ohne Kanten $T = 1$.
Jedes Blatt der Rekursion trägt ein Monom mit Koeffizient 1: die Zahl der Blätter ist $T(1, 1)$.

**Frontier-Rechnung.** Zustand: die Zusammenhangsklassen der Frontier-Knoten (Partition). Wert: eine Tabelle, die jedem Paar $(k, e)$ (Zahl der Verschmelzungen, Zahl der Kreiskanten) die Zahl der Teilmengen zuordnet. Eine gewählte Kante zwischen zwei Klassen erhöht $k$, eine innerhalb einer Klasse erhöht $e$. Am Ende ist $r(A) = k$ und $|A| - r(A) = e$.

**Einsetzungen** (für zusammenhängendes $G$ mit $n$ Knoten und $m$ Kanten):
$T(1,1)$ Spannbäume, $T(2,1)$ Wälder, $T(1,2)$ zusammenhängende aufspannende Teilgraphen, $T(2,0)$ azyklische Orientierungen, $T(2,2) = 2^m$.
**Chromatisches Polynom:** $P(G, k) = (-1)^{n-1} \, k \, T(G; 1 - k, 0)$; $P(G, -1)$ hat den Betrag $T(2, 0)$ (Stanley).
**Flusspolynom:** $F(G, k) = (-1)^{m-n+1} \, T(G; 0, 1 - k)$ zählt die nirgends verschwindenden $\mathbb{Z}_k$-Flüsse.
**Zuverlässigkeit:** $R(G; p) = p^{n-1} (1 - p)^{m-n+1} \, T\!\left(G; 1, \tfrac{1}{1-p}\right)$.

**Literatur** (Titel und Fundstelle aus dem Gedächtnis, nicht eingesehen).
W. T. Tutte: *A contribution to the theory of chromatic polynomials*, Canadian Journal of Mathematics 6, 1954, S. 80–91.
R. P. Stanley: *Acyclic orientations of graphs*, Discrete Mathematics 5, 1973, S. 171–178.
F. Jaeger, D. L. Vertigan und D. J. A. Welsh: *On the computational complexity of the Jones and Tutte polynomials*, Mathematical Proceedings of the Cambridge Philosophical Society 108, 1990, S. 35–53.
D. E. Knuth: *The Art of Computer Programming, Vol. 4A*, Addison-Wesley, 2011, Abschnitt 7.1.4 (Frontier-Methode, Simpath).
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zur Reihe: [Abzählen: von der Rekursion zur Verfahrenswahl](https://sebastianhanisch.net/konzepte-abzaehlen.html)."
)
