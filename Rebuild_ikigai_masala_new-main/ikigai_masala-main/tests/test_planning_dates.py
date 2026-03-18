"""
Tests for planning date generation in MenuSolver.
"""

import pandas as pd

from src.solver.menu_solver import MenuSolver
from src.meal_composition import MealStructure, MealType
from src.meal_composition.meal_structure import CourseRequirement


def _build_solver(planning_config):
    menu_data = pd.DataFrame([
        {"item_id": 1, "course_type": "main"}
    ])
    meal_structure = MealStructure(
        meal_type=MealType.LUNCH,
        client_id="test_client",
        course_requirements=[CourseRequirement("main")]
    )
    return MenuSolver(
        menu_data=menu_data,
        meal_structure=meal_structure,
        menu_rules=[],
        planning_config=planning_config
    )


def test_planning_dates_excludes_weekends():
    planning_config = {
        "start_date": "2026-01-30",  # Friday
        "num_days": 4,
        "include_weekends": False,
        "menu_history": {}
    }
    solver = _build_solver(planning_config)
    dates = solver._get_planning_dates()

    assert [d["day_name"] for d in dates] == ["friday", "monday", "tuesday", "wednesday"]
    assert [d["date"] for d in dates] == ["2026-01-30", "2026-02-02", "2026-02-03", "2026-02-04"]
    assert [d["day_number"] for d in dates] == [0, 1, 2, 3]
