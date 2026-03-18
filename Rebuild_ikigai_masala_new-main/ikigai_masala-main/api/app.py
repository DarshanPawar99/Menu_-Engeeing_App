"""
Flask API Application for Ikigai Masala Menu Planning System

This provides a REST API with automatic Swagger UI documentation
using flask-openapi3.
"""

import traceback
import json
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from flask_openapi3 import OpenAPI, Info, Tag
from flask_cors import CORS
from pydantic import ValidationError

from api.models import MenuPlanRequest, MenuPlanResponse, ErrorResponse
from api.config import (
    DEFAULT_EXCEL_PATH,
    PROCESSED_DATA_DIR,
    OUTPUT_DIR,
    DEFAULT_TIME_LIMIT_SECONDS,
    API_HOST,
    API_PORT,
    DEBUG
)
from src.preprocessor import ExcelReader, DataCleanser, DataSerializer
from src.menu_rules import MenuRuleLoader
from src.meal_composition import CompositionLoader
from src.solver import MenuSolver, SolutionFormatter


# OpenAPI Info
info = Info(
    title="Ikigai Masala Menu Planning API",
    version="1.0.0",
    description="API for automated menu planning with constraint solving"
)

# Create Flask-OpenAPI3 app
app = OpenAPI(__name__, info=info)

# Enable CORS for all origins
CORS(app, resources={r"/*": {"origins": "*"}})

# Define API tags
menu_tag = Tag(name="Menu Planning", description="Endpoints for menu planning operations")
health_tag = Tag(name="Health", description="Health check endpoints")


def preprocess_menu_data(excel_path: str = None, force_refresh: bool = False) -> tuple:
    """
    Preprocess menu data from Excel file.
    
    Args:
        excel_path: Path to Excel file with menu data (uses default if None)
        force_refresh: Force re-processing even if processed data exists
        
    Returns:
        Tuple of (menu_data DataFrame, metadata)
    """
    if excel_path is None:
        excel_path = DEFAULT_EXCEL_PATH
    
    serializer = DataSerializer(output_dir=PROCESSED_DATA_DIR)
    
    # Try to load existing processed data
    if not force_refresh:
        try:
            menu_data, metadata = serializer.load_latest("menu_data")
            return menu_data, metadata
        except FileNotFoundError:
            pass
    
    # Process from Excel
    reader = ExcelReader(excel_path)
    raw_data = reader.read()
    
    # Validate schema
    validation = reader.validate_schema()
    if not validation['valid']:
        raise ValueError(f"Invalid Excel schema: {validation['error']}")
    
    # Clean the data
    cleanser = DataCleanser(raw_data)
    cleaned_data = cleanser.clean()
    
    # Serialize for future use
    serializer.serialize(cleaned_data, "menu_data")
    
    # Return cleaned data with simple metadata
    metadata = {
        'row_count': len(cleaned_data),
        'columns': list(cleaned_data.columns),
        'source': excel_path
    }
    
    return cleaned_data, metadata


def load_menu_rules_from_dict(rules_data: Any):
    """
    Load and validate menu rules from dictionary/JSON data.
    
    Args:
        rules_data: Menu rules as dictionary or list of rule dictionaries
        
    Returns:
        List of menu rule objects
    """
    # Create a temporary file to use MenuRuleLoader
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        # Handle both list and dict with 'rules' key
        if isinstance(rules_data, list):
            json.dump({"rules": rules_data}, f)
        elif isinstance(rules_data, dict) and 'rules' in rules_data:
            json.dump(rules_data, f)
        else:
            # Assume it's a dict that needs to be wrapped
            json.dump({"rules": [rules_data]}, f)
        temp_path = f.name
    
    try:
        loader = MenuRuleLoader(temp_path)
        rules = loader.load_from_file()
        
        # Validate each rule
        invalid_rules = [r for r in rules if not r.validate_config()]
        if invalid_rules:
            raise ValueError(f"Invalid menu rules found: {[r.name for r in invalid_rules]}")
        
        return rules
    finally:
        # Clean up temp file
        Path(temp_path).unlink(missing_ok=True)


def load_meal_composition_from_dict(composition_data: Dict[str, Any]):
    """
    Load and validate meal composition from dictionary/JSON data.
    
    Args:
        composition_data: Meal composition as dictionary
        
    Returns:
        Dictionary of meal structures
    """
    # Create a temporary file to use CompositionLoader
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(composition_data, f)
        temp_path = f.name
    
    try:
        loader = CompositionLoader(temp_path)
        meal_structures = loader.load_from_file()
        
        # Validate each meal structure
        invalid_structures = {k: v for k, v in meal_structures.items() if not v.validate()}
        if invalid_structures:
            raise ValueError(f"Invalid meal structures found: {list(invalid_structures.keys())}")
        
        return meal_structures
    finally:
        # Clean up temp file
        Path(temp_path).unlink(missing_ok=True)


def solve_menu_plan(menu_data, meal_structure, menu_rules, planning_config, time_limit: int = 300) -> Dict[str, Any]:
    """
    Solve the menu planning problem.
    
    Args:
        menu_data: DataFrame with menu items
        meal_structure: MealStructure object
        menu_rules: List of menu rules
        planning_config: Configuration for planning (dates, etc.)
        time_limit: Solver time limit in seconds
        
    Returns:
        Solution dictionary with CSV data as JSON
    """
    import pandas as pd
    import csv
    
    solver = MenuSolver(
        menu_data=menu_data,
        meal_structure=meal_structure,
        menu_rules=menu_rules,
        planning_config=planning_config
    )
    
    solution = solver.solve(time_limit_seconds=time_limit)
    
    if not solution:
        return None
    
    # Format solution
    formatter = SolutionFormatter(solution)
    
    # Create output directory
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Export to CSV (pivot format: courses × dates)
    csv_path = output_dir / f"menu_plan_{timestamp}.csv"
    formatter.to_csv(str(csv_path), meal_structure)
    
    # Also export Excel for archival purposes (but don't return path)
    excel_path = output_dir / f"menu_plan_detailed_{timestamp}.xlsx"
    formatter.to_excel(str(excel_path))
    
    # Convert solution to structured JSON format that supports multiple items per course
    # The solution has structure: {'menu_plan': {date: [items]}, 'statistics': {...}}
    from collections import defaultdict
    
    menu_plan = solution.get('menu_plan', {})
    
    # Build item lookup dictionary
    item_lookup = {}
    
    # Group items by date and course
    menu_by_date = defaultdict(lambda: defaultdict(list))
    
    for date, items in menu_plan.items():
        for item in items:
            item_id = item.get('item_id', 'unknown')
            course = item.get('course_type', 'unknown')
            
            # Add to lookup if not already present
            if item_id not in item_lookup:
                item_lookup[item_id] = {
                    'item_name': item.get('item_name', 'Unknown Item'),
                    'course_type': item.get('course_type', 'unknown'),
                    'cuisine_family': item.get('cuisine_family', 'unknown'),
                    'item_color': item.get('item_color', 'unknown')
                }
            
            # Store item_id instead of item_name
            menu_by_date[date][course].append(item_id)
    
    # Get course order from meal structure
    course_types = [req.course_type for req in meal_structure.course_requirements]
    
    # Convert to list of dictionaries
    json_data = []
    for date in sorted(menu_by_date.keys()):
        day_menu = {'date': date}
        # Add courses in consistent order (based on meal structure)
        for course in course_types:
            if course in menu_by_date[date]:
                day_menu[course] = menu_by_date[date][course]
            else:
                day_menu[course] = []
        json_data.append(day_menu)
    
    return {
        'json_data': json_data,
        'item_lookup': item_lookup
    }


@app.post(
    "/api/v1/plan",
    tags=[menu_tag],
    responses={
        200: MenuPlanResponse,
        400: ErrorResponse,
        500: ErrorResponse
    },
    summary="Generate Menu Plan",
    description="Generate a menu plan based on the provided configuration. "
                "This endpoint processes menu data, applies rules and composition constraints, "
                "and solves for an optimal menu plan."
)
def plan_menu(body: MenuPlanRequest):
    """
    Generate a menu plan.
    
    This endpoint accepts configuration for menu planning and returns
    a solved menu plan with assignments for each date and course.
    """
    try:
        # Step 1: Preprocess menu data (from server-side Excel file)
        menu_data, metadata = preprocess_menu_data(
            excel_path=None,  # Use default from config
            force_refresh=body.force_refresh
        )
        
        # Step 2: Load menu rules from request JSON
        menu_rules = load_menu_rules_from_dict(body.menu_rules)
        
        # Step 3: Load meal composition from request JSON
        meal_structures = load_meal_composition_from_dict(body.meal_composition)
        
        # Get the requested meal structure
        meal_structure = meal_structures.get(body.meal_type)
        if not meal_structure:
            return ErrorResponse(
                error=f"No meal structure defined for '{body.meal_type}'",
                details=f"Available meal types: {list(meal_structures.keys())}"
            ).model_dump(), 400
        
        # Step 4: Prepare planning configuration
        planning_config = {
            'start_date': body.start_date,
            'num_days': body.num_days,
            'meal_type': body.meal_type,
            'include_weekends': body.include_weekends,
            'menu_history': {}  # Could be extended to load from database
        }
        
        # Step 5: Solve the menu planning problem
        result = solve_menu_plan(
            menu_data=menu_data,
            meal_structure=meal_structure,
            menu_rules=menu_rules,
            planning_config=planning_config,
            time_limit=body.time_limit_seconds
        )
        
        if result:
            return MenuPlanResponse(
                success=True,
                message="Menu plan generated successfully",
                solution=result['json_data'],
                item_lookup=result['item_lookup']
            ).model_dump(), 200
        else:
            return MenuPlanResponse(
                success=False,
                message="No solution found. Try relaxing constraints or adding more menu items.",
                solution=None,
                item_lookup=None
            ).model_dump(), 200
        
    except FileNotFoundError as e:
        return ErrorResponse(
            error="File not found",
            details=str(e)
        ).model_dump(), 400
        
    except ValueError as e:
        return ErrorResponse(
            error="Validation error",
            details=str(e)
        ).model_dump(), 400
        
    except ValidationError as e:
        return ErrorResponse(
            error="Request validation error",
            details=str(e)
        ).model_dump(), 400
        
    except Exception as e:
        return ErrorResponse(
            error="Internal server error",
            details=f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        ).model_dump(), 500


@app.get(
    "/api/v1/health",
    tags=[health_tag],
    responses={200: {"description": "Service is healthy"}},
    summary="Health Check",
    description="Check if the API service is running and responsive"
)
def health_check():
    """
    Health check endpoint.
    
    Returns basic service status and version information.
    """
    return {
        "status": "healthy",
        "service": "Ikigai Masala Menu Planning API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }, 200


@app.get(
    "/",
    tags=[health_tag],
    responses={200: {"description": "API information"}},
    summary="API Information",
    description="Get basic API information and available endpoints"
)
def root():
    """
    Root endpoint with API information.
    """
    return {
        "name": "Ikigai Masala Menu Planning API",
        "version": "1.0.0",
        "documentation": "/openapi/swagger",
        "endpoints": {
            "plan": "/api/v1/plan",
            "health": "/api/v1/health"
        }
    }, 200


if __name__ == "__main__":
    # Run the development server
    app.run(
        host=API_HOST,
        port=API_PORT,
        debug=DEBUG
    )
