"""
Ikigai Masala - Menu Planning System
Main entry point for the application
"""

import argparse
from datetime import datetime
from pathlib import Path

from src.preprocessor import ExcelReader, DataCleanser, DataSerializer
from src.menu_rules import MenuRuleLoader
from src.meal_composition import CompositionLoader
from src.solver import MenuSolver, SolutionFormatter


def preprocess_menu_data(excel_path: str, force_refresh: bool = False) -> tuple:
    """
    Preprocess menu data from Excel file.
    
    Args:
        excel_path: Path to Excel file with menu data
        force_refresh: Force re-processing even if processed data exists
        
    Returns:
        Tuple of (menu_data DataFrame, metadata)
    """
    serializer = DataSerializer(output_dir="data/processed")
    
    # Try to load existing processed data
    if not force_refresh:
        try:
            menu_data, metadata = serializer.load_latest("menu_data")
            print(f"Loaded existing processed data: {len(menu_data)} items")
            return menu_data, metadata
        except FileNotFoundError:
            print("No existing processed data found. Processing from Excel...")
    
    # Process from Excel
    print(f"\nReading menu data from {excel_path}...")
    reader = ExcelReader(excel_path)
    raw_data = reader.read()
    
    # Validate schema
    validation = reader.validate_schema()
    if not validation['valid']:
        raise ValueError(f"Invalid Excel schema: {validation['error']}")
    
    print(f"Schema validation passed: {validation['row_count']} rows")
    
    # Clean the data
    print("\nCleaning data...")
    cleanser = DataCleanser(raw_data)
    cleaned_data = cleanser.clean()
    
    # Serialize for future use
    print("\nSerializing processed data...")
    serializer.serialize(cleaned_data, "menu_data")
    
    # Return cleaned data with simple metadata
    metadata = {
        'row_count': len(cleaned_data),
        'columns': list(cleaned_data.columns),
        'source': excel_path
    }
    
    return cleaned_data, metadata


def load_menu_rules(rules_path: str):
    """
    Load and validate menu rules from JSON file.
    
    Args:
        rules_path: Path to menu rules JSON file
        
    Returns:
        List of menu rule objects
    """
    print(f"\nLoading menu rules from {rules_path}...")
    
    # Load menu rules (validation is done during loading)
    loader = MenuRuleLoader(rules_path)
    rules = loader.load_from_file()
    
    # Validate each rule
    invalid_rules = [r for r in rules if not r.validate_config()]
    if invalid_rules:
        print("Invalid menu rules found:")
        for rule in invalid_rules:
            print(f"  - {rule.name}")
        raise ValueError("Invalid menu rule configuration")
    
    print(f"Loaded {len(rules)} menu rules")
    for rule in rules:
        print(f"  - {rule.get_description()}")
    
    return rules


def load_meal_composition(composition_path: str):
    """
    Load and validate meal composition from JSON file.
    
    Args:
        composition_path: Path to meal composition JSON file
        
    Returns:
        Dictionary of meal structures
    """
    print(f"\nLoading meal composition from {composition_path}...")
    
    # Load meal structures (validation is done during loading)
    loader = CompositionLoader(composition_path)
    meal_structures = loader.load_from_file()
    
    # Validate each meal structure
    invalid_structures = {k: v for k, v in meal_structures.items() if not v.validate()}
    if invalid_structures:
        print("Invalid meal structures found:")
        for meal_type in invalid_structures.keys():
            print(f"  - {meal_type}")
        raise ValueError("Invalid meal composition configuration")
    
    print(f"Loaded {len(meal_structures)} meal structures")
    for meal_type, structure in meal_structures.items():
        print(f"  - {meal_type}: {len(structure.course_requirements)} courses")
    
    return meal_structures


def solve_menu_plan(menu_data, meal_structure, menu_rules, planning_config):
    """
    Solve the menu planning problem.
    
    Args:
        menu_data: DataFrame with menu items
        meal_structure: MealStructure object
        menu_rules: List of menu rules
        planning_config: Configuration for planning (dates, etc.)
        
    Returns:
        Solution dictionary
    """
    print("\n" + "=" * 60)
    print("STARTING MENU PLANNING SOLVER")
    print("=" * 60)
    
    solver = MenuSolver(
        menu_data=menu_data,
        meal_structure=meal_structure,
        menu_rules=menu_rules,
        planning_config=planning_config
    )
    
    solution = solver.solve(time_limit_seconds=300)
    
    if solution:
        print("\n" + "=" * 60)
        print("SOLUTION FOUND!")
        print("=" * 60)
        
        # Format and display solution
        formatter = SolutionFormatter(solution)
        formatter.print_summary()
        
        # Export to files
        output_dir = Path("data/outputs")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export to CSV (pivot format: courses × dates)
        csv_path = output_dir / f"menu_plan_{timestamp}.csv"
        formatter.to_csv(str(csv_path), meal_structure)
        
        # Also export detailed Excel for reference
        excel_path = output_dir / f"menu_plan_detailed_{timestamp}.xlsx"
        formatter.to_excel(str(excel_path))
        
        return solution
    else:
        print("\nNo solution found. Try:")
        print("  1. Relaxing some constraints")
        print("  2. Adding more menu items")
        print("  3. Adjusting meal composition requirements")
        return None


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Ikigai Masala - Menu Planning System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Plan Indian lunch for next 7 days (uses defaults)
  python main.py --start-date 2026-01-27 --days 7
  
  # Force refresh of menu data
  python main.py --force-refresh --days 7
  
  # Plan for specific date range
  python main.py --start-date 2026-02-01 --days 30
        """
    )
    
    parser.add_argument(
        '--excel',
        type=str,
        default='data/raw/menu_items.xlsx',
        help='Path to Excel file with menu data'
    )
    
    parser.add_argument(
        '--menu-rules',
        type=str,
        default='data/configs/indian_menu_rules.json',
        help='Path to menu rules JSON file'
    )
    
    parser.add_argument(
        '--composition',
        type=str,
        default='data/configs/indian_lunch_composition.json',
        help='Path to meal composition JSON file'
    )
    
    parser.add_argument(
        '--meal-type',
        type=str,
        default='lunch',
        choices=['breakfast', 'lunch', 'dinner', 'snack'],
        help='Type of meal to plan for'
    )
    
    parser.add_argument(
        '--start-date',
        type=str,
        default=datetime.now().strftime('%Y-%m-%d'),
        help='Start date for planning (YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days to plan'
    )

    parser.add_argument(
        '--include-weekends',
        action=argparse.BooleanOptionalAction,
        default=True,
        help='Include Saturday and Sunday in planning dates'
    )
    
    parser.add_argument(
        '--force-refresh',
        action='store_true',
        help='Force re-processing of Excel data'
    )
    
    args = parser.parse_args()
    
    try:
        # Step 1: Preprocess menu data
        print("\n" + "=" * 60)
        print("STEP 1: DATA PREPROCESSING")
        print("=" * 60)
        menu_data, metadata = preprocess_menu_data(args.excel, args.force_refresh)
        
        # Step 2: Load menu rules
        print("\n" + "=" * 60)
        print("STEP 2: LOADING MENU RULES")
        print("=" * 60)
        menu_rules = load_menu_rules(args.menu_rules)
        
        # Step 3: Load meal composition
        print("\n" + "=" * 60)
        print("STEP 3: LOADING MEAL COMPOSITION")
        print("=" * 60)
        meal_structures = load_meal_composition(args.composition)
        
        # Get the requested meal structure
        meal_structure = meal_structures.get(args.meal_type)
        if not meal_structure:
            raise ValueError(f"No meal structure defined for '{args.meal_type}'")
        
        # Step 4: Prepare planning configuration
        planning_config = {
            'start_date': args.start_date,
            'num_days': args.days,
            'meal_type': args.meal_type,
            'include_weekends': args.include_weekends,
            'menu_history': {}  # Could load from database
        }
        
        # Step 5: Solve the menu planning problem
        print("\n" + "=" * 60)
        print("STEP 4: SOLVING MENU PLAN")
        print("=" * 60)
        solution = solve_menu_plan(
            menu_data=menu_data,
            meal_structure=meal_structure,
            menu_rules=menu_rules,
            planning_config=planning_config
        )
        
        if solution:
            print("\n✓ Menu planning completed successfully!")
        else:
            print("\n✗ Menu planning failed. No solution found.")
            return 1
        
        return 0
        
    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
        print("\nMake sure all required files exist:")
        print(f"  - Excel file: {args.excel}")
        print(f"  - Menu Rules: {args.menu_rules}")
        print(f"  - Composition: {args.composition}")
        return 1
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
