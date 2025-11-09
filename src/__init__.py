"""
Deep-Sea Exploration Planner - Core Module

This package contains the core logic for site prioritization, robot-site matching,
mission optimization, and visualization utilities.
"""

from .scoring import SitePrioritizationEngine
from .matching import RobotSiteMatcher
from .optimizer import MissionOptimizer

__all__ = [
    'SitePrioritizationEngine',
    'RobotSiteMatcher',
    'MissionOptimizer'
]

__version__ = '1.0.0'
