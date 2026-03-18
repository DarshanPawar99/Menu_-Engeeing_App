"""
API Configuration
Server-side configuration for the Ikigai Masala API
"""

import os
from pathlib import Path

# Base directory (project root)
BASE_DIR = Path(__file__).parent.parent

# Default paths for menu data
DEFAULT_EXCEL_PATH = os.getenv(
    'MENU_EXCEL_PATH',
    str(BASE_DIR / 'data/raw/menu_items.xlsx')
)

# Processed data directory
PROCESSED_DATA_DIR = os.getenv(
    'PROCESSED_DATA_DIR',
    str(BASE_DIR / 'data/processed')
)

# Output directory for generated menu plans
OUTPUT_DIR = os.getenv(
    'OUTPUT_DIR',
    str(BASE_DIR / 'data/outputs')
)

# Default solver settings
DEFAULT_TIME_LIMIT_SECONDS = 300
MIN_TIME_LIMIT_SECONDS = 10
MAX_TIME_LIMIT_SECONDS = 600

# Default planning settings
DEFAULT_NUM_DAYS = 7
MIN_NUM_DAYS = 1
MAX_NUM_DAYS = 90

# API settings
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', '5000'))
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# CORS settings (if needed)
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
