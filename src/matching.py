"""
Robot-Site Capability Matching

This module implements compatibility analysis between robots and sites,
identifying equipment gaps and suggesting optimal robot-site pairings.
"""

import pandas as pd
from typing import Dict, List, Tuple


class RobotSiteMatcher:
    """
    Analyzes compatibility between robots and mining sites based on
    depth ratings, sensor requirements, and operational constraints.
    """

    # Sensor requirements for different site types and minerals
    SENSOR_REQUIREMENTS = {
        'Polymetallic Nodules': ['side_scan_sonar', 'multi_beam_echo_sounder', 'HD_camera'],
        'Polymetallic Sulfides': ['magnetometer', 'side_scan_sonar', 'HD_camera', 'multi_beam_echo_sounder'],
        'Rare Earth Elements': ['multi_beam_echo_sounder', 'sub_bottom_profiler', 'sediment_sampler'],
        'Cobalt Crust': ['side_scan_sonar', 'HD_camera', 'magnetometer']
    }

    def __init__(self, robots: List[Dict], sites: List[Dict]):
        """
        Initialize the matcher with robot and site data.

        Args:
            robots: List of robot dictionaries
            sites: List of site dictionaries
        """
        self.robots_df = pd.DataFrame(robots)
        self.sites_df = pd.DataFrame(sites)

    def check_depth_compatibility(self, robot: Dict, site: Dict) -> Tuple[bool, str]:
        """
        Check if robot can reach the site depth.

        Args:
            robot: Robot data dictionary
            site: Site data dictionary

        Returns:
            Tuple of (is_compatible, message)
        """
        robot_max_depth = robot['max_depth_m']
        site_depth = site['depth_m']

        # Add 10% safety margin
        safe_depth = robot_max_depth * 0.9

        if site_depth <= safe_depth:
            margin = safe_depth - site_depth
            return True, f"Compatible (safety margin: {int(margin)}m)"
        else:
            deficit = site_depth - safe_depth
            return False, f"Insufficient depth rating (needs {int(deficit)}m more)"

    def check_sensor_compatibility(self, robot: Dict, site: Dict) -> Tuple[bool, str, List[str]]:
        """
        Check if robot has required sensors for site survey.

        Args:
            robot: Robot data dictionary
            site: Site data dictionary

        Returns:
            Tuple of (is_compatible, message, missing_sensors)
        """
        robot_sensors = set(robot['sensors'])
        required_sensors = set()

        # Determine required sensors based on mineral types
        for mineral_type in site['mineral_types']:
            for key in self.SENSOR_REQUIREMENTS:
                if key in mineral_type:
                    required_sensors.update(self.SENSOR_REQUIREMENTS[key])

        missing_sensors = list(required_sensors - robot_sensors)

        if not missing_sensors:
            return True, "All required sensors present", []
        else:
            missing_str = ", ".join(missing_sensors)
            return False, f"Missing sensors: {missing_str}", missing_sensors

    def check_status_compatibility(self, robot: Dict) -> Tuple[bool, str]:
        """
        Check if robot is available for deployment.

        Args:
            robot: Robot data dictionary

        Returns:
            Tuple of (is_available, message)
        """
        status = robot['status']

        if status == 'Available':
            return True, "Available for deployment"
        elif status == 'In Maintenance':
            return False, "Currently in maintenance"
        elif status == 'Deployed':
            return False, "Currently deployed on another mission"
        elif status == 'Retired':
            return False, "Robot retired from service"
        else:
            return False, f"Unknown status: {status}"

    def calculate_compatibility_score(self, robot: Dict, site: Dict) -> float:
        """
        Calculate overall compatibility score (0-100).

        Args:
            robot: Robot data dictionary
            site: Site data dictionary

        Returns:
            Compatibility score
        """
        score = 0.0

        # Depth compatibility (40 points)
        depth_ok, _ = self.check_depth_compatibility(robot, site)
        if depth_ok:
            score += 40
        else:
            # Partial credit if close
            depth_ratio = robot['max_depth_m'] / site['depth_m']
            score += min(40, depth_ratio * 40)

        # Sensor compatibility (40 points)
        sensor_ok, _, missing = self.check_sensor_compatibility(robot, site)
        if sensor_ok:
            score += 40
        else:
            # Determine required sensor count
            required_sensors = set()
            for mineral_type in site['mineral_types']:
                for key in self.SENSOR_REQUIREMENTS:
                    if key in mineral_type:
                        required_sensors.update(self.SENSOR_REQUIREMENTS[key])

            if len(required_sensors) > 0:
                present_count = len(required_sensors) - len(missing)
                score += (present_count / len(required_sensors)) * 40

        # Status compatibility (20 points)
        status_ok, _ = self.check_status_compatibility(robot)
        if status_ok:
            score += 20

        return round(score, 2)

    def get_compatibility_matrix(self) -> pd.DataFrame:
        """
        Generate compatibility matrix for all robot-site pairs.

        Returns:
            DataFrame with sites as rows and robots as columns
        """
        matrix_data = []

        for _, site in self.sites_df.iterrows():
            row = {'site_id': site['site_id'], 'site_name': site['name']}

            for _, robot in self.robots_df.iterrows():
                score = self.calculate_compatibility_score(
                    robot.to_dict(), site.to_dict()
                )
                row[robot['robot_id']] = score

            matrix_data.append(row)

        return pd.DataFrame(matrix_data)

    def get_detailed_compatibility(self, robot_id: str, site_id: str) -> Dict:
        """
        Get detailed compatibility analysis for a specific robot-site pair.

        Args:
            robot_id: Robot identifier
            site_id: Site identifier

        Returns:
            Dictionary with detailed compatibility information
        """
        robot = self.robots_df[self.robots_df['robot_id'] == robot_id].iloc[0].to_dict()
        site = self.sites_df[self.sites_df['site_id'] == site_id].iloc[0].to_dict()

        depth_ok, depth_msg = self.check_depth_compatibility(robot, site)
        sensor_ok, sensor_msg, missing_sensors = self.check_sensor_compatibility(robot, site)
        status_ok, status_msg = self.check_status_compatibility(robot)
        compatibility_score = self.calculate_compatibility_score(robot, site)

        # Overall compatibility
        is_fully_compatible = depth_ok and sensor_ok and status_ok

        if is_fully_compatible:
            overall_status = "Fully Compatible"
            color = "green"
        elif depth_ok and status_ok:
            overall_status = "Partially Compatible"
            color = "yellow"
        else:
            overall_status = "Incompatible"
            color = "red"

        return {
            'robot_id': robot_id,
            'robot_name': robot['name'],
            'site_id': site_id,
            'site_name': site['name'],
            'compatibility_score': compatibility_score,
            'overall_status': overall_status,
            'status_color': color,
            'depth_compatible': depth_ok,
            'depth_message': depth_msg,
            'sensor_compatible': sensor_ok,
            'sensor_message': sensor_msg,
            'missing_sensors': missing_sensors,
            'status_compatible': status_ok,
            'status_message': status_msg
        }

    def find_best_robots_for_site(self, site_id: str, top_n: int = 3) -> List[Dict]:
        """
        Find the best robots for a given site.

        Args:
            site_id: Site identifier
            top_n: Number of top robots to return

        Returns:
            List of robot compatibility dictionaries, sorted by score
        """
        results = []

        for _, robot in self.robots_df.iterrows():
            compatibility = self.get_detailed_compatibility(
                robot['robot_id'], site_id
            )
            compatibility['day_rate_usd'] = robot['day_rate_usd']
            compatibility['robot_type'] = robot['type']
            results.append(compatibility)

        # Sort by compatibility score descending
        results.sort(key=lambda x: x['compatibility_score'], reverse=True)

        return results[:top_n]

    def find_best_sites_for_robot(self, robot_id: str, top_n: int = 5) -> List[Dict]:
        """
        Find the best sites for a given robot.

        Args:
            robot_id: Robot identifier
            top_n: Number of top sites to return

        Returns:
            List of site compatibility dictionaries, sorted by score
        """
        results = []

        for _, site in self.sites_df.iterrows():
            compatibility = self.get_detailed_compatibility(
                robot_id, site['site_id']
            )
            compatibility['estimated_value_millions'] = site['estimated_value_millions']
            results.append(compatibility)

        # Sort by compatibility score descending
        results.sort(key=lambda x: x['compatibility_score'], reverse=True)

        return results[:top_n]

    def identify_equipment_gaps(self) -> Dict:
        """
        Identify equipment gaps in the robot fleet.

        Returns:
            Dictionary with gap analysis
        """
        gaps = {
            'depth_gaps': [],
            'sensor_gaps': [],
            'recommendations': []
        }

        # Check depth coverage
        max_fleet_depth = self.robots_df['max_depth_m'].max()
        deep_sites = self.sites_df[self.sites_df['depth_m'] > max_fleet_depth * 0.9]

        if len(deep_sites) > 0:
            for _, site in deep_sites.iterrows():
                gaps['depth_gaps'].append({
                    'site_id': site['site_id'],
                    'site_name': site['name'],
                    'site_depth': site['depth_m'],
                    'max_fleet_depth': max_fleet_depth,
                    'depth_deficit': site['depth_m'] - max_fleet_depth
                })

        # Check sensor coverage
        all_sensors = set()
        for sensors in self.robots_df['sensors']:
            all_sensors.update(sensors)

        required_sensors = set()
        for mineral_types in self.sites_df['mineral_types']:
            for mineral_type in mineral_types:
                for key in self.SENSOR_REQUIREMENTS:
                    if key in mineral_type:
                        required_sensors.update(self.SENSOR_REQUIREMENTS[key])

        missing_sensors = required_sensors - all_sensors

        if missing_sensors:
            gaps['sensor_gaps'] = list(missing_sensors)
            gaps['recommendations'].append(
                f"Consider acquiring robots with: {', '.join(missing_sensors)}"
            )

        if gaps['depth_gaps']:
            max_site_depth = self.sites_df['depth_m'].max()
            gaps['recommendations'].append(
                f"Consider acquiring ultra-deep robots (>{max_site_depth}m rating) "
                f"to access {len(deep_sites)} deep sites"
            )

        return gaps
