"""
Menu planning solver using Google OR-Tools CP-SAT
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from ortools.sat.python import cp_model

from ..menu_rules.base_menu_rule import BaseMenuRule
from ..meal_composition.meal_structure import MealStructure


class MenuSolver:
    """
    Solves the menu planning problem using constraint programming.
    
    Uses Google OR-Tools CP-SAT solver to find optimal menu combinations
    that satisfy all menu rules and meal composition requirements.
    """
    
    def __init__(self, menu_data: pd.DataFrame, 
                 meal_structure: MealStructure,
                 menu_rules: List[BaseMenuRule],
                 planning_config: Dict[str, Any]):
        """
        Initialize the menu solver.
        
        Args:
            menu_data: DataFrame containing all available menu items
            meal_structure: MealStructure defining meal composition
            menu_rules: List of menu rule objects to apply
            planning_config: Configuration including dates, history, etc.
        """
        self.menu_data = menu_data
        self.meal_structure = meal_structure
        self.menu_rules = menu_rules
        self.planning_config = planning_config
        
        self.model = cp_model.CpModel()
        self.variables = {}
        self.solution = None
        
    def solve(self, time_limit_seconds: int = 300) -> Optional[Dict[str, Any]]:
        """
        Solve the menu planning problem.
        
        Args:
            time_limit_seconds: Maximum time to spend solving
            
        Returns:
            Dictionary containing the solution or None if no solution found
        """
        print(f"Starting menu planning solver...")
        print(f"  Menu items: {len(self.menu_data)}")
        print(f"  Meal type: {self.meal_structure.meal_type.value}")
        print(f"  Menu Rules: {len(self.menu_rules)}")
        
        # Create decision variables
        self._create_variables()
        
        # Apply meal composition constraints
        self._apply_meal_composition_constraints()
        
        # Apply all user-defined menu rules
        self._apply_menu_rules()
        
        # Set objective (optional - maximize variety, minimize cost, etc.)
        self._set_objective()
        
        # Solve the model
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = time_limit_seconds
        solver.parameters.log_search_progress = True
        
        print(f"\nSolving with time limit: {time_limit_seconds}s...")
        status = solver.Solve(self.model)
        
        # Process results
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            print(f"\n{'Optimal' if status == cp_model.OPTIMAL else 'Feasible'} solution found!")
            self.solution = self._extract_solution(solver, status)
            return self.solution
        else:
            print(f"\nNo solution found. Status: {solver.StatusName(status)}")
            return None
    
    def _create_variables(self) -> None:
        """
        Create decision variables for each menu item and day.
        
        Variables are binary: 1 if item is selected for a day, 0 otherwise.
        """
        planning_dates = self._get_planning_dates()
        
        self.variables['daily_items'] = {}
        
        for date_info in planning_dates:
            date = date_info['date']
            self.variables['daily_items'][date] = {}
            
            for _, item in self.menu_data.iterrows():
                item_id = item['item_id']
                var_name = f"item_{item_id}_day_{date}"
                
                # Binary variable: 1 if this item is selected for this day
                self.variables['daily_items'][date][item_id] = self.model.NewBoolVar(var_name)
        
        print(f"Created {len(planning_dates) * len(self.menu_data)} decision variables")
    
    def _apply_meal_composition_constraints(self) -> None:
        """
        Apply constraints based on meal composition structure.
        
        Ensures each day's menu has exactly 1 item from each course type.
        """
        for date, day_vars in self.variables['daily_items'].items():
            # Group items by course type
            course_items = self._group_items_by_course()
            
            for course_req in self.meal_structure.course_requirements:
                course_type = course_req.course_type
                
                if course_type not in course_items:
                    print(f"Warning: No items available for course '{course_type}'")
                    continue
                
                # Get variables for items of this course type
                course_vars = [
                    day_vars[item_id] for item_id in course_items[course_type]
                    if item_id in day_vars
                ]
                
                if not course_vars:
                    continue
                
                # Apply constraint: exactly 1 item from this course type
                self.model.Add(sum(course_vars) == 1)
            
            # CRITICAL: Constrain total items per day to exactly the number of courses
            # This prevents selecting items from courses not in the meal structure
            total_courses = len(self.meal_structure.course_requirements)
            self.model.Add(sum(day_vars.values()) == total_courses)
        
        print(f"Applied meal composition constraints")
    
    def _apply_menu_rules(self) -> None:
        """
        Apply all user-defined menu rules to the model.
        """
        context = self._build_rule_context()
        
        for rule in self.menu_rules:
            try:
                rule.apply(self.model, self.variables, self.menu_data, context)
            except Exception as e:
                print(f"Error applying menu rule {rule.name}: {e}")
    
    def _set_objective(self) -> None:
        """
        Set the optimization objective.
        
        Maximizes variety by maximizing the number of unique items used
        across the entire planning period.
        
        Uses auxiliary variables y_i that track whether item i is used
        at least once during the planning period.
        """
        # Create auxiliary variables for tracking unique item usage
        self.variables['unique_items'] = {}
        
        # Get all unique item IDs
        all_item_ids = set()
        for day_vars in self.variables['daily_items'].values():
            all_item_ids.update(day_vars.keys())
        
        # For each item, create a binary variable y_i
        # y_i = 1 if item i is used on at least one day, 0 otherwise
        for item_id in all_item_ids:
            var_name = f"unique_item_{item_id}"
            y_i = self.model.NewBoolVar(var_name)
            self.variables['unique_items'][item_id] = y_i
            
            # Link y_i to x_{i,d}: if item is used on any day, y_i must be 1
            # Constraint: y_i >= x_{i,d} for all days d
            for day_vars in self.variables['daily_items'].values():
                if item_id in day_vars:
                    self.model.Add(y_i >= day_vars[item_id])
            
            # Constraint: y_i <= sum of all x_{i,d} across days
            # This prevents y_i from being 1 when item is never used
            item_usage_across_days = []
            for day_vars in self.variables['daily_items'].values():
                if item_id in day_vars:
                    item_usage_across_days.append(day_vars[item_id])
            
            if item_usage_across_days:
                self.model.Add(y_i <= sum(item_usage_across_days))
        
        # Objective: Maximize the number of unique items used
        # This encourages variety and minimizes repetition
        unique_item_vars = list(self.variables['unique_items'].values())
        self.model.Maximize(sum(unique_item_vars))
        
        print(f"Set objective: maximize unique items (total available: {len(unique_item_vars)})")
    
    def _extract_solution(self, solver: cp_model.CpSolver, status: int) -> Dict[str, Any]:
        """
        Extract the solution from the solver.
        
        Args:
            solver: Solved CP-SAT solver instance
            status: Solution status from solver.Solve()
            
        Returns:
            Dictionary containing the menu plan
        """
        solution = {
            'menu_plan': {},
            'statistics': {
                'solve_time': solver.WallTime(),
                'status': solver.StatusName(status),
                'objective_value': solver.ObjectiveValue()
            }
        }
        
        for date, day_vars in self.variables['daily_items'].items():
            selected_items = []
            
            for item_id, var in day_vars.items():
                if solver.Value(var) == 1:
                    # Get item details
                    item_info = self.menu_data[self.menu_data['item_id'] == item_id].iloc[0].to_dict()
                    selected_items.append(item_info)
            
            solution['menu_plan'][date] = selected_items
        
        return solution
    
    def _get_planning_dates(self) -> List[Dict[str, Any]]:
        """
        Get list of dates for planning with metadata.
        
        Returns:
            List of dictionaries with date information
        """
        start_date = self.planning_config.get('start_date')
        num_days = self.planning_config.get('num_days', 7)
        include_weekends = self.planning_config.get('include_weekends', True)
        
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        
        planning_dates = []
        day_offset = 0
        while len(planning_dates) < num_days:
            date = start_date + timedelta(days=day_offset)
            day_name = date.strftime('%A').lower()
            if include_weekends or day_name not in ['saturday', 'sunday']:
                planning_dates.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'day_name': day_name,
                    'day_number': len(planning_dates)
                })
            day_offset += 1
        
        return planning_dates
    
    def _group_items_by_course(self) -> Dict[str, List[str]]:
        """
        Group menu items by course type.
        
        Returns:
            Dictionary mapping course types to item IDs
        """
        course_items = {}
        
        for course_type, group in self.menu_data.groupby('course_type'):
            course_items[course_type] = group['item_id'].tolist()
        
        return course_items
    
    def _build_rule_context(self) -> Dict[str, Any]:
        """
        Build context dictionary for menu rule application.
        
        Returns:
            Dictionary with planning context including meal structure
        """
        return {
            'planning_dates': self._get_planning_dates(),
            'menu_history': self.planning_config.get('menu_history', {}),
            'meal_type': self.meal_structure.meal_type.value,
            'client_id': self.meal_structure.client_id,
            'include_weekends': self.planning_config.get('include_weekends', True),
            'meal_structure': self.meal_structure  # Added for smart fallback in cuisine rules
        }
