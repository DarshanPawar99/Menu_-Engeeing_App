"""
Integration-style tests to verify cuisine menu rules via MenuSolver.
"""

import pandas as pd

from src.menu_rules import CuisineMenuRule
from src.meal_composition import CompositionLoader
from src.solver.menu_solver import MenuSolver


def _build_menu_data_single_cuisine(cuisine_family: str) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"item_id": 1, "item_name": "item_one", "course_type": "main", "cuisine_family": cuisine_family},
            {"item_id": 2, "item_name": "item_two", "course_type": "main", "cuisine_family": cuisine_family},
        ]
    )


def _build_menu_data_two_courses(italian_main_only: bool = False) -> pd.DataFrame:
    rows = [
        {"item_id": 1, "item_name": "starter_indian", "course_type": "starter", "cuisine_family": "indian"},
        {"item_id": 2, "item_name": "starter_thai", "course_type": "starter", "cuisine_family": "thai"},
    ]
    if italian_main_only:
        rows.extend(
            [
                {"item_id": 3, "item_name": "main_italian", "course_type": "main", "cuisine_family": "italian"},
                {"item_id": 4, "item_name": "main_italian_2", "course_type": "main", "cuisine_family": "italian"},
            ]
        )
    else:
        rows.extend(
            [
                {"item_id": 3, "item_name": "main_italian", "course_type": "main", "cuisine_family": "italian"},
                {"item_id": 4, "item_name": "main_indian", "course_type": "main", "cuisine_family": "indian"},
            ]
        )
    return pd.DataFrame(rows)




def _build_meal_structure(course_types=("main",)):
    loader = CompositionLoader()
    course_requirements = []
    for course_type in course_types:
        course_requirements.append(
            {
                "course_type": course_type,
                "required": True,
                "alternatives": []
            }
        )
    data = {
        "client_id": "test_client",
        "meals": [
            {
                "meal_type": "lunch",
                "course_requirements": course_requirements
            }
        ]
    }
    return loader.load_from_dict(data)["lunch"]


def _solve(menu_data, meal_structure, rule, planning_config):
    solver = MenuSolver(
        menu_data=menu_data,
        meal_structure=meal_structure,
        menu_rules=[rule],
        planning_config=planning_config
    )
    return solver.solve(time_limit_seconds=5)


def _by_course(items):
    return {item["course_type"]: item for item in items}


def test_cuisine_rule_applies_on_monday_single_cuisine():
    menu_data = _build_menu_data_single_cuisine("italian")
    meal_structure = _build_meal_structure()
    rule = CuisineMenuRule(
        {
            "name": "italian_on_monday",
            "type": "cuisine",
            "cuisine_family": "italian",
            "days_of_week": ["monday"]
        }
    )
    planning_config = {
        "start_date": "2026-02-02",  # Monday
        "num_days": 2,
        "include_weekends": True,
        "menu_history": {}
    }

    solution = _solve(menu_data, meal_structure, rule, planning_config)
    assert solution is not None
    monday_items = solution["menu_plan"]["2026-02-02"]
    assert monday_items
    assert all(item["cuisine_family"] == "italian" for item in monday_items)


def test_cuisine_rule_applies_on_wednesday_single_cuisine():
    menu_data = _build_menu_data_single_cuisine("thai")
    meal_structure = _build_meal_structure()
    rule = CuisineMenuRule(
        {
            "name": "thai_on_wednesday",
            "type": "cuisine",
            "cuisine_family": "thai",
            "days_of_week": ["wednesday"]
        }
    )
    planning_config = {
        "start_date": "2026-02-04",  # Wednesday
        "num_days": 1,
        "include_weekends": True,
        "menu_history": {}
    }

    solution = _solve(menu_data, meal_structure, rule, planning_config)
    assert solution is not None
    wednesday_items = solution["menu_plan"]["2026-02-04"]
    assert wednesday_items
    assert all(item["cuisine_family"] == "thai" for item in wednesday_items)


def test_cuisine_rule_fallback_when_course_has_no_cuisine_items():
    menu_data = _build_menu_data_two_courses(italian_main_only=True)
    meal_structure = _build_meal_structure(course_types=("starter", "main"))
    rule = CuisineMenuRule(
        {
            "name": "italian_on_monday",
            "type": "cuisine",
            "cuisine_family": "italian",
            "days_of_week": ["monday"]
        }
    )
    planning_config = {
        "start_date": "2026-02-02",  # Monday
        "num_days": 1,
        "include_weekends": True,
        "menu_history": {}
    }

    solution = _solve(menu_data, meal_structure, rule, planning_config)
    assert solution is not None
    monday_items = solution["menu_plan"]["2026-02-02"]
    selected = _by_course(monday_items)
    assert selected["main"]["cuisine_family"] == "italian"
    assert selected["starter"]["cuisine_family"] != "italian"


def test_cuisine_rule_skips_when_day_not_in_rule():
    menu_data = _build_menu_data_two_courses()
    meal_structure = _build_meal_structure(course_types=("starter", "main"))
    rule = CuisineMenuRule(
        {
            "name": "italian_on_tuesday",
            "type": "cuisine",
            "cuisine_family": "italian",
            "days_of_week": ["tuesday"]
        }
    )
    planning_config = {
        "start_date": "2026-02-02",  # Monday
        "num_days": 1,
        "include_weekends": True,
        "menu_history": {}
    }

    solution = _solve(menu_data, meal_structure, rule, planning_config)
    assert solution is not None
    monday_items = solution["menu_plan"]["2026-02-02"]
    selected = _by_course(monday_items)
    assert set(selected.keys()) == {"starter", "main"}


def test_cuisine_rule_no_items_for_cuisine_is_graceful():
    menu_data = _build_menu_data_two_courses()
    meal_structure = _build_meal_structure(course_types=("starter", "main"))
    rule = CuisineMenuRule(
        {
            "name": "french_on_monday",
            "type": "cuisine",
            "cuisine_family": "french",
            "days_of_week": ["monday"]
        }
    )
    planning_config = {
        "start_date": "2026-02-02",  # Monday
        "num_days": 1,
        "include_weekends": True,
        "menu_history": {}
    }

    solution = _solve(menu_data, meal_structure, rule, planning_config)
    assert solution is not None
    monday_items = solution["menu_plan"]["2026-02-02"]
    assert monday_items


def test_cuisine_rule_ignored_when_weekends_excluded():
    menu_data = _build_menu_data_two_courses()
    meal_structure = _build_meal_structure(course_types=("starter", "main"))
    rule = CuisineMenuRule(
        {
            "name": "italian_on_saturday",
            "type": "cuisine",
            "cuisine_family": "italian",
            "days_of_week": ["saturday"]
        }
    )
    planning_config = {
        "start_date": "2026-02-07",  # Saturday
        "num_days": 1,
        "include_weekends": False,
        "menu_history": {}
    }

    solution = _solve(menu_data, meal_structure, rule, planning_config)
    assert solution is not None
    assert list(solution["menu_plan"].keys()) == ["2026-02-09"]
