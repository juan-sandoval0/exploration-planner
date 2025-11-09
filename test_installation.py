"""
Test script to verify installation and basic functionality.
Run this after installing dependencies to ensure everything is set up correctly.
"""

import sys
import json
from pathlib import Path

def test_imports():
    """Test that all required packages can be imported."""
    print("Testing imports...")
    try:
        import streamlit
        import plotly
        import folium
        import pandas
        import numpy
        import scipy
        import geopy
        print("✓ All packages imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_data_files():
    """Test that data files exist and are valid JSON."""
    print("\nTesting data files...")
    try:
        with open('data/sites.json', 'r') as f:
            sites = json.load(f)
        print(f"✓ Loaded {len(sites)} sites from sites.json")

        with open('data/robots.json', 'r') as f:
            robots = json.load(f)
        print(f"✓ Loaded {len(robots)} robots from robots.json")

        return True
    except Exception as e:
        print(f"✗ Data file error: {e}")
        return False

def test_core_modules():
    """Test that core modules can be imported."""
    print("\nTesting core modules...")
    try:
        sys.path.append('src')
        from scoring import SitePrioritizationEngine
        from matching import RobotSiteMatcher
        from optimizer import MissionOptimizer
        print("✓ All core modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Module import error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality of core modules."""
    print("\nTesting basic functionality...")
    try:
        sys.path.append('src')
        from scoring import SitePrioritizationEngine

        # Load test data
        with open('data/sites.json', 'r') as f:
            sites = json.load(f)

        # Test scoring
        scorer = SitePrioritizationEngine()
        scored_sites = scorer.score_sites(sites)

        print(f"✓ Successfully scored {len(scored_sites)} sites")
        print(f"  Top site: {scored_sites.iloc[0]['name']} (score: {scored_sites.iloc[0]['composite_score']:.2f})")

        return True
    except Exception as e:
        print(f"✗ Functionality test error: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Deep-Sea Exploration Planner - Installation Test")
    print("=" * 60)

    tests = [
        test_imports,
        test_data_files,
        test_core_modules,
        test_basic_functionality
    ]

    results = [test() for test in tests]

    print("\n" + "=" * 60)
    if all(results):
        print("SUCCESS: All tests passed!")
        print("\nYou can now run the application with:")
        print("  streamlit run app.py")
    else:
        print("FAILURE: Some tests failed. Please check the errors above.")
    print("=" * 60)

if __name__ == "__main__":
    main()
