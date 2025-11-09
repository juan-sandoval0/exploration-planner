"""
Deep-Sea Critical Minerals Exploration Planner

Interactive web application for analyzing potential mining sites,
managing robotics fleet, and optimizing exploration missions.
"""

import streamlit as st
import pandas as pd
import json
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from scoring import SitePrioritizationEngine
from matching import RobotSiteMatcher
from optimizer import MissionOptimizer
from visualization import (
    create_site_map, create_priority_chart, create_score_breakdown_chart,
    create_compatibility_heatmap, create_gantt_chart, create_mission_route_map,
    create_cost_breakdown_chart, create_depth_distribution_chart,
    create_value_vs_difficulty_scatter
)
from streamlit_folium import folium_static


# Page configuration
st.set_page_config(
    page_title="Deep-Sea Exploration Planner",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_data
def load_data():
    """Load site and robot data from JSON files."""
    with open('data/sites.json', 'r') as f:
        sites = json.load(f)
    with open('data/robots.json', 'r') as f:
        robots = json.load(f)
    return sites, robots


def main():
    """Main application entry point."""

    # Header
    st.title("Deep-Sea Critical Minerals Exploration Planner")
    st.markdown("""
    Advanced planning tool for deep-sea mining operations combining site analysis,
    robotics fleet management, and mission optimization.
    """)

    # Load data
    sites, robots = load_data()

    # Sidebar - Global Settings
    st.sidebar.header("Configuration")

    # Navigation
    page = st.sidebar.radio(
        "Navigation",
        ["Site Explorer", "Fleet Management", "Capability Matching",
         "Mission Planner", "Coverage Analytics"]
    )

    st.sidebar.markdown("---")

    # === SITE EXPLORER PAGE ===
    if page == "Site Explorer":
        st.header("Site Explorer & Prioritization")

        # Scoring weights configuration
        st.sidebar.subheader("Scoring Weights")

        # Initialize session state for weights if not exists
        if 'raw_weights' not in st.session_state:
            st.session_state.raw_weights = {
                'mineral_concentration': 0.20,
                'depth': 0.15,
                'distance_from_port': 0.10,
                'environmental_sensitivity': 0.15,
                'estimated_value': 0.20,
                'terrain_difficulty': 0.10,
                'survey_data_quality': 0.10
            }

        # Create sliders for raw weights (unnormalized)
        raw_weights = {
            'mineral_concentration': st.sidebar.slider(
                "Mineral Concentration", 0.0, 1.0,
                st.session_state.raw_weights['mineral_concentration'], 0.05
            ),
            'depth': st.sidebar.slider(
                "Depth (accessibility)", 0.0, 1.0,
                st.session_state.raw_weights['depth'], 0.05
            ),
            'distance_from_port': st.sidebar.slider(
                "Distance from Port", 0.0, 1.0,
                st.session_state.raw_weights['distance_from_port'], 0.05
            ),
            'environmental_sensitivity': st.sidebar.slider(
                "Environmental Risk", 0.0, 1.0,
                st.session_state.raw_weights['environmental_sensitivity'], 0.05
            ),
            'estimated_value': st.sidebar.slider(
                "Estimated Value", 0.0, 1.0,
                st.session_state.raw_weights['estimated_value'], 0.05
            ),
            'terrain_difficulty': st.sidebar.slider(
                "Terrain Difficulty", 0.0, 1.0,
                st.session_state.raw_weights['terrain_difficulty'], 0.05
            ),
            'survey_data_quality': st.sidebar.slider(
                "Survey Data Quality", 0.0, 1.0,
                st.session_state.raw_weights['survey_data_quality'], 0.05
            )
        }

        # Update session state
        st.session_state.raw_weights = raw_weights

        # Normalize weights to sum to 1.0
        weight_sum = sum(raw_weights.values())
        if weight_sum > 0:
            weights = {k: v / weight_sum for k, v in raw_weights.items()}
        else:
            # If all weights are 0, use equal weights
            weights = {k: 1/7 for k in raw_weights.keys()}

        with st.sidebar.expander("View Normalized Weights"):
            for key, value in weights.items():
                label = key.replace('_', ' ').title()
                st.write(f"{label}: {value:.3f}")

        # Initialize scoring engine
        try:
            scorer = SitePrioritizationEngine(weights)
            scored_sites = scorer.score_sites(sites)

            # Display tabs
            tab1, tab2, tab3 = st.tabs(["Map View", "Rankings", "Analytics"])

            with tab1:
                st.subheader("Global Site Map")
                site_map = create_site_map(scored_sites, color_by='composite_score')
                folium_static(site_map, width=None, height=600)

                st.caption("Sites color-coded by priority: Green (High), Orange (Medium), Red (Low)")

            with tab2:
                st.subheader("Site Priority Rankings")

                col1, col2 = st.columns([2, 1])

                with col1:
                    priority_chart = create_priority_chart(scored_sites)
                    st.plotly_chart(priority_chart, use_container_width=True)

                with col2:
                    st.markdown("### Top 5 Sites")
                    for idx, row in scored_sites.head(5).iterrows():
                        st.metric(
                            label=row['name'],
                            value=f"{row['composite_score']:.1f}",
                            delta=f"${row['estimated_value_millions']}M"
                        )

                # Detailed site table
                st.subheader("Detailed Site Scores")
                display_cols = ['site_id', 'name', 'composite_score',
                               'mineral_concentration', 'depth_m',
                               'estimated_value_millions', 'jurisdiction']
                st.dataframe(
                    scored_sites[display_cols].style.background_gradient(
                        subset=['composite_score'], cmap='RdYlGn'
                    ),
                    height=400
                )

            with tab3:
                st.subheader("Site Analytics")

                col1, col2 = st.columns(2)

                with col1:
                    depth_chart = create_depth_distribution_chart(scored_sites)
                    st.plotly_chart(depth_chart, use_container_width=True)

                with col2:
                    scatter_chart = create_value_vs_difficulty_scatter(scored_sites)
                    st.plotly_chart(scatter_chart, use_container_width=True)

                # Individual site analysis
                st.subheader("Individual Site Analysis")
                selected_site = st.selectbox(
                    "Select a site for detailed analysis:",
                    scored_sites['name'].tolist()
                )

                site_data = scored_sites[scored_sites['name'] == selected_site].iloc[0]

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("### Site Information")
                    st.write(f"**Site ID:** {site_data['site_id']}")
                    st.write(f"**Depth:** {site_data['depth_m']}m")
                    st.write(f"**Location:** {site_data['latitude']:.2f}, {site_data['longitude']:.2f}")
                    st.write(f"**Jurisdiction:** {site_data['jurisdiction']}")
                    st.write(f"**Distance from Port:** {site_data['distance_from_port_km']}km")

                    st.markdown("### Score Breakdown")
                    breakdown = scorer.get_score_breakdown(site_data)
                    radar_chart = create_score_breakdown_chart(breakdown, weights)
                    st.plotly_chart(radar_chart, use_container_width=True)

                with col2:
                    st.markdown("### Economic Viability")

                    # Economic parameters
                    extraction_cost = st.number_input("Extraction cost ($/ton)", value=50, step=10)
                    refining_cost = st.number_input("Refining cost ($/ton)", value=30, step=5)
                    transport_cost = st.number_input("Transport cost ($/ton)", value=20, step=5)
                    tonnage = st.number_input("Estimated tonnage", value=100000, step=10000)
                    mineral_price = st.number_input("Mineral price ($/ton)", value=8000, step=100)

                    economics = scorer.calculate_economic_viability(
                        site_data.to_dict(),
                        extraction_cost_per_ton=extraction_cost,
                        refining_cost_per_ton=refining_cost,
                        transport_cost_per_ton=transport_cost,
                        estimated_tonnage=tonnage,
                        mineral_price_per_ton=mineral_price
                    )

                    st.write(f"**NPV:** ${economics['npv_millions']:.2f}M")
                    st.write(f"**ROI:** {economics['roi_percent']:.2f}%")
                    st.write(f"**Annual Profit:** ${economics['annual_profit_millions']:.2f}M")
                    st.write(f"**Profit per Ton:** ${economics['profit_per_ton']:.2f}")

                    priority, color = scorer.categorize_priority(
                        site_data['composite_score'], economics
                    )

                    st.markdown(f"### Priority: :{color}[{priority}]")

        except ValueError as e:
            st.error(f"Configuration error: {e}")

    # === FLEET MANAGEMENT PAGE ===
    elif page == "Fleet Management":
        st.header("Robotics Fleet Management")

        robots_df = pd.DataFrame(robots)

        # Fleet statistics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Robots", len(robots_df))

        with col2:
            available = len(robots_df[robots_df['status'] == 'Available'])
            st.metric("Available", available)

        with col3:
            in_maintenance = len(robots_df[robots_df['status'] == 'In Maintenance'])
            st.metric("In Maintenance", in_maintenance)

        with col4:
            deployed = len(robots_df[robots_df['status'] == 'Deployed'])
            st.metric("Deployed", deployed)

        # Fleet table
        st.subheader("Fleet Overview")

        # Format display
        display_df = robots_df[['robot_id', 'name', 'type', 'max_depth_m',
                                'endurance_hours', 'speed_knots', 'status',
                                'day_rate_usd']].copy()

        # Color code status
        def color_status(val):
            if val == 'Available':
                return 'background-color: #90EE90'
            elif val == 'In Maintenance':
                return 'background-color: #FFD700'
            elif val == 'Deployed':
                return 'background-color: #FFB6C1'
            else:
                return ''

        st.dataframe(
            display_df.style.applymap(color_status, subset=['status']),
            height=400
        )

        # Individual robot details
        st.subheader("Robot Details")
        selected_robot = st.selectbox(
            "Select a robot:",
            robots_df['name'].tolist()
        )

        robot_data = robots_df[robots_df['name'] == selected_robot].iloc[0]

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Specifications")
            st.write(f"**Robot ID:** {robot_data['robot_id']}")
            st.write(f"**Type:** {robot_data['type']}")
            st.write(f"**Max Depth:** {robot_data['max_depth_m']}m")
            st.write(f"**Endurance:** {robot_data['endurance_hours']} hours")
            st.write(f"**Speed:** {robot_data['speed_knots']} knots")
            st.write(f"**Day Rate:** ${robot_data['day_rate_usd']:,}")

        with col2:
            st.markdown("### Status & Sensors")
            st.write(f"**Status:** {robot_data['status']}")
            st.write(f"**Last Maintenance:** {robot_data['last_maintenance']}")
            st.write(f"**Next Maintenance:** {robot_data['next_maintenance']}")

            st.markdown("**Sensors:**")
            for sensor in robot_data['sensors']:
                st.write(f"- {sensor.replace('_', ' ').title()}")

    # === CAPABILITY MATCHING PAGE ===
    elif page == "Capability Matching":
        st.header("Robot-Site Capability Matching")

        # Initialize matcher
        matcher = RobotSiteMatcher(robots, sites)

        tab1, tab2, tab3 = st.tabs(["Compatibility Matrix", "Site Analysis", "Equipment Gaps"])

        with tab1:
            st.subheader("Compatibility Matrix")
            st.caption("Shows compatibility scores (0-100) for each robot-site pair")

            compatibility_matrix = matcher.get_compatibility_matrix()

            heatmap = create_compatibility_heatmap(compatibility_matrix)
            st.plotly_chart(heatmap, use_container_width=True)

        with tab2:
            st.subheader("Detailed Compatibility Analysis")

            sites_df = pd.DataFrame(sites)
            robots_df = pd.DataFrame(robots)

            col1, col2 = st.columns(2)

            with col1:
                selected_site_name = st.selectbox(
                    "Select Site:",
                    sites_df['name'].tolist()
                )
                site_id = sites_df[sites_df['name'] == selected_site_name].iloc[0]['site_id']

            with col2:
                selected_robot_name = st.selectbox(
                    "Select Robot:",
                    robots_df['name'].tolist()
                )
                robot_id = robots_df[robots_df['name'] == selected_robot_name].iloc[0]['robot_id']

            # Get detailed compatibility
            compatibility = matcher.get_detailed_compatibility(robot_id, site_id)

            # Display results
            st.markdown(f"### Compatibility Score: {compatibility['compatibility_score']}/100")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.write(f"**Depth:** {compatibility['depth_message']}")

            with col2:
                st.write(f"**Sensors:** {compatibility['sensor_message']}")

            with col3:
                st.write(f"**Status:** {compatibility['status_message']}")

            # Best robots for selected site
            st.markdown("### Best Robots for This Site")
            best_robots = matcher.find_best_robots_for_site(site_id, top_n=5)

            for i, robot_match in enumerate(best_robots, 1):
                with st.expander(f"{i}. {robot_match['robot_name']} - Score: {robot_match['compatibility_score']:.1f}"):
                    st.write(f"**Type:** {robot_match['robot_type']}")
                    st.write(f"**Day Rate:** ${robot_match['day_rate_usd']:,}")
                    st.write(f"**Status:** {robot_match['overall_status']}")

        with tab3:
            st.subheader("Equipment Gap Analysis")

            gaps = matcher.identify_equipment_gaps()

            if gaps['depth_gaps']:
                st.warning(f"**Depth Coverage Gaps:** {len(gaps['depth_gaps'])} sites exceed fleet capabilities")

                gap_df = pd.DataFrame(gaps['depth_gaps'])
                st.dataframe(gap_df, height=200)
            else:
                st.success("All sites are within fleet depth capabilities")

            if gaps['sensor_gaps']:
                st.warning(f"**Missing Sensors:** {len(gaps['sensor_gaps'])} sensor types not in fleet")
                for sensor in gaps['sensor_gaps']:
                    st.write(f"- {sensor.replace('_', ' ').title()}")
            else:
                st.success("Fleet has all required sensor types")

            if gaps['recommendations']:
                st.markdown("### Recommendations")
                for rec in gaps['recommendations']:
                    st.info(rec)

    # === MISSION PLANNER PAGE ===
    elif page == "Mission Planner":
        st.header("Mission Planning & Optimization")

        st.sidebar.subheader("Mission Parameters")

        time_window = st.sidebar.slider("Planning Window (days)", 30, 365, 180, 30)
        budget = st.sidebar.number_input("Budget ($)", value=10000000, step=500000)
        vessel_speed = st.sidebar.slider("Vessel Speed (knots)", 8, 20, 12, 1)
        vessel_rate = st.sidebar.number_input("Vessel Day Rate ($)", value=75000, step=5000)
        prioritize_by = st.sidebar.selectbox("Prioritize Sites By", ["score", "value"])

        if st.sidebar.button("Generate Mission Plan", type="primary"):
            # Initialize optimizer
            scorer = SitePrioritizationEngine()
            scored_sites = scorer.score_sites(sites)
            matcher = RobotSiteMatcher(robots, sites)
            compatibility_matrix = matcher.get_compatibility_matrix()

            optimizer = MissionOptimizer(
                robots, scored_sites.to_dict('records'), compatibility_matrix
            )

            with st.spinner("Optimizing mission schedule..."):
                result = optimizer.greedy_mission_scheduler(
                    time_window_days=time_window,
                    budget_usd=budget,
                    vessel_speed_knots=vessel_speed,
                    vessel_day_rate=vessel_rate,
                    prioritize_by=prioritize_by
                )

            missions = result['missions']
            stats = result['statistics']

            # Store in session state
            st.session_state['missions'] = missions
            st.session_state['stats'] = stats

        # Display results if available
        if 'missions' in st.session_state:
            missions = st.session_state['missions']
            stats = st.session_state['stats']

            # Statistics
            st.subheader("Mission Plan Summary")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Missions", stats['total_missions'])

            with col2:
                st.metric("Sites Surveyed", stats['num_sites_surveyed'])

            with col3:
                st.metric("Total Cost", f"${stats['total_cost_usd']:,.0f}")

            with col4:
                st.metric("Coverage", f"{stats['coverage_percent']:.1f}%")

            # Tabs for different views
            tab1, tab2, tab3 = st.tabs(["Timeline", "Route Map", "Details"])

            with tab1:
                st.subheader("Mission Timeline")
                gantt_chart = create_gantt_chart(missions)
                st.plotly_chart(gantt_chart, use_container_width=True)

                col1, col2 = st.columns(2)

                with col1:
                    cost_chart = create_cost_breakdown_chart(missions)
                    st.plotly_chart(cost_chart, use_container_width=True)

                with col2:
                    st.markdown("### Budget Utilization")
                    st.write(f"**Budget:** ${budget:,.0f}")
                    st.write(f"**Spent:** ${stats['total_cost_usd']:,.0f}")
                    st.write(f"**Remaining:** ${stats['remaining_budget_usd']:,.0f}")
                    st.write(f"**Utilization:** {stats['budget_utilization_percent']:.1f}%")

                    st.progress(stats['budget_utilization_percent'] / 100)

            with tab2:
                st.subheader("Mission Routes")
                robots_df = pd.DataFrame(robots)
                route_map = create_mission_route_map(missions, robots_df)
                folium_static(route_map, width=None, height=600)

            with tab3:
                st.subheader("Mission Details")

                missions_df = pd.DataFrame(missions)
                display_cols = ['mission_id', 'robot_name', 'site_name', 'start_date',
                               'end_date', 'total_hours', 'cost_usd', 'compatibility_score']

                st.dataframe(
                    missions_df[display_cols].style.format({
                        'cost_usd': '${:,.0f}',
                        'compatibility_score': '{:.1f}'
                    }),
                    height=400
                )

                # Download missions as JSON
                missions_json = json.dumps(missions, indent=2, default=str)
                st.download_button(
                    label="Download Mission Plan (JSON)",
                    data=missions_json,
                    file_name="mission_plan.json",
                    mime="application/json"
                )

        else:
            st.info("Configure parameters and click 'Generate Mission Plan' to start optimization.")

    # === COVERAGE ANALYTICS PAGE ===
    elif page == "Coverage Analytics":
        st.header("Exploration Coverage Tracking")

        sites_df = pd.DataFrame(sites)
        robots_df = pd.DataFrame(robots)

        # Summary statistics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Sites", len(sites_df))

        with col2:
            # Count sites by survey quality
            high_quality = len(sites_df[sites_df['survey_data_quality'] >= 70])
            st.metric("High Quality Surveys", high_quality)

        with col3:
            low_quality = len(sites_df[sites_df['survey_data_quality'] < 40])
            st.metric("Sites Needing Survey", low_quality)

        # Coverage by jurisdiction
        st.subheader("Coverage by Jurisdiction")

        jurisdiction_stats = sites_df.groupby('jurisdiction').agg({
            'site_id': 'count',
            'survey_data_quality': 'mean',
            'estimated_value_millions': 'sum'
        }).reset_index()

        jurisdiction_stats.columns = ['Jurisdiction', 'Number of Sites',
                                      'Avg Survey Quality', 'Total Est. Value ($M)']

        st.dataframe(
            jurisdiction_stats.style.background_gradient(
                subset=['Avg Survey Quality'], cmap='RdYlGn'
            ).format({
                'Avg Survey Quality': '{:.1f}',
                'Total Est. Value ($M)': '{:.0f}'
            }),
            height=300
        )

        # Survey quality distribution
        st.subheader("Survey Data Quality Distribution")

        quality_bins = pd.cut(
            sites_df['survey_data_quality'],
            bins=[0, 40, 70, 100],
            labels=['Low (0-40)', 'Medium (40-70)', 'High (70-100)']
        )

        quality_counts = quality_bins.value_counts()

        col1, col2 = st.columns(2)

        with col1:
            import plotly.graph_objects as go
            fig = go.Figure(data=[go.Bar(
                x=quality_counts.index,
                y=quality_counts.values,
                marker=dict(color=['#d62728', '#ff7f0e', '#2ca02c'])
            )])
            fig.update_layout(
                title="Sites by Survey Quality",
                xaxis_title="Quality Level",
                yaxis_title="Number of Sites"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### Priority Survey Targets")
            low_quality_sites = sites_df[sites_df['survey_data_quality'] < 40].sort_values(
                'estimated_value_millions', ascending=False
            ).head(5)

            for _, site in low_quality_sites.iterrows():
                st.write(f"**{site['name']}**")
                st.write(f"- Quality: {site['survey_data_quality']}")
                st.write(f"- Est. Value: ${site['estimated_value_millions']}M")
                st.write(f"- Depth: {site['depth_m']}m")
                st.markdown("---")


if __name__ == "__main__":
    main()
