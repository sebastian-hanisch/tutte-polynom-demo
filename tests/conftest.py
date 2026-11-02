"""Gemeinsame Fixtures: die Mini-Instanzen, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def triangle():
    """Dreieck, Knoten 0, 1, 2. T = x² + x + y (zwei Kanten bilden einen Spannbaum: 3 Spannbäume; die dritte Kante schließt den Kreis), P(k) = k(k−1)(k−2), 3! = 6 azyklische Orientierungen.
    Zuverlässigkeit bei p = 1/3: verbunden, wenn mindestens zwei Kanten halten: 3 · (1/3)² · (2/3) + (1/3)³ = 6/27 + 1/27 = 7/27. Flüsse mit Werten aus Z_k: derselbe Wert c ≠ 0 rundherum (ein Kreis), also F(k) = k − 1, bei k = 3 zwei, bei k = 2 einer."""
    return {"n": 3, "edges": [(0, 1), (1, 2), (0, 2)], "T": {(2, 0): 1, (1, 0): 1, (0, 1): 1}, "trees": 3, "coeffs": [0, 2, -3, 1], "acyclic": 6, "R_third": (7, 27), "flows_3": 2}


@pytest.fixture
def square():
    """Viereck C4: T = x³ + x² + x + y; P(k) = (k−1)⁴ + (k−1), also P(3) = 16 + 2 = 18; 4 Spannbäume; 2⁴ − 2 = 14 azyklische Orientierungen."""
    return {"n": 4, "edges": [(0, 1), (1, 2), (2, 3), (0, 3)], "T": {(3, 0): 1, (2, 0): 1, (1, 0): 1, (0, 1): 1}, "P3": 18, "trees": 4, "acyclic": 14}


@pytest.fixture
def k4():
    """K4: T = x³ + 3x² + 2x + 4xy + 2y + 3y² + y³ (aus dem Gedächtnis, durch die Teilmengensumme bestätigt); 16 Spannbäume (4²), 24 = 4! azyklische Orientierungen, P(k) = k(k−1)(k−2)(k−3), F(4) = 6."""
    T = {(3, 0): 1, (2, 0): 3, (1, 0): 2, (1, 1): 4, (0, 1): 2, (0, 2): 3, (0, 3): 1}
    return {"n": 4, "edges": [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)], "T": T, "trees": 16, "acyclic": 24, "P4": 24, "F4": 6}


@pytest.fixture
def tiny():
    """Kleinste Fälle: eine Kante (Brücke) T = x; eine Schleife T = y; zwei parallele Kanten T = x + y; ein Weg mit drei Kanten T = x³."""
    return {"bridge": (2, [(0, 1)], {(1, 0): 1}), "loop": (1, [(0, 0)], {(0, 1): 1}), "parallel": (2, [(0, 1), (0, 1)], {(1, 0): 1, (0, 1): 1}), "path": (4, [(0, 1), (1, 2), (2, 3)], {(3, 0): 1})}
