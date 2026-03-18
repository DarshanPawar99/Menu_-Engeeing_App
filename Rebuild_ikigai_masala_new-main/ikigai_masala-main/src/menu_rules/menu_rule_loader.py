"""
Menu rule loader from JSON configuration - MVP Version
"""

import json
from pathlib import Path
from typing import List, Dict, Any

from .base_menu_rule import BaseMenuRule, MenuRuleType
from .cuisine_menu_rule import CuisineMenuRule
from .color_pairing_menu_rule import ColorPairingMenuRule
from .color_variety_menu_rule import ColorVarietyMenuRule
from .unique_items_menu_rule import UniqueItemsMenuRule


class MenuRuleLoader:
    """
    Loads menu rules from JSON configuration files.
    MVP version: Only supports cuisine rules.
    """
    
    # Map rule types to their implementation classes
    RULE_CLASSES = {
        'cuisine': CuisineMenuRule,
        'color_pairing': ColorPairingMenuRule,
        'color_variety': ColorVarietyMenuRule,
        'unique_items': UniqueItemsMenuRule,
    }
    
    def __init__(self, config_path: str = None):
        """
        Initialize the menu rule loader.
        
        Args:
            config_path: Path to JSON configuration file
        """
        self.config_path = Path(config_path) if config_path else None
        self.rules = []
        
    def load_from_file(self, config_path: str = None) -> List[BaseMenuRule]:
        """
        Load menu rules from a JSON file.
        
        Args:
            config_path: Path to JSON configuration file
            
        Returns:
            List of menu rule objects
        """
        if config_path:
            self.config_path = Path(config_path)
        
        if not self.config_path or not self.config_path.exists():
            raise FileNotFoundError(f"Menu rule config file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            config_data = json.load(f)
        
        return self.load_from_dict(config_data)
    
    def load_from_dict(self, config_data: Dict[str, Any]) -> List[BaseMenuRule]:
        """
        Load menu rules from a dictionary.
        
        Args:
            config_data: Dictionary containing rule configurations
            
        Returns:
            List of menu rule objects
        """
        self.rules = []
        
        # Support both 'constraints' (old) and 'rules' (new) keys for backward compatibility
        rules_list = config_data.get('rules', config_data.get('constraints', []))
        
        for rule_config in rules_list:
            rule_type = rule_config.get('type', '').lower()
            
            try:
                rule = self._create_rule(rule_config)
                if rule and rule.validate_config():
                    self.rules.append(rule)
                else:
                    print(f"Warning: Invalid rule configuration: {rule_config.get('name')}")
            except Exception as e:
                print(f"Error creating rule: {e}")
                print(f"Config: {rule_config}")
        
        print(f"Loaded {len(self.rules)} menu rule(s)")
        return self.rules
    
    def _create_rule(self, rule_config: Dict[str, Any]) -> BaseMenuRule:
        """
        Create a menu rule object from configuration.
        
        Args:
            rule_config: Dictionary with rule parameters
            
        Returns:
            Menu rule object
        """
        rule_type = rule_config.get('type', '').lower()
        
        if rule_type not in self.RULE_CLASSES:
            raise ValueError(f"Unknown rule type: {rule_type}")
        
        rule_class = self.RULE_CLASSES[rule_type]
        return rule_class(rule_config)
    
    def get_rules_by_type(self, rule_type: str) -> List[BaseMenuRule]:
        """
        Get all rules of a specific type.
        
        Args:
            rule_type: Type of rule to filter
            
        Returns:
            List of matching rules
        """
        return [r for r in self.rules if r.rule_type.value == rule_type]
    
    def get_enabled_rules(self) -> List[BaseMenuRule]:
        """
        Get all enabled rules.
        
        Returns:
            List of enabled rules
        """
        return list(self.rules)
