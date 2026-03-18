"""
Excel file reader for menu data - MVP Version
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Any


class ExcelReader:
    """
    Reads menu data from Excel files.
    
    Expected columns (MVP):
    - item_id: Unique identifier for menu item
    - item_name: Name of the dish
    - course_type: Type of course (starter, main, rice, dessert, etc.)
    - cuisine_family: Cuisine category (Italian, Chinese, Indian, etc.)
    - item_color: Color/category tag for the item
    """
    
    def __init__(self, file_path: str):
        """
        Initialize the Excel reader.
        
        Args:
            file_path: Path to the Excel file
        """
        self.file_path = Path(file_path)
        self.data = None
        
    def read(self) -> pd.DataFrame:
        """
        Read the Excel file and return as DataFrame.
        
        Returns:
            pandas DataFrame containing menu data
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"Excel file not found: {self.file_path}")
        
        self.data = pd.read_excel(self.file_path)
        
        print(f"Read {len(self.data)} menu items from {self.file_path}")
        return self.data
    
    def validate_schema(self) -> Dict[str, Any]:
        """
        Validate that the Excel file has required columns.
        
        Returns:
            Dictionary with validation results
        """
        required_columns = ['item_id', 'item_name', 'course_type', 'cuisine_family', 'item_color']
        
        if self.data is None:
            return {'valid': False, 'error': 'No data loaded'}
        
        missing_columns = [col for col in required_columns if col not in self.data.columns]
        
        if missing_columns:
            return {
                'valid': False,
                'missing_columns': missing_columns,
                'error': f"Missing required columns: {missing_columns}"
            }
        
        return {
            'valid': True,
            'columns': list(self.data.columns),
            'row_count': len(self.data)
        }
