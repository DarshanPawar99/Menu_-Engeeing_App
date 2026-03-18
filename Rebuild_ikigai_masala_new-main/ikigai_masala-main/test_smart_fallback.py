"""
Test script to demonstrate the smart fallback mechanism for cuisine rules.

This script simulates a scenario where certain cuisine items are missing
for specific course types, demonstrating how the system relaxes constraints
intelligently.
"""

import pandas as pd
from ortools.sat.python import cp_model

from src.menu_rules import CuisineMenuRule
from src.meal_composition import MealStructure, MealType
from src.meal_composition.meal_structure import CourseRequirement

def create_test_menu_data():
    """Create test menu data with intentionally missing items"""
    data = {
        'item_id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'item_name': [
            'dosa', 'idli', 'sambhar', 'rasam', 'chicken_curry',
            'roti', 'dal', 'sabzi', 'paneer', 'biryani'
        ],
        'course_type': [
            'bread', 'bread', 'dal', 'dal', 'nonveg_main',
            'bread', 'dal', 'veg_dry', 'veg_gravy', 'rice'
        ],
        'cuisine_family': [
            'south_indian', 'south_indian', 'south_indian', 'south_indian', 'south_indian',
            'north_indian', 'north_indian', 'north_indian', 'north_indian', 'north_indian'
        ]
    }
    return pd.DataFrame(data)

def test_smart_fallback_missing_course():
    """Test scenario where South Indian has no items for certain courses"""
    
    print("=" * 70)
    print("TEST: Smart Fallback for Missing Course Types")
    print("=" * 70)
    
    # Create menu data (South Indian missing veg_dry and rice)
    menu_df = create_test_menu_data()
    
    print("\nAvailable items:")
    print(menu_df[['item_name', 'course_type', 'cuisine_family']].to_string(index=False))
    
    print("\n" + "=" * 70)
    print("South Indian items by course:")
    south_indian = menu_df[menu_df['cuisine_family'] == 'south_indian']
    for course in ['bread', 'dal', 'nonveg_main', 'veg_dry', 'rice', 'veg_gravy']:
        count = len(south_indian[south_indian['course_type'] == course])
        status = "✓ Available" if count > 0 else "✗ MISSING"
        print(f"  {course:15}: {count} items {status}")
    
    # Create meal structure requiring all 6 courses
    meal_structure = MealStructure(
        meal_type=MealType.LUNCH,
        client_id='test',
        course_requirements=[
            CourseRequirement('bread'),
            CourseRequirement('dal'),
            CourseRequirement('nonveg_main'),
            CourseRequirement('veg_dry'),
            CourseRequirement('rice'),
            CourseRequirement('veg_gravy'),
        ]
    )
    
    # Create cuisine rule for South Indian on Monday
    rule_config = {
        'name': 'south_indian_monday',
        'type': 'cuisine',
        'cuisine_family': 'south_indian',
        'days_of_week': ['monday']
    }
    
    rule = CuisineMenuRule(rule_config)
    
    # Setup model and variables
    model = cp_model.CpModel()
    variables = {'daily_items': {}}
    
    date_key = '2026-01-19'
    variables['daily_items'][date_key] = {}
    
    for idx, row in menu_df.iterrows():
        item_id = row['item_id']
        var = model.NewBoolVar(f'item_{item_id}_day_{date_key}')
        variables['daily_items'][date_key][item_id] = var
    
    # Build context with meal structure
    context = {
        'planning_dates': [
            {'date': '2026-01-19', 'day_name': 'monday'}
        ],
        'meal_structure': meal_structure
    }
    
    print("\n" + "=" * 70)
    print("Applying South Indian cuisine rule with smart fallback...")
    print("=" * 70)
    
    # Apply the rule
    rule.apply(model, variables, menu_df, context)
    
    print("\n" + "=" * 70)
    print("EXPECTED BEHAVIOR:")
    print("=" * 70)
    print("✓ South Indian constraint applied to: bread, dal, nonveg_main")
    print("⚠  Constraint relaxed for: veg_dry, rice, veg_gravy (no South Indian items)")
    print("  → These courses can use any cuisine (North Indian in this case)")
    print("\nThis ensures a feasible solution while maximizing cuisine adherence!")
    print("=" * 70)

if __name__ == '__main__':
    test_smart_fallback_missing_course()
