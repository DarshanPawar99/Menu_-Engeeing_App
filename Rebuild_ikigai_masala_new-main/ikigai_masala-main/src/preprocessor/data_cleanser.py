"""
Data cleanser for menu data - MVP Version
"""

import pandas as pd
from typing import Dict, Any


class DataCleanser:
    """
    Basic data cleaning for menu data.
    MVP version with minimal essential checks only.
    """
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize the data cleanser.
        
        Args:
            data: Raw DataFrame from Excel
        """
        self.raw_data = data.copy()
        self.cleaned_data = None
        
    def clean(self) -> pd.DataFrame:
        """
        Perform basic cleaning operations on the data.
        
        Returns:
            Cleaned DataFrame
        """
        df = self.raw_data.copy()
        
        # 1. Remove duplicates based on item_id
        initial_count = len(df)
        df = df.drop_duplicates(subset=['item_id'], keep='first')
        duplicates_removed = initial_count - len(df)
        if duplicates_removed > 0:
            print(f"  Removed {duplicates_removed} duplicate items")
        
        # 2. Handle missing values (fill with empty string)
        df['item_name'] = df['item_name'].fillna('')
        df['course_type'] = df['course_type'].fillna('')
        df['cuisine_family'] = df['cuisine_family'].fillna('')
        if 'item_color' not in df.columns:
            df['item_color'] = ''
        df['item_color'] = df['item_color'].fillna('')
        
        # 3. Standardize text fields (lowercase and trim)
        df['item_id'] = df['item_id'].astype(str).str.strip()
        df['item_name'] = df['item_name'].astype(str).str.strip().str.lower()
        df['course_type'] = df['course_type'].astype(str).str.strip().str.lower()
        df['cuisine_family'] = df['cuisine_family'].astype(str).str.strip().str.lower()
        df['item_color'] = df['item_color'].astype(str).str.strip().str.lower()
        
        # 4. Remove any rows with empty item_id or item_name
        df = df[df['item_id'].str.len() > 0]
        df = df[df['item_name'].str.len() > 0]
        
        self.cleaned_data = df
        print(f"  Cleaned data: {len(df)} items ready")
        return df
