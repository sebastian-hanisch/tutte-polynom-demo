# Tutte- und chromatisches Polynom – ein Polynom, viele Zahlen – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-tutte-polynom-demo.streamlit.app/)** -->

Stück 14 von 16 der Reihe **„Abzählen und erzeugende Funktionen“** in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“ (die Linie wird erst vollständig veröffentlicht; Stück 14 war als gelb markiert und wurde nach Stück 13 zum Bauen entschieden). Vorgänger sind `aufzaehlen-rekursion-demo` (Stück 1), `rationale-ef-demo` (Stück 2), `symbolische-methode-demo` (Stück 3), `semiring-rekursion-demo` (Stück 4), `multimengen-partitionen-demo` (Stück 5), `beschriftete-strukturen-demo` (Stück 6), `siebformel-demo` (Stück 7), `zaehlen-nach-parameter-demo` (Stück 8), `asymptotik-demo` (Stück 9), `gleichverteilt-ziehen-demo` (Stück 10), `burnside-polya-demo` (Stück 11), `isomorphieausschluss-demo` (Stück 12) und `frontier-diagramm-demo` (Stück 13); das letzte hat ein **Diagramm** gebaut und darauf **Zahlen** ausgewertet. Diese Demo wertet auf demselben Diagramm ein **Polynom** aus: das **Tutte-Polynom** T(x, y), aus dem Spannbäume, Färbungen (das chromatische Polynom), Flüsse, azyklische Orientierungen und die **Zuverlässigkeit** eines Graphen als Einsetzungen folgen. **Deletion–Contraction** (Kante löschen oder zusammenziehen) definiert es, die Frontier-Rechnung mit einem Polynom als Wert berechnet es, und jede Zahl wird gegen einen unabhängigen Weg geprüft.

## Warum dieses Problem

Wer wissen will, wie viele Spannbäume ein Netz hat, wie viele Färbungen mit k Farben, wie viele azyklische Orientierungen und wie wahrscheinlich es zusammenhängend bleibt, wenn jede Verbindung nur mit Wahrscheinlichkeit p hält, rechnet normalerweise fünf verschiedene Dinge. Das Tutte-Polynom rechnet **eines**: ein Polynom in zwei Veränderlichen, dessen Werte an fünf Stellen diese fünf Zahlen sind. Die Demo zeigt, wie man es berechnet, dass die Zustände dieselben sind wie bei den Spannbäumen in Stück 13, und wo es endet.

## Befunde und Korrekturen gegenüber dem Plan

- **Hook bestätigt und verbunden:** Das 6×6-Gitter (60 Kanten, 2^60 Teilmengen) braucht 6.001 Zustände und liefert ein Polynom mit 430 Monomen; daraus 32.565.539.635.200 Spannbäume, 101.596.896 Dreifärbungen und 39.931.856.138.212.664 azyklische Orientierungen. Die Zustandszahlen (6.001, 27.645 beim 7×7-Gitter) sind **genau** die der Spannbaum-Diagramme aus Stück 13; nur der Wert ist ein Polynom statt einer Zahl.
- **Blätter gleich Spannbäume:** Deletion–Contraction hat mit Schleifen- und Brückenregel genau T(1, 1) Blätter, nicht 2^m: beim 4×4-Gitter 100.352 statt 16.777.216; mit Zusammenfassen gleicher Teilgraphen (nach Umbenennung, ohne Isomorphietest) braucht das 5×5-Gitter 242.898 Aufrufe statt 557.568.000 Blättern.
- **Die größte Schicht ist eine Catalan-Zahl:** bei den quadratischen Gittern 3×3 bis 7×7 gleich 5, 14, 42, 132, 429 (gemessen, nicht bewiesen; 1.430 beim 8×8-Gitter aus Phase 0).
- **Die Kantenordnung entscheidet wie in Stück 13:** dasselbe Gitter hat als 3×8 (Frontier 9) 17.657 Zustände, als 8×3 (Frontier 4) nur 171, mit demselben Polynom.
- **Zuverlässigkeit mit 30.000 statt 100.000 Ziehungen:** die App zieht je Punkt 30.000-mal (schneller); der größte Betrag von z liegt bei 2,04.
- **Eigene Fehler im Bau (nicht in der Messung):** (1) Ein Handwert war falsch: das Dreieck hat F(k) = k − 1 nirgends verschwindende Flüsse mit Werten aus Z_k, nicht (k−1)(k−2); das Aufzählen aller Flüsse im Test fand es (k = 2 gibt einen Fluss, nicht keinen). (2) Der Name „Kreis C6“ fiel in den Zweig für „K…“ (vollständige Graphen); der erste App-Lauf fand es. (3) Der Plan nannte das Polynom des Dreiecks mit Anhang x⁴ + x³ + xy; richtig ist x³ + x² + xy (Brücke mal Dreieck). (4) Pipe-Zeichen in der Grenzentabelle hätten die Tabellenzellen zerrissen. (5) „1 Zustände“ statt „1 Zustand“ im Urteilstext (der Randfall mit einer Kante fand es).
- **Präfix `tpl_`, Port 9327.**

## Modell

**Graphen:** `(n, Kanten)` mit Knoten 0 bis n − 1; Mehrfachkanten und Schleifen sind erlaubt. Gitter (zeilen- oder spaltenweise), Petersen-Graph, vollständige Graphen, Kreise und eigene Kantenlisten (`parse_edge_list`: „1-2, 2-3, 1-3“, Knoten 1 bis 9, höchstens 20 Kanten, zusammenhängend).

**Frontier-Rechnung (`frontier_tutte`):** Die Kanten werden der Reihe nach entschieden. Der **Zustand** sind die Zusammenhangsklassen der Frontier-Knoten, der **Wert** ein Wörterbuch {(Verschmelzungen k, Kreiskanten e): Zahl der Teilmengen}: eine gewählte Kante zwischen zwei Klassen erhöht k, eine innerhalb einer Klasse e. Am Ende ist T = Σ Zahl · (x−1)^(r(E)−k) · (y−1)^e. **Deletion–Contraction (`tutte_dc`):** T(G) = T(G−e) + T(G/e), Brücke x · T(G/e), Schleife y · T(G−e); mit einem Speicher gleiche Teilgraphen zusammengefasst.

**Einsetzungen:** Spannbäume T(1,1), Wälder T(2,1), zusammenhängende Teilgraphen T(1,2), azyklische Orientierungen T(2,0), 2^m = T(2,2); Färbungen P(G,k) = (−1)^(n−c) k^c T(1−k, 0) (`chromatic_value`, `chromatic_coefficients`); Flüsse F(G,k) = (−1)^(m−n+c) T(0, 1−k); Zuverlässigkeit p^(n−c) (1−p)^(m−n+c) T(1, 1/(1−p)) in Brüchen.

**Prüfwege:** `tutte_subsets` (Teilmengensumme über alle 2^m Kantenmengen), `kirchhoff` (Determinante in Brüchen), `colorings_brute`, `grid_colorings` (Zeilen-Transfermatrix), `acyclic_orientations_brute`, `reliability_brute` (Brüche), `reliability_sample` (Zufallsziehen mit festem Seed), `flows_brute`; dazu Stanleys Satz (|P(−1)| = T(2,0)) als zweiter Auswertungspunkt desselben Polynoms.

## Methodik

- **Prüfungen in der App:** Spannbäume gegen Kirchhoff; Färbungen gegen Zählen, Transfermatrix oder die Zahlen aus Stück 12; Orientierungen gegen Aufzählen (bis 12 Kanten) oder Stanley; Wälder und zusammenhängende Teilgraphen gegen die Teilmengensumme (bis 15 Kanten); das ganze Polynom gegen Teilmengensumme und Deletion–Contraction (bis 27 Kanten); Flüsse gegen Aufzählen; Zuverlässigkeit gegen Aufzählen (bis 12 Kanten) oder Zufallsziehen. Ein Widerspruch ist ein Fehler.
- **Eingabe:** Graph (fünf), Zeilen und Spalten (bis 7), Knoten (vollständiger Graph bis K7, Kreis ab 3), Kantenordnung (nur Gitter), eigene Kantenliste, Farbenzahl (1 bis 12), Haltewahrscheinlichkeit (1 bis 99 Prozent). Die Adresszeile spiegelt die Einstellung.
- **Fünf Experimente:** (1) Deletion–Contraction ohne und mit Zusammenfassen, (2) ein Polynom, viele Zahlen, (3) Frontier im Polynom-Semiring (Zustände, Catalan-Zahlen, Ordnung), (4) das chromatische Polynom, (5) Zuverlässigkeit exakt gegen Zufallsziehen. Dazu eine Spielwiese: eine eigene Kantenliste mit Polynom, Spannbäumen und P(k). Alles ist deterministisch bis auf das Zufallsziehen mit festem Seed 20261102.

## Befunde (gemessen, keine Behauptungen)

Jede Zahl steht in `tests/test_claims.py`, `tests/test_algorithm.py`, `tests/test_verdicts.py` oder `tests/test_oracle_tpl.py`. Zeiten stehen in keinem Test.

| Frage | Befund |
|---|---|
| Handinstanzen | Dreieck: T = x² + x + y, 3 Spannbäume, P(k) = k³ − 3k² + 2k, 6 azyklische Orientierungen, Zuverlässigkeit bei p = 1/3: 7/27, F(k) = k − 1; Viereck: T = x³ + x² + x + y, 4 Spannbäume, P(3) = 18, 14 Orientierungen; K4: T = x³ + 3x² + 2x + 4xy + 2y + 3y² + y³, 16 Spannbäume, P(4) = 24, 24 Orientierungen, F(4) = 6 |
| Deletion–Contraction: Gitter, Kanten, Spannbäume (= Blätter), Aufrufe ohne / mit Zusammenfassen, Frontier-Zustände | 2×2: 4, 4, 14 / 11, 7; 2×3: 7, 15, 66 / 33, 21; 3×3: 12, 192, 851 / 132, 46; 2×5: 13, 209, 1.214 / 141, 151; 3×4: 17, 2.415, 12.065 / 574, 153; 4×4: 24, 100.352, 497.030 / 3.418, 251; 3×6: 27, 380.160, – / 5.992, 1.649; 5×5: 40, 557.568.000, – / 242.898, 1.259 |
| Frontier im Polynom-Semiring: größte Schicht (Catalan-Zahl), Summe der Zustände, Monome | 3×3: 5, 46, 21; 4×4: 14, 251, 73; 5×5: 42, 1.259, 194; 6×6: 132, 6.001, 430; 7×7: 429, 27.645, 839; 8×8 (Phase 0, nicht in der App): 1.430, 124.329, 1.491; 3×8: 1.341, 17.657, 171; 8×3: 5, 171, 171 |
| Gitter (Spannbäume, Wälder, zusammenhängende Teilgraphen, azyklische Orientierungen, P(3), P(4)) | 3×3: 192, 3.102, 431, 2.398, 246, 9.612; 4×4: 100.352, 8.790.016, 555.195, 5.015.972, 7.812, 6.000.732; 6×6: 32.565.539.635.200, 181.075.508.242.067.552, 2.692.324.030.864.335, 39.931.856.138.212.664, 101.596.896, 380.053.267.505.964 |
| Andere Graphen (Spannbäume, Wälder, zusammenhängende Teilgraphen, Orientierungen) | K4: 16, 38, 38, 24; K5: 125, 291, 728, 120; Kreis C6: 6, 63, 7, 62 (P(3) = 66, P(4) = 732); Petersen-Graph: 2.000, 22.292, 5.968, 16.680 |
| Petersen-Graph | 26 Monome; P(3), P(4), P(5) = 120, 12.960, 332.880 (gleich Stück 12); F(2) = F(3) = F(4) = 0 und F(5) = 240 (aus dem Gedächtnis); P(k) = k¹⁰ − 15k⁹ + 105k⁸ − 455k⁷ + 1353k⁶ − 2861k⁵ + 4275k⁴ − 4305k³ + 2606k² − 704k |
| Färbungen mit zwei bis fünf Farben | Dreieck 0, 6, 24, 60; K4 0, 0, 24, 120; Kreis C6 2, 66, 732, 4.100; Petersen 0, 120, 12.960, 332.880; Gitter 3×3 2, 246, 9.612, 142.820; Gitter 4×4 2, 7.812, 6.000.732, 828.850.160; kleinste Farbenzahl mit einer Färbung 3, 4, 2, 3, 2, 2 |
| Zuverlässigkeit exakt (Ziehungen mit 30.000 Zügen), p = 0,5 / 0,9 / 0,99 | Gitter 4×4: 0,033092 (0,0333) / 0,944085 (0,9443) / 0,999584 (0,9996); Gitter 6×6: 0,002335 (0,00237) / 0,935088 (0,9355) / 0,999576 (0,99933); Petersen: 0,182129 (0,18) / 0,988567 (0,9891) / 0,99999 (1,0); größter Betrag von z: 2,04 |
| Zuverlässigkeit gegen Aufzählen (Brüche) | Dreieck bei p = 1/3: 7/27; Kreis C5 bei p = 1/2: 6/32; Pfad mit vier Kanten: p⁴ |
| Spielwiese | 1-2, 2-3, 3-1, 3-4: T = x³ + x² + xy, 3 Spannbäume, 12 azyklische Orientierungen, P(k) = k⁴ − 4k³ + 5k² − 2k |

## Ehrliche Grenzen

- **Literaturwerte aus dem Gedächtnis:** Tutte-Polynom und seine Auswertungen (Tutte 1954; Stanley 1973 für azyklische Orientierungen), das Flusspolynom des Petersen-Graphen (F(5) = 240), die #P-Härte (Jaeger, Vertigan, Welsh) und Knuths Frontier-Methode wurden nicht an einer Quelle gelesen. Teilmengensumme, Deletion–Contraction, Kirchhoff, Zählen und Aufzählen stützen die Ausgaben; das K4-Polynom stand aus dem Gedächtnis im Plan und stimmt mit der Teilmengensumme überein.
- **Einfaches Zusammenfassen:** Deletion–Contraction fasst nur nach Umbenennung gleiche Teilgraphen zusammen, nicht isomorphe; ein Isomorphietest würde mehr sparen und kostet selbst.
- **Gitter und kleine Graphen:** gemessen sind Gitter, Petersen-Graph, vollständige Graphen und Kreise; allgemeine Graphen brauchen eine Kantenordnung (hier die der Liste) und haben andere Frontiers. Das Tutte-Polynom ist im Allgemeinen #P-schwer; die Rechnung ist exponentiell in der Frontierbreite.
- **Prüfwege nur klein:** Zählen aller Färbungen bis 300.000 Zuordnungen, Aufzählen von Orientierungen und Kantenzuständen bis 12 Kanten, Teilmengensumme bis 15, Deletion–Contraction bis 27 Kanten; darüber Kirchhoff, Transfermatrix, Stanley und Zufallsziehen.
- **Unabhängige Kanten:** die Zuverlässigkeit setzt gleiche, unabhängige Haltewahrscheinlichkeiten voraus.
- **Aufwand als Zustände und Aufrufe**, nicht als Zeit; der erste Aufruf braucht etwa eine halbe Minute, weil die Experimente einmal rechnen (danach zwischengespeichert; das 8×8-Gitter braucht in Python etwa 26 Sekunden und ist deshalb nicht in der App).
- **Browser:** Seitentext, Zahlen, Diagrammbreiten, Preset-Klick im Browser geprüft; Handy-Breite nicht.
- Alles gerechnet, keine echten Daten.

## Verifikation

- **Kern:** Handinstanzen (Dreieck, Viereck, K4, Brücke, Schleife, parallele Kanten, Weg) für Polynom, Spannbäume, P(k), Orientierungen, Zuverlässigkeit, Flüsse und die Aufrufe der Rekursion; Frontier gleich Teilmengensumme gleich Deletion–Contraction (mit und ohne Zusammenfassen) auf 80 zufälligen Multigraphen mit Schleifen und mehreren Komponenten; Spannbäume gegen Kirchhoff, Färbungen gegen Zählen aller Färbungen, Orientierungen gegen Aufzählen, Flüsse gegen Aufzählen, Zuverlässigkeit gegen Aufzählen in Brüchen, Gitterfärbungen gegen die Transfermatrix, Petersen-Graph gegen Zählen, Kirchhoff und Stück 12.
- **Eigenschaften:** nichtnegative ganze Koeffizienten; unabhängig von Kanten- und Knotenreihenfolge; Gitter und Transponiertes gleich; Produkt bei disjunkter Vereinigung und bei Gelenkknoten; geschlossene Formen für Bäume, Kreise und vollständige Graphen (Cayley, n!); chromatisches Polynom: Koeffizient von k^(n−1) gleich −m, wechselnde Vorzeichen; Flusspolynom von K4 und Kreisen; Zuverlässigkeit wächst mit p; Zustände je Schicht höchstens Bell-Zahl der Frontierbreite; größte Schicht quadratischer Gitter gleich Catalan-Zahl; Zustandssummen gleich Stück 13; Zusammenfassen braucht weniger Aufrufe.
- **Randfälle:** 1×1 wird 1×2, Größen über den Grenzen, vollständiger Graph und Kreis außerhalb ihrer Größen, unbekannter Graph und Ordnung, Farbenzahl und Wahrscheinlichkeit außerhalb der Regler, eine Farbe, Kantenlisten mit Müll (acht Fälle) mit Rückfall und Hinweis, Schleifen und Mehrfachkanten, die langsamen Prüfwege nur bei kleinen Graphen, Auswahl des Prüfwegs für die Färbungen, Formatierung.
- **Urteilstexte:** genauer Wortlaut für alle Voreinstellungen und Experimente, Einzahlformen, Fehlerfälle.
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler an Minimum und Maximum), jedes Preset, jeder Graph, Permalink mit Müll, Spielwiese (auch mit Fehler), PDF für jeden Graphen, eindeutige Diagrammschlüssel; Footer-Test; Layout-Test.
- **Nicht gemacht:** Mutationstests (seit 2026-10-28 nicht mehr verlangt), Docker-Lauf der Linux-CI (Docker fehlt auf diesem Rechner; die CI nach dem Push entscheidet).

137 Tests (`pytest tests`).

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App: Ergebnis, Kernfrage, fünf Experimente, Spielwiese, Grenzen, Formeln |
| `tpl_algorithm.py` | Kern: Graphen, Frontier-Rechnung im Polynom-Semiring, Deletion–Contraction, Einsetzungen, Prüfwege |
| `tpl_constants.py` | Regler-Grenzen, Grenzen der Prüfwege, Experiment-Konstanten, Farben, Presets |
| `tpl_evaluation.py` | Analyse, Experimente, Urteilstexte, Formatierung |
| `tpl_layout.py` | Fester Kopf (Stylesheet) |
| `tpl_pdf_export.py` | PDF des aktuellen Graphen (fpdf2) |
| `tpl_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben) |
| `tpl_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Handwerte, Orakel, Eigenschaften, Randfälle, Urteilstexte, Claims, Presets, Layout, AppTest, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Schwierige Auswertungspunkte:** Ising- und Potts-Modell, Jones-Polynom, Approximation des Tutte-Polynoms (Jerrum, Sinclair): nur genannt.
- **Baumzerlegungen und Pfadbreite:** Verweis auf die Härte-Linie; hier gilt nur die Frontierbreite der gegebenen Kantenordnung.
- **Matroide:** das Tutte-Polynom ist für Matroide definiert, hier nur Graphen.
- **Isomorphietest beim Zusammenfassen, Kantenordnung suchen:** nur genannt.
- **Schätzen, wo das Zählen aufhört:** Stück 15; hier steht das Zufallsziehen nur als Gegenprobe der Zuverlässigkeit.
- **Verwandte Demos:** `graph-coloring-demo` (Greedy, DSATUR, exakt: die chromatische Zahl, nicht die Zahl der Färbungen), `random-spanning-tree-demo` (Kirchhoff und Wilson), `frontier-diagramm-demo` (das Diagramm), `siebformel-demo` (die Siebformel hinter dem chromatischen Polynom), `burnside-polya-demo` und `isomorphieausschluss-demo` (Färbungen des Petersen-Graphen als Bahnen); nur Verweise.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

Streamlit Cloud: Python-Version nach der Voreinstellung der Plattform (lokal `3.14`, CI `3.12`); der Code nutzt nur Merkmale, die in `3.12` laufen.

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und fpdf2.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
