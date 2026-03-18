"""
Test script to verify the menu planning system
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported"""
    print("Testing module imports...")
    
    try:
        from src.preprocessor import ExcelReader, DataCleanser, DataSerializer
        print("  ✓ Preprocessor module")
        
        from src.menu_rules import (
            BaseMenuRule, 
            CuisineMenuRule,
            MenuRuleLoader
        )
        print("  ✓ Menu rules module")
        
        from src.meal_composition import MealStructure, MealType, CompositionLoader
        print("  ✓ Meal composition module")
        
        from src.solver import MenuSolver, SolutionFormatter
        print("  ✓ Solver module")
        
        from src.utils import ConfigValidator, DateUtils
        print("  ✓ Utils module")
        
        return True
        
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        return False


def test_config_validation():
    """Test configuration validation"""
    print("\nTesting configuration validation...")
    
    from src.utils import ConfigValidator
    
    # Test menu rules config
    rules_path = "examples/sample_menu_rules.json"
    if Path(rules_path).exists():
        is_valid, errors = ConfigValidator.validate_config_file(rules_path, 'menu_rule')
        if is_valid:
            print(f"  ✓ Menu rules config valid")
        else:
            print(f"  ✗ Menu rules config invalid: {errors}")
            return False
    else:
        print(f"  ⚠ Menu rules file not found: {rules_path}")
    
    # Test composition config
    composition_path = "examples/sample_meal_composition.json"
    if Path(composition_path).exists():
        is_valid, errors = ConfigValidator.validate_config_file(composition_path, 'composition')
        if is_valid:
            print(f"  ✓ Meal composition config valid")
        else:
            print(f"  ✗ Meal composition config invalid: {errors}")
            return False
    else:
        print(f"  ⚠ Composition file not found: {composition_path}")
    
    return True


def test_menu_rule_loading():
    """Test loading menu rules from JSON"""
    print("\nTesting menu rule loading...")
    
    from src.menu_rules import MenuRuleLoader
    
    try:
        loader = MenuRuleLoader("examples/sample_menu_rules.json")
        rules = loader.load_from_file()
        
        print(f"  ✓ Loaded {len(rules)} menu rules")
        
        for rule in rules[:3]:  # Show first 3
            print(f"    - {rule.name} ({rule.rule_type.value})")
        
        if len(rules) > 3:
            print(f"    ... and {len(rules) - 3} more")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error loading menu rules: {e}")
        return False


def test_composition_loading():
    """Test loading meal composition from JSON"""
    print("\nTesting meal composition loading...")
    
    from src.meal_composition import CompositionLoader
    
    try:
        loader = CompositionLoader("examples/sample_meal_composition.json")
        meal_structures = loader.load_from_file()
        
        print(f"  ✓ Loaded {len(meal_structures)} meal structures")
        
        for meal_type, structure in meal_structures.items():
            print(f"    - {meal_type}: {len(structure.course_requirements)} courses")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error loading meal composition: {e}")
        return False


def test_date_utils():
    """Test date utility functions"""
    print("\nTesting date utilities...")
    
    from src.utils import DateUtils
    
    try:
        # Generate date range
        dates = DateUtils.generate_date_range("2026-01-27", 7)
        print(f"  ✓ Generated {len(dates)} dates")
        
        # Get day of week
        day = DateUtils.get_day_of_week("2026-01-27")
        print(f"  ✓ 2026-01-27 is a {day}")
        
        # Days between
        gap = DateUtils.days_between("2026-01-27", "2026-02-03")
        print(f"  ✓ Days between: {gap}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error in date utils: {e}")
        return False


def check_sample_data():
    """Check if sample data exists"""
    print("\nChecking for sample data...")
    
    data_path = Path("data/raw/menu_items.xlsx")
    
    if data_path.exists():
        print(f"  ✓ Sample data exists: {data_path}")
        return True
    else:
        print(f"  ⚠ Sample data not found: {data_path}")
        print(f"    Run: python create_sample_data.py")
        return False


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("IKIGAI MASALA - SYSTEM TEST")
    print("=" * 60)
    
    results = {
        "Imports": test_imports(),
        "Config Validation": test_config_validation(),
        "Menu Rule Loading": test_menu_rule_loading(),
        "Composition Loading": test_composition_loading(),
        "Date Utils": test_date_utils(),
        "Sample Data": check_sample_data(),
    }
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:.<40} {status}")
    
    print("=" * 60)
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n✓ All tests passed!")
        print("\nNext steps:")
        print("  1. Create sample data: python create_sample_data.py")
        print("  2. Run the solver: python main.py")
        return 0
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
