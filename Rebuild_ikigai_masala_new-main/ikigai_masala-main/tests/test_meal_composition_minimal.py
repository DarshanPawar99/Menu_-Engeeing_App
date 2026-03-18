"""
Minimal tests for meal_composition module wiring.
"""

from src.meal_composition import MealStructure, MealType, CompositionLoader
from src.meal_composition.meal_structure import CourseRequirement


def test_meal_composition_exports():
    assert MealStructure is not None
    assert MealType is not None
    assert CompositionLoader is not None


def test_meal_structure_basic_validation():
    structure = MealStructure(
        meal_type=MealType.LUNCH,
        client_id="test_client",
        course_requirements=[CourseRequirement("main")]
    )
    assert structure.validate() is True


def test_composition_loader_from_dict_minimal():
    loader = CompositionLoader()
    data = {
        "client_id": "test_client",
        "meals": [
            {
                "meal_type": "lunch",
                "course_requirements": [
                    {"course_type": "main", "required": True, "alternatives": []}
                ]
            }
        ]
    }
    structures = loader.load_from_dict(data)
    assert "lunch" in structures
    assert structures["lunch"].client_id == "test_client"
