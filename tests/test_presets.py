"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, jedes Preset zeigt etwas anderes."""

import tpl_algorithm as A
import tpl_constants as C
import tpl_evaluation as ev
import tpl_presets as P


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_regler_bounds():
    for name, preset in C.PRESETS.items():
        assert preset["graph"] in C.GRAPHS and preset["order"] in C.ORDERS, name
        for field, key in P.PRESET_KEYS.items():
            lo, hi = P.SETTING_SPECS[key].lo, P.SETTING_SPECS[key].hi
            if lo is not None:
                assert lo <= preset[field] <= hi, (name, field)
        assert len(preset["edges"]) <= C.EDGES_MAX_LEN


def test_default_preset_equals_default_settings_and_comes_first():
    first = next(iter(C.PRESETS.values()))
    for field, key in P.PRESET_KEYS.items():
        assert first[field] == P.SETTING_SPECS[key].default
    assert first["graph"] == C.DEFAULT_GRAPH and first["order"] == C.DEFAULT_ORDER


def test_every_preset_passes_the_checker_without_notes_or_problems():
    for name, preset in C.PRESETS.items():
        a = ev.analyse(ev.Settings(**preset))
        assert a.problems == [] and a.notes == [], name


def test_presets_differ_from_each_other_in_the_visible_fields():
    seen = set()
    for name, preset in C.PRESETS.items():
        a = ev.analyse(ev.Settings(**preset))
        key = (a.label, a.k, int(a.p * 100), a.order_key, tuple(A.parse_edge_list(preset["edges"])[1]) if preset["graph"] == "Eigene Kantenliste" else None)
        assert key not in seen, name
        seen.add(key)


def test_every_graph_kind_appears_in_a_preset():
    assert {p["graph"] for p in C.PRESETS.values()} == set(C.GRAPHS)


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)
    assert P.SETTING_SPECS["graph_select"].choices == C.GRAPHS and P.SETTING_SPECS["order_select"].choices == C.ORDERS and P.SETTING_SPECS["edges_input"].max_len == C.EDGES_MAX_LEN
