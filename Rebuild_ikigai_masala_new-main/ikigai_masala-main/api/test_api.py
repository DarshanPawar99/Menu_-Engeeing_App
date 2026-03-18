#!/usr/bin/env python3
"""
Simple test client for the Ikigai Masala API

This script demonstrates how to use the API programmatically.
"""

import requests
import json
from datetime import datetime, timedelta
from pathlib import Path


def test_api_health():
    """Test the health check endpoint"""
    print("\n" + "=" * 60)
    print("Testing Health Check Endpoint")
    print("=" * 60)
    
    url = "http://localhost:5000/api/v1/health"
    
    try:
        response = requests.get(url, timeout=5)
        print(f"\n✓ Status Code: {response.status_code}")
        print(f"✓ Response: {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


def load_example_configs():
    """Load example menu rules and composition configs"""
    config_dir = Path(__file__).parent.parent / "data" / "configs"
    
    # Load menu rules
    with open(config_dir / "indian_menu_rules.json") as f:
        menu_rules_data = json.load(f)
    
    # Load composition
    with open(config_dir / "indian_lunch_composition.json") as f:
        composition_data = json.load(f)
    
    # Return rules array and full composition structure (with "meals" key)
    return menu_rules_data.get("rules", []), composition_data


def test_api_menu_plan(num_days=7):
    """Test the menu planning endpoint"""
    print("\n" + "=" * 60)
    print(f"Testing Menu Planning Endpoint ({num_days} days)")
    print("=" * 60)
    
    url = "http://localhost:5000/api/v1/plan"
    
    # Calculate start date (tomorrow)
    start_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Load example configs
    menu_rules, meal_composition = load_example_configs()
    
    # Request payload with JSON content instead of paths
    # meal_composition should have the full structure with "meals" key
    payload = {
        "menu_rules": menu_rules,
        "meal_composition": meal_composition,
        "meal_type": "lunch",
        "start_date": start_date,
        "num_days": num_days,
        "include_weekends": True,
        "force_refresh": False,
        "time_limit_seconds": 300
    }
    
    print(f"\n📤 Request:")
    print(json.dumps(payload, indent=2))
    
    try:
        print(f"\n⏳ Sending request to {url}...")
        response = requests.post(url, json=payload, timeout=600)
        
        print(f"\n✓ Status Code: {response.status_code}")
        
        result = response.json()
        
        if result.get('success'):
            print(f"\n✓ Menu plan generated successfully!")
            
            solution = result.get('solution', [])
            print(f"\n📊 Menu Plan Summary:")
            print(f"   - Total days: {len(solution)}")
            
            if solution:
                # Get all courses from first day
                first_day = solution[0]
                courses = [k for k in first_day.keys() if k != 'date']
                print(f"   - Courses: {', '.join(courses)}")
                
                print(f"\n📝 Menu Plan (first 3 days):")
                for day_data in solution[:3]:
                    print(f"\n   {day_data.get('date', 'Unknown date')}:")
                    for course, items in day_data.items():
                        if course != 'date':
                            # items is an array
                            items_str = ', '.join(items) if items else '(none)'
                            print(f"      {course}: {items_str}")
                
                if len(solution) > 3:
                    print(f"\n   ... and {len(solution) - 3} more days")
        else:
            print(f"\n✗ Menu planning failed")
            print(f"   Message: {result.get('message', 'Unknown error')}")
            if result.get('error'):
                print(f"   Error: {result.get('error')}")
            if result.get('details'):
                print(f"   Details: {result.get('details')}")
        
        return result.get('success', False)
        
    except requests.exceptions.Timeout:
        print(f"\n✗ Request timed out (this is normal for large planning problems)")
        return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


def test_api_with_custom_params():
    """Test the API with custom parameters"""
    print("\n" + "=" * 60)
    print("Testing Menu Planning with Custom Parameters")
    print("=" * 60)
    
    url = "http://localhost:5000/api/v1/plan"
    
    # Load example configs
    menu_rules, meal_composition = load_example_configs()
    
    # Request payload with custom parameters
    payload = {
        "menu_rules": menu_rules,
        "meal_composition": meal_composition,
        "meal_type": "lunch",
        "start_date": "2026-03-01",
        "num_days": 5,
        "include_weekends": False,  # No weekends
        "force_refresh": False,
        "time_limit_seconds": 180  # Shorter time limit
    }
    
    print(f"\n📤 Request:")
    print(json.dumps(payload, indent=2))
    
    try:
        print(f"\n⏳ Sending request to {url}...")
        response = requests.post(url, json=payload, timeout=300)
        
        result = response.json()
        
        if result.get('success'):
            print(f"\n✓ Menu plan generated successfully!")
            solution = result.get('solution', [])
            print(f"   Total dates: {len(solution)}")
            if solution:
                courses = [k for k in solution[0].keys() if k != 'date']
                print(f"   Courses: {', '.join(courses)}")
        else:
            print(f"\n✗ Failed: {result.get('message', 'Unknown error')}")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🍛 Ikigai Masala API Test Suite")
    print("=" * 60)
    print("\nMake sure the API server is running:")
    print("  python -m api.run_api")
    print("\nor:")
    print("  python api/run_api.py")
    
    # Test health endpoint
    health_ok = test_api_health()
    
    if not health_ok:
        print("\n✗ Health check failed. Make sure the API server is running.")
        return 1
    
    # Test menu planning with default params
    plan_ok = test_api_menu_plan(num_days=7)
    
    # Test with custom params (optional, comment out if too slow)
    # custom_ok = test_api_with_custom_params()
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"✓ Health Check: {'PASSED' if health_ok else 'FAILED'}")
    print(f"✓ Menu Planning: {'PASSED' if plan_ok else 'FAILED'}")
    print()
    
    return 0 if (health_ok and plan_ok) else 1


if __name__ == "__main__":
    exit(main())
