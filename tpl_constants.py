"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

GRAPHS = ("Gitter", "Petersen-Graph", "Vollständiger Graph", "Kreis", "Eigene Kantenliste")
DEFAULT_GRAPH = "Gitter"
ORDER_NAMES = {"zeile": "Zeile", "spalte": "Spalte"}
ORDERS = tuple(ORDER_NAMES.values())
ORDER_KEYS = {v: k for k, v in ORDER_NAMES.items()}
DEFAULT_ORDER = "Zeile"

SIDE_MIN, SIDE_MAX, DEFAULT_ROWS, DEFAULT_COLS = 1, 7, 6, 6
N_MIN, N_MAX, DEFAULT_N = 2, 12, 5            # Knotenzahl für vollständigen Graphen und Kreis
COMPLETE_CAP, CYCLE_MIN = 7, 3                # vollständiger Graph bis K7, Kreis ab C3
K_MIN, K_MAX, DEFAULT_K = 1, 12, 3            # Zahl der Farben
P_MIN, P_MAX, DEFAULT_P = 1, 99, 90           # Haltewahrscheinlichkeit einer Kante in Prozent
DEFAULT_EDGES = "1-2, 2-3, 1-3, 3-4"
EDGES_MAX_LEN = 120
CUSTOM_MAX_VERTICES, CUSTOM_MAX_EDGES = 9, 20

SUBSETS_EDGE_LIMIT = 15       # Teilmengensumme über alle 2^m Mengen bis zu so vielen Kanten
DC_EDGE_LIMIT = 27            # Deletion–Contraction mit Zusammenfassen bis zu so vielen Kanten
ORIENTATION_EDGE_LIMIT = 12   # Aufzählen aller Orientierungen und aller Kantenzustände bis zu so vielen Kanten
COLORING_BRUTE_LIMIT = 300000  # Zählen aller Färbungen, wenn k^n so klein ist
TRANSFER_ROWS_LIMIT = 400      # Zeilen-Transfermatrix für Gitter, wenn so wenige Zeilenfärbungen
FLOW_BRUTE_LIMIT = 300000      # Aufzählen aller Flüsse, wenn (k−1)^m so klein ist
SAMPLE_DRAWS = 30000           # Zufallsziehungen für die Zuverlässigkeit großer Graphen
SAMPLE_SEED = 20261102

PETERSEN_COLORINGS = {3: 120, 4: 12960, 5: 332880}   # aus Stück 12 (Aufzählen und Burnside), nicht neu gerechnet
PETERSEN_FLOW_5 = 240                                 # aus dem Gedächtnis (Flusspolynom des Petersen-Graphen)

EXP_DC_PLAIN = ((2, 2), (2, 3), (3, 3), (2, 5), (3, 4), (4, 4))   # Gitter, auf denen die Rekursion ohne Zusammenfassen läuft
EXP_DC_MEMO_ONLY = ((3, 6), (5, 5))                                 # nur mit Zusammenfassen (ohne: Blätter = Spannbäume, zu viele)
EXP_FRONTIER_SQUARES = (3, 4, 5, 6, 7)
EXP_ORDER_PAIR = ((3, 8), (8, 3))
EXP_VALUE_GRAPHS = ("Dreieck", "K4", "K5", "Kreis C6", "Petersen-Graph", "Gitter 3×3", "Gitter 4×4", "Gitter 6×6")
EXP_COLOR_KS = (2, 3, 4, 5)
EXP_COLOR_GRAPHS = ("Dreieck", "K4", "Kreis C6", "Petersen-Graph", "Gitter 3×3", "Gitter 4×4")
EXP_REL_GRAPHS = ("Gitter 4×4", "Gitter 6×6", "Petersen-Graph")
EXP_REL_PS = tuple(i / 20 for i in range(1, 20))   # 0,05 bis 0,95
EXP_REL_SAMPLE_PS = (0.5, 0.9, 0.99)
PLAY_EDGES_DEFAULT = "1-2, 2-3, 3-1, 3-4"

COLOR_MAIN = "#2F6B65"
COLOR_ALL = "rgba(150,150,150,0.75)"
COLOR_WARN = "#c0504d"
COLOR_LINE = "#4c78a8"

PRESETS = {
    "Standardfall: Gitter 6×6": {"graph": "Gitter", "rows": 6, "cols": 6, "n": 5, "order": "Zeile", "k": 3, "p": 90, "edges": DEFAULT_EDGES},
    "Petersen-Graph: Färbungen und Fluss": {"graph": "Petersen-Graph", "rows": 6, "cols": 6, "n": 5, "order": "Zeile", "k": 5, "p": 90, "edges": DEFAULT_EDGES},
    "Vollständiger Graph K5": {"graph": "Vollständiger Graph", "rows": 6, "cols": 6, "n": 5, "order": "Zeile", "k": 4, "p": 50, "edges": DEFAULT_EDGES},
    "Gitter 4×4: Färbungen und Zuverlässigkeit": {"graph": "Gitter", "rows": 4, "cols": 4, "n": 5, "order": "Zeile", "k": 4, "p": 90, "edges": DEFAULT_EDGES},
    "Kreis C6": {"graph": "Kreis", "rows": 6, "cols": 6, "n": 6, "order": "Zeile", "k": 3, "p": 80, "edges": DEFAULT_EDGES},
    "Eigene Kantenliste: Dreieck mit Anhang": {"graph": "Eigene Kantenliste", "rows": 6, "cols": 6, "n": 5, "order": "Zeile", "k": 3, "p": 90, "edges": DEFAULT_EDGES},
}
PRESET_HELP = {
    "Standardfall: Gitter 6×6": "Das 6×6-Gitter hat 60 Kanten (2^60 Teilmengen), die Frontier-Rechnung braucht 6.001 Zustände und liefert ein Polynom mit 430 Monomen: daraus 32.565.539.635.200 Spannbäume und 101.596.896 Dreifärbungen.",
    "Petersen-Graph: Färbungen und Fluss": "Der Petersen-Graph hat 2.000 Spannbäume und 332.880 Färbungen mit fünf Farben (Stück 12 hat sie schon gezählt); der Fluss mit Werten aus Z₅ hat 240 Möglichkeiten.",
    "Vollständiger Graph K5": "Fünf Knoten, jeder mit jedem: mit vier Farben gibt es keine Färbung (P(4) = 0), 120 azyklische Orientierungen (5!), Tutte-Polynom mit 14 Monomen.",
    "Gitter 4×4: Färbungen und Zuverlässigkeit": "7.812 Dreifärbungen und 6.000.732 Vierfärbungen des 4×4-Gitters; hält jede Kante mit Wahrscheinlichkeit 0,9, bleibt es mit Wahrscheinlichkeit 0,944085 zusammenhängend.",
    "Kreis C6": "Der Kreis hat sechs Spannbäume und das chromatische Polynom (k−1)⁶ + (k−1): bei drei Farben 66 Färbungen.",
    "Eigene Kantenliste: Dreieck mit Anhang": "Das Dreieck 1-2-3 mit einem Anhang 3-4: Tutte-Polynom x³ + x² + xy, 12 Färbungen mit drei Farben; die Liste ist in der Seitenleiste änderbar.",
}
