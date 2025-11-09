"""
Mission Planning Optimizer

This module implements mission scheduling and route optimization for
deep-sea exploration missions using greedy algorithms with constraints.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from geopy.distance import geodesic


class MissionOptimizer:
    """
    Optimizes mission scheduling for robot deployments to mining sites,
    considering constraints like robot availability, transit times, and budgets.
    """

    def __init__(self, robots: List[Dict], sites: List[Dict],
                 compatibility_scores: pd.DataFrame):
        """
        Initialize the mission optimizer.

        Args:
            robots: List of robot dictionaries
            sites: List of site dictionaries
            compatibility_scores: Matrix of robot-site compatibility scores
        """
        self.robots_df = pd.DataFrame(robots)
        self.sites_df = pd.DataFrame(sites)
        self.compatibility_matrix = compatibility_scores

    def calculate_transit_time(self, from_lat: float, from_lon: float,
                               to_lat: float, to_lon: float,
                               vessel_speed_knots: float = 12) -> float:
        """
        Calculate transit time between two locations in hours.

        Args:
            from_lat: Starting latitude
            from_lon: Starting longitude
            to_lat: Destination latitude
            to_lon: Destination longitude
            vessel_speed_knots: Speed of support vessel in knots

        Returns:
            Transit time in hours
        """
        # Calculate distance using geodesic (great circle) distance
        distance_km = geodesic(
            (from_lat, from_lon),
            (to_lat, to_lon)
        ).kilometers

        # Convert knots to km/h (1 knot = 1.852 km/h)
        speed_kmh = vessel_speed_knots * 1.852

        transit_time_hours = distance_km / speed_kmh

        return transit_time_hours

    def calculate_mission_duration(self, site: Dict, robot: Dict,
                                   survey_area_km2: float = 25) -> float:
        """
        Estimate mission duration for a site survey.

        Args:
            site: Site data dictionary
            robot: Robot data dictionary
            survey_area_km2: Area to survey in square kilometers

        Returns:
            Mission duration in hours
        """
        # Base survey time based on robot speed and area
        # Assume systematic survey pattern with some overlap
        robot_speed_kmh = robot['speed_knots'] * 1.852
        survey_hours = (survey_area_km2 / robot_speed_kmh) * 3  # *3 for coverage pattern

        # Add time for deployment and recovery
        deployment_hours = 4

        # Add time based on depth (deeper = slower operations)
        depth_factor = 1 + (site['depth_m'] / 5000) * 0.5

        # Add time based on terrain difficulty
        terrain_factor = 1 + (site['terrain_difficulty'] / 100) * 0.3

        total_hours = (survey_hours * depth_factor * terrain_factor) + deployment_hours

        # Ensure within robot endurance
        return min(total_hours, robot['endurance_hours'] * 0.8)

    def calculate_mission_cost(self, robot: Dict, mission_duration_hours: float,
                              transit_time_hours: float,
                              vessel_day_rate: float = 75000) -> float:
        """
        Calculate total mission cost.

        Args:
            robot: Robot data dictionary
            mission_duration_hours: On-site mission duration
            transit_time_hours: Transit time to/from site
            vessel_day_rate: Daily rate for support vessel

        Returns:
            Total mission cost in USD
        """
        total_hours = mission_duration_hours + transit_time_hours
        total_days = total_hours / 24

        robot_cost = robot['day_rate_usd'] * total_days
        vessel_cost = vessel_day_rate * total_days

        # Additional operational costs (fuel, consumables, crew)
        operational_cost = total_days * 15000

        return robot_cost + vessel_cost + operational_cost

    def greedy_mission_scheduler(self,
                                 time_window_days: int = 180,
                                 budget_usd: float = 10000000,
                                 vessel_speed_knots: float = 12,
                                 vessel_day_rate: float = 75000,
                                 prioritize_by: str = 'score') -> Dict:
        """
        Schedule missions using a greedy algorithm.

        Args:
            time_window_days: Planning horizon in days
            budget_usd: Total budget constraint
            vessel_speed_knots: Support vessel speed
            vessel_day_rate: Daily rate for support vessel
            prioritize_by: 'score' or 'value' - how to prioritize sites

        Returns:
            Dictionary with mission schedule and statistics
        """
        missions = []
        remaining_budget = budget_usd
        start_date = datetime.now()

        # Get available robots
        available_robots = self.robots_df[
            self.robots_df['status'] == 'Available'
        ].copy()

        # Initialize robot schedules
        robot_schedules = {
            row['robot_id']: {'available_from': start_date, 'missions': []}
            for _, row in available_robots.iterrows()
        }

        # Sort sites by priority
        if prioritize_by == 'score':
            sites_sorted = self.sites_df.sort_values(
                'mineral_concentration', ascending=False
            ).copy()
        else:
            sites_sorted = self.sites_df.sort_values(
                'estimated_value_millions', ascending=False
            ).copy()

        # Greedy assignment
        for _, site in sites_sorted.iterrows():
            if remaining_budget <= 0:
                break

            # Find best available robot for this site
            best_robot = None
            best_score = -1
            best_start_time = None

            for robot_id, schedule in robot_schedules.items():
                robot = available_robots[
                    available_robots['robot_id'] == robot_id
                ].iloc[0].to_dict()

                # Check depth compatibility
                if robot['max_depth_m'] * 0.9 < site['depth_m']:
                    continue

                # Get compatibility score
                comp_score = self.calculate_compatibility_score_simple(
                    robot, site.to_dict()
                )

                if comp_score > best_score:
                    best_score = comp_score
                    best_robot = robot
                    best_start_time = schedule['available_from']

            # If found compatible robot, schedule mission
            if best_robot and best_score >= 40:
                # Calculate transit time from robot's current position
                transit_time = self.calculate_transit_time(
                    best_robot['current_location']['lat'],
                    best_robot['current_location']['lon'],
                    site['latitude'],
                    site['longitude'],
                    vessel_speed_knots
                )

                # Calculate mission duration
                mission_duration = self.calculate_mission_duration(
                    site.to_dict(), best_robot
                )

                # Calculate cost
                mission_cost = self.calculate_mission_cost(
                    best_robot, mission_duration, transit_time, vessel_day_rate
                )

                # Check budget
                if mission_cost > remaining_budget:
                    continue

                # Check if mission fits in time window
                total_hours = transit_time + mission_duration
                mission_end = best_start_time + timedelta(hours=total_hours)

                if (mission_end - start_date).days > time_window_days:
                    continue

                # Schedule the mission
                mission = {
                    'mission_id': f"MISSION_{len(missions) + 1:03d}",
                    'site_id': site['site_id'],
                    'site_name': site['name'],
                    'robot_id': best_robot['robot_id'],
                    'robot_name': best_robot['name'],
                    'start_date': best_start_time,
                    'end_date': mission_end,
                    'transit_hours': round(transit_time, 1),
                    'survey_hours': round(mission_duration, 1),
                    'total_hours': round(total_hours, 1),
                    'cost_usd': round(mission_cost, 2),
                    'compatibility_score': best_score,
                    'site_latitude': site['latitude'],
                    'site_longitude': site['longitude']
                }

                missions.append(mission)
                remaining_budget -= mission_cost

                # Update robot schedule
                robot_schedules[best_robot['robot_id']]['available_from'] = mission_end
                robot_schedules[best_robot['robot_id']]['missions'].append(mission)

        # Calculate statistics
        total_cost = budget_usd - remaining_budget
        num_sites_surveyed = len(set([m['site_id'] for m in missions]))
        num_robots_used = len(set([m['robot_id'] for m in missions]))

        coverage_percent = (num_sites_surveyed / len(self.sites_df)) * 100

        return {
            'missions': missions,
            'statistics': {
                'total_missions': len(missions),
                'total_cost_usd': round(total_cost, 2),
                'remaining_budget_usd': round(remaining_budget, 2),
                'budget_utilization_percent': round((total_cost / budget_usd) * 100, 2),
                'num_sites_surveyed': num_sites_surveyed,
                'num_robots_used': num_robots_used,
                'coverage_percent': round(coverage_percent, 2),
                'avg_mission_cost_usd': round(total_cost / len(missions), 2) if missions else 0
            }
        }

    def calculate_compatibility_score_simple(self, robot: Dict, site: Dict) -> float:
        """
        Simplified compatibility score calculation.

        Args:
            robot: Robot data dictionary
            site: Site data dictionary

        Returns:
            Compatibility score
        """
        score = 0.0

        # Depth check
        if robot['max_depth_m'] * 0.9 >= site['depth_m']:
            score += 50
        else:
            depth_ratio = robot['max_depth_m'] / site['depth_m']
            score += min(50, depth_ratio * 50)

        # Sensor check (simplified)
        required_sensors = {'side_scan_sonar', 'multi_beam_echo_sounder', 'HD_camera'}
        robot_sensors = set(robot['sensors'])
        sensor_match = len(required_sensors & robot_sensors) / len(required_sensors)
        score += sensor_match * 50

        return score

    def generate_route_sequence(self, missions: List[Dict]) -> List[Dict]:
        """
        Generate optimized route sequences for each robot.

        Args:
            missions: List of scheduled missions

        Returns:
            List of route waypoints for visualization
        """
        routes = []

        # Group missions by robot
        robot_missions = {}
        for mission in missions:
            robot_id = mission['robot_id']
            if robot_id not in robot_missions:
                robot_missions[robot_id] = []
            robot_missions[robot_id].append(mission)

        # Generate route for each robot
        for robot_id, missions_list in robot_missions.items():
            robot = self.robots_df[
                self.robots_df['robot_id'] == robot_id
            ].iloc[0].to_dict()

            # Sort missions by start date
            missions_sorted = sorted(missions_list, key=lambda x: x['start_date'])

            waypoints = [{
                'robot_id': robot_id,
                'robot_name': robot['name'],
                'location_type': 'start',
                'latitude': robot['current_location']['lat'],
                'longitude': robot['current_location']['lon'],
                'timestamp': missions_sorted[0]['start_date'] if missions_sorted else datetime.now()
            }]

            for mission in missions_sorted:
                waypoints.append({
                    'robot_id': robot_id,
                    'robot_name': robot['name'],
                    'location_type': 'mission_site',
                    'site_id': mission['site_id'],
                    'site_name': mission['site_name'],
                    'latitude': mission['site_latitude'],
                    'longitude': mission['site_longitude'],
                    'timestamp': mission['start_date'],
                    'mission_id': mission['mission_id']
                })

            routes.extend(waypoints)

        return routes
