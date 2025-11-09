"""
Site Prioritization Engine

This module implements multi-criteria scoring for deep-sea mining sites,
economic viability calculations, and priority categorization.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


class SitePrioritizationEngine:
    """
    Engine for scoring and prioritizing potential mining sites based on
    multiple weighted criteria.
    """

    DEFAULT_WEIGHTS = {
        'mineral_concentration': 0.20,
        'depth': 0.15,
        'distance_from_port': 0.10,
        'environmental_sensitivity': 0.15,
        'estimated_value': 0.20,
        'terrain_difficulty': 0.10,
        'survey_data_quality': 0.10
    }

    def __init__(self, weights: Dict[str, float] = None):
        """
        Initialize the prioritization engine.

        Args:
            weights: Dictionary of criterion weights (must sum to 1.0)
        """
        self.weights = weights if weights else self.DEFAULT_WEIGHTS.copy()
        self._validate_weights()

    def _validate_weights(self):
        """Ensure weights sum to approximately 1.0"""
        total = sum(self.weights.values())
        if not np.isclose(total, 1.0, atol=0.01):
            raise ValueError(f"Weights must sum to 1.0, got {total}")

    def normalize_score(self, value: float, min_val: float, max_val: float,
                       inverse: bool = False) -> float:
        """
        Normalize a value to 0-100 scale.

        Args:
            value: The value to normalize
            min_val: Minimum value in dataset
            max_val: Maximum value in dataset
            inverse: If True, higher values get lower scores

        Returns:
            Normalized score (0-100)
        """
        if max_val == min_val:
            return 50.0

        normalized = (value - min_val) / (max_val - min_val) * 100

        if inverse:
            normalized = 100 - normalized

        return normalized

    def score_sites(self, sites: List[Dict]) -> pd.DataFrame:
        """
        Score all sites based on multiple criteria.

        Args:
            sites: List of site dictionaries

        Returns:
            DataFrame with sites and their scores
        """
        df = pd.DataFrame(sites)

        # Extract min/max for normalization
        mineral_conc_range = (df['mineral_concentration'].min(),
                             df['mineral_concentration'].max())
        depth_range = (df['depth_m'].min(), df['depth_m'].max())
        distance_range = (df['distance_from_port_km'].min(),
                         df['distance_from_port_km'].max())
        env_range = (df['environmental_sensitivity'].min(),
                    df['environmental_sensitivity'].max())
        value_range = (df['estimated_value_millions'].min(),
                      df['estimated_value_millions'].max())
        terrain_range = (df['terrain_difficulty'].min(),
                        df['terrain_difficulty'].max())
        quality_range = (df['survey_data_quality'].min(),
                        df['survey_data_quality'].max())

        # Calculate normalized scores for each criterion
        df['mineral_score'] = df['mineral_concentration'].apply(
            lambda x: self.normalize_score(x, *mineral_conc_range, inverse=False)
        )

        df['depth_score'] = df['depth_m'].apply(
            lambda x: self.normalize_score(x, *depth_range, inverse=True)
        )

        df['distance_score'] = df['distance_from_port_km'].apply(
            lambda x: self.normalize_score(x, *distance_range, inverse=True)
        )

        df['environmental_score'] = df['environmental_sensitivity'].apply(
            lambda x: self.normalize_score(x, *env_range, inverse=True)
        )

        df['value_score'] = df['estimated_value_millions'].apply(
            lambda x: self.normalize_score(x, *value_range, inverse=False)
        )

        df['terrain_score'] = df['terrain_difficulty'].apply(
            lambda x: self.normalize_score(x, *terrain_range, inverse=True)
        )

        df['quality_score'] = df['survey_data_quality'].apply(
            lambda x: self.normalize_score(x, *quality_range, inverse=False)
        )

        # Calculate composite score
        df['composite_score'] = (
            df['mineral_score'] * self.weights['mineral_concentration'] +
            df['depth_score'] * self.weights['depth'] +
            df['distance_score'] * self.weights['distance_from_port'] +
            df['environmental_score'] * self.weights['environmental_sensitivity'] +
            df['value_score'] * self.weights['estimated_value'] +
            df['terrain_score'] * self.weights['terrain_difficulty'] +
            df['quality_score'] * self.weights['survey_data_quality']
        )

        # Round composite score
        df['composite_score'] = df['composite_score'].round(2)

        # Sort by composite score descending
        df = df.sort_values('composite_score', ascending=False).reset_index(drop=True)

        return df

    def calculate_economic_viability(self,
                                     site_data: Dict,
                                     extraction_cost_per_ton: float = 50,
                                     refining_cost_per_ton: float = 30,
                                     transport_cost_per_ton: float = 20,
                                     estimated_tonnage: float = 100000,
                                     mineral_price_per_ton: float = 8000,
                                     discount_rate: float = 0.10,
                                     project_years: int = 10) -> Dict:
        """
        Calculate economic viability metrics for a site.

        Args:
            site_data: Site information dictionary
            extraction_cost_per_ton: Cost to extract per ton
            refining_cost_per_ton: Cost to refine per ton
            transport_cost_per_ton: Cost to transport per ton
            estimated_tonnage: Estimated total tonnage
            mineral_price_per_ton: Market price per ton
            discount_rate: Discount rate for NPV calculation
            project_years: Project duration in years

        Returns:
            Dictionary with economic metrics
        """
        # Adjust costs based on site characteristics
        depth_multiplier = 1 + (site_data['depth_m'] / 10000) * 0.5
        distance_multiplier = 1 + (site_data['distance_from_port_km'] / 5000) * 0.3
        terrain_multiplier = 1 + (site_data['terrain_difficulty'] / 100) * 0.4

        adjusted_extraction_cost = extraction_cost_per_ton * depth_multiplier * terrain_multiplier
        adjusted_transport_cost = transport_cost_per_ton * distance_multiplier

        total_cost_per_ton = (adjusted_extraction_cost +
                             refining_cost_per_ton +
                             adjusted_transport_cost)

        # Revenue calculation
        concentration_factor = site_data['mineral_concentration'] / 100
        effective_price_per_ton = mineral_price_per_ton * concentration_factor

        profit_per_ton = effective_price_per_ton - total_cost_per_ton

        # Annual values
        annual_tonnage = estimated_tonnage / project_years
        annual_revenue = annual_tonnage * effective_price_per_ton
        annual_costs = annual_tonnage * total_cost_per_ton
        annual_profit = annual_revenue - annual_costs

        # NPV calculation
        npv = sum([annual_profit / ((1 + discount_rate) ** year)
                  for year in range(1, project_years + 1)])

        # Simple ROI
        total_revenue = estimated_tonnage * effective_price_per_ton
        total_costs = estimated_tonnage * total_cost_per_ton
        roi_percent = ((total_revenue - total_costs) / total_costs) * 100 if total_costs > 0 else 0

        return {
            'total_cost_per_ton': round(total_cost_per_ton, 2),
            'effective_price_per_ton': round(effective_price_per_ton, 2),
            'profit_per_ton': round(profit_per_ton, 2),
            'annual_revenue_millions': round(annual_revenue / 1_000_000, 2),
            'annual_costs_millions': round(annual_costs / 1_000_000, 2),
            'annual_profit_millions': round(annual_profit / 1_000_000, 2),
            'npv_millions': round(npv / 1_000_000, 2),
            'roi_percent': round(roi_percent, 2),
            'is_viable': profit_per_ton > 0
        }

    def categorize_priority(self, composite_score: float,
                           economic_viability: Dict) -> Tuple[str, str]:
        """
        Categorize site into priority tier.

        Args:
            composite_score: Composite score from scoring algorithm
            economic_viability: Economic viability metrics

        Returns:
            Tuple of (priority_level, priority_color)
        """
        if not economic_viability['is_viable']:
            return "Not Viable", "#d62728"

        if composite_score >= 70 and economic_viability['roi_percent'] > 50:
            return "High Priority", "#2ca02c"
        elif composite_score >= 50 and economic_viability['roi_percent'] > 25:
            return "Medium Priority", "#ff7f0e"
        elif composite_score >= 35:
            return "Further Study Needed", "#1f77b4"
        else:
            return "Low Priority", "#bcbd22"

    def get_score_breakdown(self, site_data: pd.Series) -> Dict[str, float]:
        """
        Get detailed score breakdown for a site.

        Args:
            site_data: Site data as pandas Series

        Returns:
            Dictionary with score components
        """
        return {
            'Mineral Concentration': site_data['mineral_score'],
            'Depth (accessibility)': site_data['depth_score'],
            'Distance from Port': site_data['distance_score'],
            'Environmental Risk': site_data['environmental_score'],
            'Estimated Value': site_data['value_score'],
            'Terrain Difficulty': site_data['terrain_score'],
            'Survey Data Quality': site_data['quality_score']
        }
