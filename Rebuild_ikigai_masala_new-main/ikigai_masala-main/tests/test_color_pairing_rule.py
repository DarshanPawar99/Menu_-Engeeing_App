"""
Dedicated tests for ColorPairingMenuRule (positive and negative scenarios).
"""

import pandas as pd

from src.menu_rules import ColorPairingMenuRule
from src.meal_composition import CompositionLoader
from src.solver.menu_solver import MenuSolver


def _build_meal_structure():
    loader = CompositionLoader()
    data = {
        "client_id": "test_client",
        "meals": [
            {
                "meal_type": "lunch",
                "course_requirements": [
                    {"course_type": "starter", "required": True, "alternatives": []},
                    {"course_type": "main", "required": True, "alternatives": []},
                ],
            }
        ],
    }
    return loader.load_from_dict(data)["lunch"]


def _solve(menu_data, rule, planning_config):
    solver = MenuSolver(
        menu_data=menu_data,
        meal_structure=_build_meal_structure(),
        menu_rules=[rule],
        planning_config=planning_config,
    )
    return solver.solve(time_limit_seconds=5)


def _by_course(items):
    return {item["course_type"]: item for item in items}


def test_color_pairing_positive_prevents_same_color():
    menu_data = pd.DataFrame(
        [
            {"item_id": 10, "item_name": "starter_red", "course_type": "starter", "cuisine_family": "indian", "item_color": "red"},
            {"item_id": 11, "item_name": "starter_blue", "course_type": "starter", "cuisine_family": "indian", "item_color": "blue"},
            {"item_id": 20, "item_name": "main_red", "course_type": "main", "cuisine_family": "indian", "item_color": "red"},
            {"item_id": 21, "item_name": "main_blue", "course_type": "main", "cuisine_family": "indian", "item_color": "blue"},
        ]
    )
    rule = ColorPairingMenuRule(
        {
            "name": "starter_main_color_mismatch",
            "type": "color_pairing",
            "course_type_a": "starter",
            "course_type_b": "main",
        }
    )
    planning_config = {
        "start_date": "2026-02-02",
        "num_days": 1,
        "include_weekends": True,
        "menu_history": {},
    }

    solution = _solve(menu_data, rule, planning_config)
    assert solution is not None
    items = solution["menu_plan"]["2026-02-02"]
    selected = _by_course(items)
    assert selected["starter"]["item_color"] != selected["main"]["item_color"]


def test_color_pairing_negative_infeasible_when_only_same_color():
    menu_data = pd.DataFrame(
        [
            {"item_id": 30, "item_name": "starter_red", "course_type": "starter", "cuisine_family": "indian", "item_color": "red"},
            {"item_id": 40, "item_name": "main_red", "course_type": "main", "cuisine_family": "indian", "item_color": "red"},
        ]
    )
    rule = ColorPairingMenuRule(
        {
            "name": "starter_main_color_mismatch",
            "type": "color_pairing",
            "course_type_a": "starter",
            "course_type_b": "main",
        }
    )
    planning_config = {
        "start_date": "2026-02-02",
        "num_days": 1,
        "include_weekends": True,
        "menu_history": {},
    }

    solution = _solve(menu_data, rule, planning_config)
    assert solution is None
