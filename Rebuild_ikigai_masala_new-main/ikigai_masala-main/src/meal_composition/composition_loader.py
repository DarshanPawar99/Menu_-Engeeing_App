"""
Composition loader from JSON configuration
"""

import json
from pathlib import Path
from typing import Dict, List, Any

from .meal_structure import MealStructure, MealType


class CompositionLoader:
    """
    Loads meal composition structures from JSON configuration files.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the composition loader.
        
        Args:
            config_path: Path to JSON configuration file
        """
        self.config_path = Path(config_path) if config_path else None
        self.meal_structures = {}
        
    def load_from_file(self, config_path: str = None) -> Dict[str, MealStructure]:
        """
        Load meal compositions from a JSON file.
        
        Args:
            config_path: Path to JSON configuration file
            
        Returns:
            Dictionary mapping meal types to MealStructure objects
        """
        if config_path:
            self.config_path = Path(config_path)
        
        if not self.config_path or not self.config_path.exists():
            raise FileNotFoundError(f"Composition config file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            config_data = json.load(f)
        
        return self.load_from_dict(config_data)
    
    def load_from_dict(self, config_data: Dict[str, Any]) -> Dict[str, MealStructure]:
        """
        Load meal compositions from a dictionary.
        
        Args:
            config_data: Dictionary containing meal composition configurations
            
        Returns:
            Dictionary mapping meal types to MealStructure objects
        """
        self.meal_structures = {}
        
        client_id = config_data.get('client_id', 'default')
        meals = config_data.get('meals', [])
        
        for meal_config in meals:
            try:
                meal_config['client_id'] = client_id
                meal_structure = MealStructure.from_dict(meal_config)
                
                if meal_structure.validate():
                    meal_key = meal_structure.meal_type.value
                    self.meal_structures[meal_key] = meal_structure
                else:
                    print(f"Warning: Invalid meal structure for {meal_config.get('meal_type')}")
            except Exception as e:
                print(f"Error creating meal structure: {e}")
                print(f"Config: {meal_config}")
        
        print(f"Loaded {len(self.meal_structures)} meal structures for client '{client_id}'")
        return self.meal_structures
    
    def get_meal_structure(self, meal_type: str) -> MealStructure:
        """
        Get meal structure for a specific meal type.
        
        Args:
            meal_type: Type of meal (breakfast, lunch, dinner, snack)
            
        Returns:
            MealStructure object or None
        """
        return self.meal_structures.get(meal_type.lower())
    
    def export_to_file(self, output_path: str) -> None:
        """
        Export meal structures to JSON file.
        
        Args:
            output_path: Path to save the JSON file
        """
        export_data = {
            'client_id': list(self.meal_structures.values())[0].client_id if self.meal_structures else 'default',
            'meals': [structure.to_dict() for structure in self.meal_structures.values()]
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"Exported meal compositions to {output_path}")
