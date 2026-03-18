"""
Script to analyze menu data Excel file
"""

import pandas as pd
from pathlib import Path


def analyze_menu_file(file_path):
    """
    Analyze the menu items Excel file.
    
    Args:
        file_path: Path to Excel file
    """
    print("="*70)
    print("MENU DATA ANALYSIS")
    print("="*70)
    
    # Read the Excel file
    df = pd.read_excel(file_path)
    
    print(f"\n📊 Basic Info:")
    print(f"  Total rows: {len(df)}")
    print(f"  Total columns: {len(df.columns)}")
    print(f"  Column names: {list(df.columns)}")
    
    print(f"\n📋 First 10 rows:")
    print(df.head(10).to_string())
    
    print(f"\n🔍 Unique values per column:")
    for col in df.columns:
        unique_vals = df[col].dropna().unique()
        print(f"\n  {col}:")
        print(f"    Count: {len(unique_vals)}")
        print(f"    Values: {sorted(unique_vals)}")
    
    print(f"\n📈 Value counts per column:")
    for col in df.columns:
        print(f"\n  {col}:")
        print(df[col].value_counts().to_string())
    
    print(f"\n🔢 Data types:")
    print(df.dtypes.to_string())
    
    print(f"\n❓ Missing values:")
    missing = df.isnull().sum()
    print(missing[missing > 0].to_string() if missing.sum() > 0 else "  None")
    
    print(f"\n📊 Summary statistics:")
    print(df.describe(include='all').to_string())
    
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    
    return df


if __name__ == "__main__":
    file_path = "data/raw/menu_items_aggregation.xlsx"
    
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        print("Please ensure the file exists at the specified path.")
    else:
        df = analyze_menu_file(file_path)
        
        # Export to CSV for easy viewing
        csv_path = "data/raw/menu_items_analysis.csv"
        df.to_csv(csv_path, index=False)
        print(f"\n💾 Exported to CSV: {csv_path}")
