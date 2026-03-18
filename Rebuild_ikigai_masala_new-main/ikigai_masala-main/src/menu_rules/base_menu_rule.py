"""
Base menu rule class for all rule types - MVP Version
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any
from ortools.sat.python import cp_model


class MenuRuleType(Enum):
    """Types of menu rules supported in MVP"""
    CUISINE = "cuisine"
    COLOR_PAIRING = "color_pairing"
    COLOR_VARIETY = "color_variety"
    UNIQUE_ITEMS = "unique_items"


class BaseMenuRule(ABC):
    """
    Abstract base class for all menu rules.
    All rule types must inherit from this class.
    """
    
    def __init__(self, rule_config: Dict[str, Any]):
        """
        Initialize the menu rule with configuration.
        
        Args:
            rule_config: Dictionary containing rule parameters
        """
        self.config = rule_config
        self.rule_type = None
        self.enabled = True
        self.name = rule_config.get('name', 'unnamed_rule')
        self.priority = rule_config.get('priority', 1)  # Lower number = higher priority
        
    @abstractmethod
    def apply(self, model: cp_model.CpModel, variables: Dict[str, Any], 
              menu_data: Any, context: Dict[str, Any]) -> None:
        """
        Apply the menu rule to the CP-SAT model.
        
        Args:
            model: OR-Tools CP-SAT model
            variables: Dictionary of decision variables
            menu_data: Menu data (DataFrame or dict)
            context: Additional context (dates, history, etc.)
        """
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate the menu rule configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        pass
    
    def get_description(self) -> str:
        """
        Get a human-readable description of the menu rule.
        
        Returns:
            String description
        """
        return f"{self.rule_type.value}: {self.name}"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}', enabled={self.enabled})>"
