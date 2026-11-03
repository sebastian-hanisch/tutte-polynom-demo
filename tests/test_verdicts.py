"""Urteilstexte (Schicht 3): die Texte, die die App zeigt, mit genauem Wortlaut für alle Voreinstellungen und Experimente, damit jede Zahl darin geprüft ist."""

import tpl_constants as C
import tpl_evaluation as ev

S = ev.Settings


def answer(name):
    return ev.verdict_answers(ev.analyse(S(**C.PRESETS[name])))


def test_answer_standard_case_exact():
    assert answer("Standardfall: Gitter 6×6") == ("success",
        "Gitter 6×6: 36 Knoten, 60 Kanten. Die Frontier-Rechnung (Kantenordnung: Zeile, Frontier 7) braucht 6.001 Zustände (größte Schicht 132) statt der 1,15·10¹⁸ (19 Stellen) Kantenmengen und liefert ein Tutte-Polynom mit 430 Monomen. "
        "Daraus: 32.565.539.635.200 Spannbäume, 101.596.896 Färbungen mit 3 Farben, 3,99·10¹⁶ (17 Stellen) azyklische Orientierungen; hält jede Kante mit Wahrscheinlichkeit 0,90, bleibt der Graph mit Wahrscheinlichkeit 0,935088 zusammenhängend. Alle Prüfwege stimmen überein.")


def test_answer_petersen_and_k5_exact():
    assert answer("Petersen-Graph: Färbungen und Fluss") == ("success",
        "Petersen-Graph: 10 Knoten, 15 Kanten. Die Frontier-Rechnung (Kantenordnung: vorgegeben, Frontier 6) braucht 361 Zustände (größte Schicht 49) statt der 32.768 Kantenmengen und liefert ein Tutte-Polynom mit 26 Monomen. "
        "Daraus: 2.000 Spannbäume, 332.880 Färbungen mit 5 Farben, 16.680 azyklische Orientierungen; hält jede Kante mit Wahrscheinlichkeit 0,90, bleibt der Graph mit Wahrscheinlichkeit 0,988567 zusammenhängend. Alle Prüfwege stimmen überein.")
    assert answer("Vollständiger Graph K5") == ("success",
        "K5: 5 Knoten, 10 Kanten. Die Frontier-Rechnung (Kantenordnung: vorgegeben, Frontier 5) braucht 66 Zustände (größte Schicht 14) statt der 1.024 Kantenmengen und liefert ein Tutte-Polynom mit 14 Monomen. "
        "Daraus: 125 Spannbäume, 0 Färbungen mit 4 Farben, 120 azyklische Orientierungen; hält jede Kante mit Wahrscheinlichkeit 0,50, bleibt der Graph mit Wahrscheinlichkeit 0,710938 zusammenhängend. Alle Prüfwege stimmen überein.")


def test_answer_grid_cycle_and_custom_exact():
    assert answer("Gitter 4×4: Färbungen und Zuverlässigkeit") == ("success",
        "Gitter 4×4: 16 Knoten, 24 Kanten. Die Frontier-Rechnung (Kantenordnung: Zeile, Frontier 5) braucht 251 Zustände (größte Schicht 14) statt der 16.777.216 Kantenmengen und liefert ein Tutte-Polynom mit 73 Monomen. "
        "Daraus: 100.352 Spannbäume, 6.000.732 Färbungen mit 4 Farben, 5.015.972 azyklische Orientierungen; hält jede Kante mit Wahrscheinlichkeit 0,90, bleibt der Graph mit Wahrscheinlichkeit 0,944085 zusammenhängend. Alle Prüfwege stimmen überein.")
    assert answer("Kreis C6") == ("success",
        "Kreis C6: 6 Knoten, 6 Kanten. Die Frontier-Rechnung (Kantenordnung: vorgegeben, Frontier 3) braucht 11 Zustände (größte Schicht 2) statt der 64 Kantenmengen und liefert ein Tutte-Polynom mit 6 Monomen. "
        "Daraus: 6 Spannbäume, 66 Färbungen mit 3 Farben, 62 azyklische Orientierungen; hält jede Kante mit Wahrscheinlichkeit 0,80, bleibt der Graph mit Wahrscheinlichkeit 0,655360 zusammenhängend. Alle Prüfwege stimmen überein.")
    assert answer("Eigene Kantenliste: Dreieck mit Anhang") == ("success",
        "Eigener Graph: 4 Knoten, 4 Kanten. Die Frontier-Rechnung (Kantenordnung: wie in der Liste, Frontier 3) braucht 6 Zustände (größte Schicht 2) statt der 16 Kantenmengen und liefert ein Tutte-Polynom mit 3 Monomen. "
        "Daraus: 3 Spannbäume, 12 Färbungen mit 3 Farben, 12 azyklische Orientierungen; hält jede Kante mit Wahrscheinlichkeit 0,90, bleibt der Graph mit Wahrscheinlichkeit 0,874800 zusammenhängend. Alle Prüfwege stimmen überein.")


def test_answer_singular_forms_and_error():
    a = ev.analyse(S("Eigene Kantenliste", 6, 6, 5, "Zeile", 1, 50, "1-2"))
    text = ev.verdict_answers(a)[1]
    assert "2 Knoten, 1 Kante." in text and "braucht 1 Zustand (" in text and "mit 1 Monom." in text and "1 Spannbaum," in text and "0 Färbungen mit 1 Farbe" in text and "2 azyklische Orientierungen;" in text
    a.problems.append("zwei Wege weichen ab")
    assert ev.verdict_answers(a) == ("error", "Die Rechenwege widersprechen sich: zwei Wege weichen ab")


def test_ways_table_of_the_petersen_preset():
    a = ev.analyse(S(**C.PRESETS["Petersen-Graph: Färbungen und Fluss"]))
    assert [(w["Größe"], w["Wert"], w["Prüfweg"], w["Prüfwert"], w["Prüfung"]) for w in a.ways] == [
        ("Spannbäume T(1,1)", "2.000", "Kirchhoff (Determinante der Laplace-Matrix)", "2.000", "gleich"),
        ("Färbungen mit 5 Farben: P(5)", "332.880", "Stück 12 (Zählen und Burnside)", "332.880", "gleich"),
        ("Azyklische Orientierungen T(2,0)", "16.680", "Stanley: |P(−1)| (ein anderer Auswertungspunkt desselben Polynoms)", "16.680", "gleich"),
        ("Wälder T(2,1)", "22.292", "Teilmengensumme (alle 2^m Kantenmengen)", "22.292", "gleich"),
        ("Zusammenhängende Teilgraphen T(1,2)", "5.968", "Teilmengensumme (alle 2^m Kantenmengen)", "5.968", "gleich"),
        ("Alle Kantenmengen T(2,2)", "32.768", "2^m", "32.768", "gleich"),
        ("Ganzes Polynom", "26 Monome", "Teilmengensumme", "26 Monome", "gleich"),
        ("Ganzes Polynom", "26 Monome", "Deletion–Contraction mit Zusammenfassen", "26 Monome", "gleich"),
        ("Nirgends verschwindende Flüsse mit Werten aus Z5: F(5)", "240", "aus dem Gedächtnis (Flusspolynom des Petersen-Graphen)", "240", "gleich"),
        ("Zuverlässigkeit bei p = 0,90", "0,988567", "Zufallsziehen (30.000 Ziehungen, fester Seed)", "0,98910", "z = 0,87"),
    ]


def test_dc_verdict_exact():
    assert ev.verdict_dc(ev.dc_rows()) == ("success",
        "Deletion–Contraction hat genau so viele Blätter wie der Graph Spannbäume (bei allen 6 gerechneten Gittern gleich; 4×4: 100.352 Blätter in 497.030 Aufrufen, nicht 16.777.216 Kantenmengen). "
        "Fasst man gleiche Teilgraphen zusammen, braucht das 5×5-Gitter 242.898 Aufrufe statt 557.568.000 Blättern; die Frontier-Rechnung kommt mit 1.259 Zuständen aus, und Deletion–Contraction mit Zusammenfassen und die Frontier-Rechnung liefern dasselbe Polynom.")


def test_values_verdict_exact():
    assert ev.verdict_values(ev.value_rows()) == ("success",
        "Aus einem Polynom je Graph folgen alle diese Zahlen; von 71 Prüfungen gegen unabhängige Wege stimmen 71. Beim 6×6-Gitter (60 Kanten, 430 Monome): 32.565.539.635.200 Spannbäume, 101.596.896 Dreifärbungen, 3,99·10¹⁶ (17 Stellen) azyklische Orientierungen. "
        "Beim Dreieck gibt es mit drei Farben 6 Färbungen (3! = 6), bei K4 mit vier Farben 24.")


def test_frontier_verdict_exact():
    assert ev.verdict_frontier(ev.frontier_rows()) == ("success",
        "Dieselben Zustände wie die Spannbäume in Stück 13 (Summen 46, 251, 1.259, 6.001, 27.645 für n = 3 bis 7), nur ist der Wert ein Polynom: beim 7×7-Gitter 839 Monome. "
        "Die größte Schicht ist bei den quadratischen Gittern 3×3 bis 7×7 die Catalan-Zahl (5, 14, 42, 132, 429; gemessen, nicht bewiesen, in Phase 0 auch beim 8×8-Gitter). "
        "Die Ordnung entscheidet wie in Stück 13: das 3×8-Gitter hat in Zeilenordnung (Frontier 9) 17.657 Zustände, dasselbe Gitter als 8×3 (Frontier 4) nur 171, beide mit 59.817.135 Spannbäumen.")


def test_colors_verdict_exact():
    assert ev.verdict_colors(ev.color_rows()) == ("success",
        "Das chromatische Polynom P(G, k) zählt die Färbungen für jede Farbenzahl auf einmal; 24 von 24 Werten sind gegen Zählen, Transfermatrix oder Stück 12 geprüft und gleich. "
        "Kleinste Farbenzahl mit mindestens einer Färbung: Dreieck 3, K4 4, Kreis C6 2, Petersen-Graph 3, Gitter 3×3 2, Gitter 4×4 2. Petersen-Graph: 120, 12.960, 332.880 Färbungen mit drei, vier und fünf Farben (Stück 12).")


def test_reliability_verdict_exact():
    assert ev.verdict_reliability(ev.reliability_rows()) == ("success",
        "Die exakte Zuverlässigkeit steigt mit p und liegt bei allen 9 Zufallsziehungen im Rahmen (Schwelle: Betrag von z höchstens 4; größter Betrag von z: 2,04). Beim 6×6-Gitter mit p = 0,9: exakt 0,935088, in 30.000 Ziehungen 0,93550. "
        "Das Ziehen ist der Schätzer (Stück 15), das Polynom die Wahrheit.")


def test_play_verdict_exact():
    assert ev.verdict_play(ev.play_graph(C.PLAY_EDGES_DEFAULT)) == ("success",
        "4 Knoten, 4 Kanten: T(x, y) = x³ + x² + xy; 3 Spannbäume, 12 azyklische Orientierungen; P(k) = k⁴ − 4k³ + 5k² − 2k. Gleich der Teilmengensumme über alle Kantenmengen.")


def test_verdicts_turn_into_errors_when_a_check_fails():
    rows = [dict(r) for r in ev.dc_rows()]
    rows[0]["gleich"] = False
    assert ev.verdict_dc(rows)[0] == "error"
    rows = [dict(r) for r in ev.dc_rows()]
    rows[1]["Blätter"] += 1
    assert ev.verdict_dc(rows)[0] == "error"
    fr = [dict(r) for r in ev.frontier_rows()]
    fr[0]["Zustände"] += 1
    assert ev.verdict_frontier(fr)[0] == "error"
    col = [dict(r) for r in ev.color_rows()]
    col[0] = {**col[0], "Prüfung": {2: ("Zählen aller Färbungen", "weicht ab"), 3: ("x", "gleich"), 4: ("x", "gleich"), 5: ("x", "gleich")}}
    assert ev.verdict_colors(col)[0] == "error"
    rel = [dict(r) for r in ev.reliability_rows()]
    rel[0] = {**rel[0], "Ziehungen": [{**rel[0]["Ziehungen"][0], "z": 6.0}] + rel[0]["Ziehungen"][1:]}
    assert ev.verdict_reliability(rel)[0] == "error"
    bad_play = ev.play_graph(C.PLAY_EDGES_DEFAULT) | {"ok": False}
    assert ev.verdict_play(bad_play)[0] == "error"
