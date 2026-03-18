"""
Pydantic models for API request/response validation
"""

from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field, validator


class MenuPlanRequest(BaseModel):
    """Request model for menu planning endpoint"""
    
    menu_rules: Union[List[Dict[str, Any]], Dict[str, Any]] = Field(
        description='Menu rules configuration as JSON object or array of rules'
    )
    
    meal_composition: Dict[str, Any] = Field(
        description='Meal composition configuration as JSON object with meal structures'
    )
    
    meal_type: str = Field(
        default='lunch',
        description='Type of meal to plan for (must match a key in meal_composition)',
        pattern='^[a-z_]+$'
    )
    
    start_date: Optional[str] = Field(
        default=None,
        description='Start date for planning (YYYY-MM-DD format). Defaults to today.'
    )
    
    num_days: int = Field(
        default=7,
        ge=1,
        le=90,
        description='Number of days to plan (1-90)'
    )
    
    include_weekends: bool = Field(
        default=True,
        description='Include Saturday and Sunday in planning dates'
    )
    
    force_refresh: bool = Field(
        default=False,
        description='Force re-processing of Excel data'
    )
    
    time_limit_seconds: int = Field(
        default=300,
        ge=10,
        le=600,
        description='Solver time limit in seconds (10-600)'
    )
    
    @validator('start_date')
    def validate_start_date(cls, v):
        if v is None:
            return datetime.now().strftime('%Y-%m-%d')
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('start_date must be in YYYY-MM-DD format')
    
    @validator('meal_type')
    def validate_meal_type_lowercase(cls, v):
        return v.lower()
    
    class Config:
        json_schema_extra = {
            "example": {
                "menu_rules": [
                    {
                        "rule_type": "cuisine_variety",
                        "enabled": True,
                        "config": {
                            "applicable_courses": ["rice", "dal"],
                            "min_days_gap": 2
                        }
                    }
                ],
                "meal_composition": {
                    "meals": [
                        {
                            "meal_type": "lunch",
                            "course_requirements": [
                                {
                                    "course_type": "rice"
                                },
                                {
                                    "course_type": "dal"
                                }
                            ]
                        }
                    ]
                },
                "meal_type": "lunch",
                "start_date": "2026-02-05",
                "num_days": 7,
                "include_weekends": True,
                "force_refresh": False,
                "time_limit_seconds": 300
            }
        }


class MenuPlanResponse(BaseModel):
    """Response model for menu planning endpoint"""
    
    success: bool = Field(description='Whether the solver found a solution')
    
    message: str = Field(description='Status message')
    
    solution: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description='Menu plan solution as JSON format. Each object represents a date with courses as keys and arrays of item IDs as values. Supports multiple items per course.'
    )
    
    item_lookup: Optional[Dict[str, Dict[str, str]]] = Field(
        default=None,
        description='Lookup dictionary mapping item_id to item details (item_name, course_type, cuisine_family, item_color)'
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Menu plan generated successfully",
                "solution": [
                    {
                        "date": "2026-02-05",
                        "rice": ["RICE001"],
                        "dal": ["DAL001"],
                        "bread": ["BREAD001", "BREAD002"],
                        "veg_dry": ["VEG001"],
                        "veg_gravy": ["VEG002"],
                        "nonveg_main": ["NONVEG001"]
                    },
                    {
                        "date": "2026-02-06",
                        "rice": ["RICE002"],
                        "dal": ["DAL002"],
                        "bread": ["BREAD003"],
                        "veg_dry": ["VEG003"],
                        "veg_gravy": ["VEG004"],
                        "nonveg_main": ["NONVEG002"]
                    }
                ],
                "item_lookup": {
                    "RICE001": {
                        "item_name": "Jeera Rice",
                        "course_type": "rice",
                        "cuisine_family": "north_indian",
                        "item_color": "white"
                    },
                    "DAL001": {
                        "item_name": "Moong Dal Tadka",
                        "course_type": "dal",
                        "cuisine_family": "north_indian",
                        "item_color": "yellow"
                    },
                    "BREAD001": {
                        "item_name": "Roti",
                        "course_type": "bread",
                        "cuisine_family": "north_indian",
                        "item_color": "brown"
                    }
                }
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    
    success: bool = Field(default=False, description='Always False for errors')
    error: str = Field(description='Error message')
    details: Optional[str] = Field(default=None, description='Detailed error information')
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "Invalid configuration",
                "details": "Menu rules file not found"
            }
        }
