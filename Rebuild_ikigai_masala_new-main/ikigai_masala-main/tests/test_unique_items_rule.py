"""
Dedicated tests for UniqueItemsMenuRule (positive and negative scenarios).
"""

import pandas as pd

from src.menu_rules import UniqueItemsMenuRule
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


def test_unique_items_positive_no_repetition_across_days():
    menu_data = pd.DataFrame(
        [
            {"item_id": 1, "item_name": "starter_a", "course_type": "starter", "cuisine_family": "indian", "item_color": "red"},
            {"item_id": 2, "item_name": "starter_b", "course_type": "starter", "cuisine_family": "indian", "item_color": "blue"},
            {"item_id": 3, "item_name": "main_a", "course_type": "main", "cuisine_family": "indian", "item_color": "red"},
            {"item_id": 4, "item_name": "main_b", "course_type": "main", "cuisine_family": "indian", "item_color": "blue"},
        ]
    )
    rule = UniqueItemsMenuRule(
        {
            "name": "unique_items_session",
            "type": "unique_items",
        }
    )
    planning_config = {
        "start_date": "2026-02-02",
        "num_days": 2,
        "include_weekends": True,
        "menu_history": {},
    }

    solution = _solve(menu_data, rule, planning_config)
    assert solution is not None

    day1_items = solution["menu_plan"]["2026-02-02"]
    day2_items = solution["menu_plan"]["2026-02-03"]
    day1_ids = {item["item_id"] for item in day1_items}
    day2_ids = {item["item_id"] for item in day2_items}

    assert day1_ids.isdisjoint(day2_ids)


def test_unique_items_negative_infeasible_when_insufficient_unique_items():
    menu_data = pd.DataFrame(
        [
            {"item_id": 10, "item_name": "starter_only", "course_type": "starter", "cuisine_family": "indian", "item_color": "red"},
            {"item_id": 20, "item_name": "main_only", "course_type": "main", "cuisine_family": "indian", "item_color": "blue"},
        ]
    )
    rule = UniqueItemsMenuRule(
        {
            "name": "unique_items_session",
            "type": "unique_items",
        }
    )
    planning_config = {
        "start_date": "2026-02-02",
        "num_days": 2,
        "include_weekends": True,
        "menu_history": {},
    }

    solution = _solve(menu_data, rule, planning_config)
    assert solution is None
