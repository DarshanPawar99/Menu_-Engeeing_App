"""
Meal structure definition
"""

from enum import Enum
from typing import Dict, List, Any
from dataclasses import dataclass, field


class MealType(Enum):
    """Types of meals"""
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


@dataclass
class CourseRequirement:
    """
    Defines requirements for a course type in a meal.
    
    Attributes:
        course_type: Type of course (e.g., "starter", "main", "rice")
    """
    course_type: str
    
    def __repr__(self):
        return f"CourseRequirement({self.course_type})"


@dataclass
class MealStructure:
    """
    Defines the structure and composition of a meal.
    
    A meal structure specifies what courses should be included.
    
    Example:
        Lunch structure:
        - bread
        - veg_dry
        - rice
        - veg_gravy
        - nonveg_main
        - dal
    """
    meal_type: MealType
    client_id: str
    course_requirements: List[CourseRequirement]
    special_rules: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Calculate total items needed"""
        pass  # No calculations needed with simplified structure
    
    def get_course_requirement(self, course_type: str) -> CourseRequirement:
        """
        Get requirement for a specific course type.
        
        Args:
            course_type: Course type to look up
            
        Returns:
            CourseRequirement object or None
        """
        for req in self.course_requirements:
            if req.course_type.lower() == course_type.lower():
                return req
        return None
    
    def validate(self) -> bool:
        """
        Validate the meal structure configuration.
        
        Returns:
            True if valid, False otherwise
        """
        if not self.course_requirements:
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert meal structure to dictionary format.
        
        Returns:
            Dictionary representation
        """
        return {
            'meal_type': self.meal_type.value,
            'client_id': self.client_id,
            'course_requirements': [
                {
                    'course_type': req.course_type
                }
                for req in self.course_requirements
            ],
            'special_rules': self.special_rules
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MealStructure':
        """
        Create MealStructure from dictionary.
        
        Args:
            data: Dictionary containing meal structure data
            
        Returns:
            MealStructure object
        """
        meal_type = MealType(data['meal_type'])
        client_id = data.get('client_id', 'default')
        
        course_requirements = [
            CourseRequirement(
                course_type=req['course_type']
            )
            for req in data.get('course_requirements', [])
        ]
        
        return cls(
            meal_type=meal_type,
            client_id=client_id,
            course_requirements=course_requirements,
            special_rules=data.get('special_rules', {})
        )
    
    def __repr__(self):
        return f"MealStructure({self.meal_type.value} for {self.client_id}: {len(self.course_requirements)} courses)"
