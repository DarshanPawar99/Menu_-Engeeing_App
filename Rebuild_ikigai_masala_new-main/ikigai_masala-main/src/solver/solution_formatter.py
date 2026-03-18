"""
Solution formatter for presenting menu plans - MVP Version
"""

import pandas as pd
from typing import Dict, Any


class SolutionFormatter:
    """
    Formats menu planning solutions for various output formats.
    Simplified MVP version focusing on clean CSV output.
    """
    
    def __init__(self, solution: Dict[str, Any]):
        """
        Initialize the formatter with a solution.
        
        Args:
            solution: Solution dictionary from MenuSolver
        """
        self.solution = solution
        
    def print_summary(self) -> None:
        """
        Print a brief summary of the solution to console.
        """
        print("\n" + "=" * 60)
        print("MENU PLAN SOLUTION")
        print("=" * 60)
        
        stats = self.solution.get('statistics', {})
        print(f"\nStatus: {stats.get('status', 'UNKNOWN')}")
        print(f"Solve Time: {stats.get('solve_time', 0):.2f}s")
        
        menu_plan = self.solution.get('menu_plan', {})
        print(f"\n📅 Generated menu for {len(menu_plan)} days")
        print("=" * 60)
    
    def to_csv(self, output_path: str, meal_structure=None) -> None:
        """
        Export solution to CSV file in pivot format (courses as rows, dates as columns).
        Shows only the selected items per course as defined in meal composition.
        
        Args:
            output_path: Path to save the CSV file
            meal_structure: MealStructure object to get course order and requirements
        """
        menu_plan = self.solution.get('menu_plan', {})
        
        # Get all dates sorted
        dates = sorted(menu_plan.keys())
        
        # Determine course types from meal structure
        if meal_structure:
            # Use the order from meal composition (simplified: 1 item per course)
            course_info = {}
            for req in meal_structure.course_requirements:
                course_info[req.course_type] = {
                    'order': len(course_info),
                    'max_items': 1
                }
            course_types = [req.course_type for req in meal_structure.course_requirements]
        else:
            # Get unique course types from the solution
            course_types = set()
            for items in menu_plan.values():
                for item in items:
                    course_types.add(item.get('course_type', ''))
            course_types = sorted(course_types)
            course_info = {ct: {'order': i, 'max_items': 1} for i, ct in enumerate(course_types)}
        
        # Build the pivot data
        rows = []
        for course_type in course_types:
            row = {'Course': course_type.replace('_', ' ').title()}
            max_items = course_info.get(course_type, {}).get('max_items', 1)
            
            for date in dates:
                items = menu_plan[date]
                # Find items matching this course type
                matching_items = [
                    item for item in items 
                    if item.get('course_type', '') == course_type
                ]
                
                # Take only the required number of items (as per meal composition)
                if matching_items:
                    item_names = [
                        item.get('item_name', '').replace('_', ' ').title() 
                        for item in matching_items[:max_items]
                    ]
                    row[date] = ' | '.join(item_names) if len(item_names) > 1 else item_names[0] if item_names else ''
                else:
                    row[date] = ''
            
            rows.append(row)
        
        df = pd.DataFrame(rows)
        df.to_csv(output_path, index=False)
        
        print(f"\n{'=' * 60}")
        print(f"📊 Exported menu plan to {output_path}")
        print(f"   Format: Courses (rows) × Dates (columns)")
        print(f"   Courses: {len(course_types)}")
        print(f"   Days: {len(dates)}")
        print(f"{'=' * 60}")
    
    def to_excel(self, output_path: str) -> None:
        """
        Export detailed solution to Excel file (all items).
        
        Args:
            output_path: Path to save the Excel file
        """
        rows = []
        
        for date, items in self.solution.get('menu_plan', {}).items():
            for item in items:
                rows.append({
                    'date': date,
                    'item_id': item.get('item_id', ''),
                    'item_name': item.get('item_name', ''),
                    'course_type': item.get('course_type', ''),
                    'cuisine_family': item.get('cuisine_family', '')
                })
        
        df = pd.DataFrame(rows)
        df.to_excel(output_path, index=False)
        
        print(f"   Detailed data: {output_path}")
