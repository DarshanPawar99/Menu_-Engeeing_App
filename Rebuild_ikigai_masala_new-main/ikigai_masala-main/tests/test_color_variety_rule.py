"""
Dedicated tests for ColorVarietyMenuRule (positive and negative scenarios).
"""

import pandas as pd

from src.menu_rules import ColorVarietyMenuRule
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
                    {"course_type": "dessert", "required": True, "alternatives": []},
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


def _distinct_colors(items):
    return {item["item_color"] for item in items}

def _print_solution(menu_data, rule, planning_config, solution):
    print("\n--- Color Variety Test ---")
    print("Menu data:")
    for _, row in menu_data.iterrows():
        print(
            f"- id={row['item_id']} name={row['item_name']} course={row['course_type']} "
            f"color={row['item_color']}"
        )
    print("Rule config:")
    print(rule.config)
    print("Planning config:")
    print(planning_config)

    if solution is None:
        print("Solution: None (infeasible)")
        return

    print("Solution:")
    for date, items in solution["menu_plan"].items():
        colors = sorted(_distinct_colors(items))
        print(f"- {date}: colors={colors}")
        for item in items:
            print(
                f"  - {item['course_type']}: {item['item_name']} "
                f"(color={item['item_color']})"
            )

def test_color_variety_positive_meets_min_distinct_colors():
    menu_data = pd.DataFrame(
        [
            {"item_id": 10, "item_name": "starter_red", "course_type": "starter", "cuisine_family": "indian", "item_color": "red"},
            {"item_id": 20, "item_name": "main_blue", "course_type": "main", "cuisine_family": "indian", "item_color": "blue"},
            {"item_id": 30, "item_name": "dessert_green", "course_type": "dessert", "cuisine_family": "indian", "item_color": "green"},
        ]
    )
    rule = ColorVarietyMenuRule(
        {
            "name": "daily_color_variety",
            "type": "color_variety",
            "min_distinct_colors": {
                "breakfast": 2,
                "lunch": 3,
                "dinner": 3,
                "snack": 1,
            },
        }
    )
    planning_config = {
        "start_date": "2026-02-02",
        "num_days": 1,
        "include_weekends": True,
        "menu_history": {},
    }

    solution = _solve(menu_data, rule, planning_config)
    _print_solution(menu_data, rule, planning_config, solution)
    assert solution is not None
    items = solution["menu_plan"]["2026-02-02"]
    assert len(_distinct_colors(items)) >= 3


def test_color_variety_negative_infeasible_when_insufficient_colors():
    menu_data = pd.DataFrame(
        [
            {"item_id": 10, "item_name": "starter_red", "course_type": "starter", "cuisine_family": "indian", "item_color": "red"},
            {"item_id": 20, "item_name": "main_red", "course_type": "main", "cuisine_family": "indian", "item_color": "red"},
            {"item_id": 30, "item_name": "dessert_blue", "course_type": "dessert", "cuisine_family": "indian", "item_color": "blue"},
        ]
    )
    rule = ColorVarietyMenuRule(
        {
            "name": "daily_color_variety",
            "type": "color_variety",
            "min_distinct_colors": {
                "breakfast": 2,
                "lunch": 3,
                "dinner": 3,
                "snack": 1,
            },
        }
    )
    planning_config = {
        "start_date": "2026-02-02",
        "num_days": 1,
        "include_weekends": True,
        "menu_history": {},
    }

    solution = _solve(menu_data, rule, planning_config)
    _print_solution(menu_data, rule, planning_config, solution)
    assert solution is None
