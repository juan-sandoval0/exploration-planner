"""
Visualization Utilities

This module provides functions for creating interactive visualizations
including maps, charts, and mission timelines.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import folium
from folium import plugins
from typing import Dict, List
from datetime import datetime, timedelta


def create_site_map(sites_df: pd.DataFrame, color_by: str = 'composite_score') -> folium.Map:
    """
    Create an interactive map of mining sites.

    Args:
        sites_df: DataFrame with site information
        color_by: Column to use for color coding

    Returns:
        Folium map object
    """
    # Center map on mean coordinates
    center_lat = sites_df['latitude'].mean()
    center_lon = sites_df['longitude'].mean()

    # Create base map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=2,
        tiles='OpenStreetMap'
    )

    # Add different tile layers
    folium.TileLayer('CartoDB positron').add_to(m)
    folium.TileLayer('CartoDB dark_matter').add_to(m)

    # Determine color scale
    if color_by in sites_df.columns:
        min_val = sites_df[color_by].min()
        max_val = sites_df[color_by].max()

        for _, site in sites_df.iterrows():
            value = site[color_by]

            # Normalize to 0-1 for color mapping
            normalized = (value - min_val) / (max_val - min_val) if max_val > min_val else 0.5

            # Color scale from red (low) to green (high)
            if normalized < 0.33:
                color = 'red'
            elif normalized < 0.67:
                color = 'orange'
            else:
                color = 'green'

            # Create popup content
            popup_html = f"""
            <div style="font-family: Arial; font-size: 12px; width: 250px;">
                <h4 style="margin: 0 0 10px 0;">{site['name']}</h4>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr><td><b>Site ID:</b></td><td>{site['site_id']}</td></tr>
                    <tr><td><b>Depth:</b></td><td>{site['depth_m']}m</td></tr>
                    <tr><td><b>Mineral Conc.:</b></td><td>{site['mineral_concentration']}</td></tr>
                    <tr><td><b>Est. Value:</b></td><td>${site['estimated_value_millions']}M</td></tr>
                    <tr><td><b>Distance from Port:</b></td><td>{site['distance_from_port_km']}km</td></tr>
                    <tr><td><b>Jurisdiction:</b></td><td>{site['jurisdiction']}</td></tr>
                </table>
            </div>
            """

            # Add marker
            folium.CircleMarker(
                location=[site['latitude'], site['longitude']],
                radius=8,
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=site['site_id'],
                color='black',
                fillColor=color,
                fillOpacity=0.8,
                weight=2
            ).add_to(m)

    # Add layer control
    folium.LayerControl().add_to(m)

    return m


def create_priority_chart(sites_df: pd.DataFrame) -> go.Figure:
    """
    Create bar chart of site priorities.

    Args:
        sites_df: DataFrame with site scores

    Returns:
        Plotly figure
    """
    # Sort by composite score
    df_sorted = sites_df.sort_values('composite_score', ascending=True)

    # Color code by score
    colors = ['#2ca02c' if score >= 70 else '#ff7f0e' if score >= 50
              else '#1f77b4' if score >= 35 else '#d62728'
              for score in df_sorted['composite_score']]

    fig = go.Figure(data=[
        go.Bar(
            y=df_sorted['name'],
            x=df_sorted['composite_score'],
            orientation='h',
            marker=dict(color=colors),
            text=df_sorted['composite_score'].round(1),
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Score: %{x:.1f}<extra></extra>'
        )
    ])

    fig.update_layout(
        title='Site Priority Rankings',
        xaxis_title='Composite Score',
        yaxis_title='',
        height=max(400, len(df_sorted) * 25),
        showlegend=False,
        margin=dict(l=200)
    )

    return fig


def create_score_breakdown_chart(score_components: Dict[str, float],
                                 weights: Dict[str, float]) -> go.Figure:
    """
    Create radar chart showing score breakdown for a site.

    Args:
        score_components: Dictionary of score components
        weights: Dictionary of weights for each component

    Returns:
        Plotly figure
    """
    categories = list(score_components.keys())
    values = list(score_components.values())

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Score Components'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=False,
        title='Score Breakdown by Component'
    )

    return fig


def create_compatibility_heatmap(compatibility_matrix: pd.DataFrame) -> go.Figure:
    """
    Create heatmap of robot-site compatibility scores.

    Args:
        compatibility_matrix: DataFrame with compatibility scores

    Returns:
        Plotly figure
    """
    # Extract robot columns (exclude site_id and site_name)
    robot_cols = [col for col in compatibility_matrix.columns
                  if col not in ['site_id', 'site_name']]

    # Create heatmap data
    heatmap_data = compatibility_matrix[robot_cols].values
    y_labels = compatibility_matrix['site_name'].values

    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data,
        x=robot_cols,
        y=y_labels,
        colorscale=[
            [0, '#d62728'],      # Red for incompatible
            [0.4, '#ff7f0e'],    # Orange for partial
            [0.7, '#ffff00'],    # Yellow for good
            [1, '#2ca02c']       # Green for excellent
        ],
        colorbar=dict(title='Compatibility<br>Score'),
        hovertemplate='Robot: %{x}<br>Site: %{y}<br>Score: %{z:.1f}<extra></extra>'
    ))

    fig.update_layout(
        title='Robot-Site Compatibility Matrix',
        xaxis_title='Robot ID',
        yaxis_title='Site Name',
        height=max(500, len(y_labels) * 25),
        margin=dict(l=200)
    )

    return fig


def create_gantt_chart(missions: List[Dict]) -> go.Figure:
    """
    Create Gantt chart for mission timeline.

    Args:
        missions: List of mission dictionaries

    Returns:
        Plotly figure
    """
    if not missions:
        # Return empty figure
        fig = go.Figure()
        fig.add_annotation(
            text="No missions scheduled",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20)
        )
        return fig

    # Prepare data for Gantt chart
    gantt_data = []
    for mission in missions:
        gantt_data.append({
            'Task': f"{mission['robot_name']}",
            'Start': mission['start_date'],
            'Finish': mission['end_date'],
            'Resource': mission['site_name'],
            'Mission': mission['mission_id']
        })

    df = pd.DataFrame(gantt_data)

    # Create figure
    fig = go.Figure()

    # Color map for different robots
    unique_robots = df['Task'].unique()
    colors = px.colors.qualitative.Set3[:len(unique_robots)]
    color_map = dict(zip(unique_robots, colors))

    for _, row in df.iterrows():
        fig.add_trace(go.Bar(
            x=[row['Finish'] - row['Start']],
            y=[row['Task']],
            base=row['Start'],
            orientation='h',
            marker=dict(color=color_map[row['Task']]),
            name=row['Task'],
            showlegend=False,
            hovertemplate=(
                f"<b>{row['Mission']}</b><br>"
                f"Robot: {row['Task']}<br>"
                f"Site: {row['Resource']}<br>"
                f"Start: {row['Start'].strftime('%Y-%m-%d %H:%M')}<br>"
                f"End: {row['Finish'].strftime('%Y-%m-%d %H:%M')}<br>"
                "<extra></extra>"
            )
        ))

    fig.update_layout(
        title='Mission Timeline (Gantt Chart)',
        xaxis_title='Date',
        yaxis_title='Robot',
        barmode='overlay',
        height=max(400, len(unique_robots) * 80),
        showlegend=False
    )

    return fig


def create_mission_route_map(missions: List[Dict], robots_df: pd.DataFrame) -> folium.Map:
    """
    Create map showing mission routes.

    Args:
        missions: List of mission dictionaries
        robots_df: DataFrame with robot information

    Returns:
        Folium map object
    """
    # Calculate center point
    if missions:
        lats = [m['site_latitude'] for m in missions]
        lons = [m['site_longitude'] for m in missions]
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)
    else:
        center_lat = 0
        center_lon = 0

    # Create map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=2,
        tiles='OpenStreetMap'
    )

    # Color map for robots
    robot_colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'cadetblue']

    # Group missions by robot
    robot_missions = {}
    for mission in missions:
        robot_id = mission['robot_id']
        if robot_id not in robot_missions:
            robot_missions[robot_id] = []
        robot_missions[robot_id].append(mission)

    # Draw routes for each robot
    for idx, (robot_id, missions_list) in enumerate(robot_missions.items()):
        color = robot_colors[idx % len(robot_colors)]

        # Get robot's starting position
        robot = robots_df[robots_df['robot_id'] == robot_id].iloc[0]
        current_pos = [robot['current_location']['lat'], robot['current_location']['lon']]

        # Add starting marker
        folium.Marker(
            location=current_pos,
            icon=folium.Icon(color=color, icon='home'),
            popup=f"{robot['name']} - Starting Position"
        ).add_to(m)

        # Sort missions by start date
        missions_sorted = sorted(missions_list, key=lambda x: x['start_date'])

        # Draw route
        route_coords = [current_pos]

        for mission in missions_sorted:
            site_pos = [mission['site_latitude'], mission['site_longitude']]
            route_coords.append(site_pos)

            # Add site marker
            folium.CircleMarker(
                location=site_pos,
                radius=6,
                color=color,
                fillColor=color,
                fillOpacity=0.7,
                popup=f"{mission['mission_id']}<br>{mission['site_name']}"
            ).add_to(m)

        # Draw route line
        folium.PolyLine(
            route_coords,
            color=color,
            weight=2,
            opacity=0.7,
            popup=f"{robot['name']} Route"
        ).add_to(m)

    return m


def create_cost_breakdown_chart(missions: List[Dict]) -> go.Figure:
    """
    Create pie chart of cost breakdown by robot.

    Args:
        missions: List of mission dictionaries

    Returns:
        Plotly figure
    """
    if not missions:
        fig = go.Figure()
        fig.add_annotation(
            text="No missions to display",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20)
        )
        return fig

    # Aggregate costs by robot
    robot_costs = {}
    for mission in missions:
        robot_name = mission['robot_name']
        if robot_name not in robot_costs:
            robot_costs[robot_name] = 0
        robot_costs[robot_name] += mission['cost_usd']

    fig = go.Figure(data=[go.Pie(
        labels=list(robot_costs.keys()),
        values=list(robot_costs.values()),
        hovertemplate='<b>%{label}</b><br>Cost: $%{value:,.0f}<br>%{percent}<extra></extra>'
    )])

    fig.update_layout(
        title='Mission Cost Distribution by Robot'
    )

    return fig


def create_depth_distribution_chart(sites_df: pd.DataFrame) -> go.Figure:
    """
    Create histogram of site depth distribution.

    Args:
        sites_df: DataFrame with site information

    Returns:
        Plotly figure
    """
    fig = go.Figure(data=[go.Histogram(
        x=sites_df['depth_m'],
        nbinsx=15,
        marker=dict(color='#1f77b4', line=dict(color='black', width=1))
    )])

    fig.update_layout(
        title='Distribution of Site Depths',
        xaxis_title='Depth (meters)',
        yaxis_title='Number of Sites',
        showlegend=False
    )

    return fig


def create_value_vs_difficulty_scatter(sites_df: pd.DataFrame) -> go.Figure:
    """
    Create scatter plot of estimated value vs. terrain difficulty.

    Args:
        sites_df: DataFrame with site information

    Returns:
        Plotly figure
    """
    fig = go.Figure(data=[go.Scatter(
        x=sites_df['terrain_difficulty'],
        y=sites_df['estimated_value_millions'],
        mode='markers+text',
        text=sites_df['site_id'],
        textposition='top center',
        marker=dict(
            size=sites_df['mineral_concentration'] / 5,
            color=sites_df['composite_score'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title='Composite<br>Score'),
            line=dict(width=1, color='black')
        ),
        hovertemplate=(
            '<b>%{text}</b><br>'
            'Terrain Difficulty: %{x}<br>'
            'Estimated Value: $%{y}M<br>'
            '<extra></extra>'
        )
    )])

    fig.update_layout(
        title='Site Value vs. Terrain Difficulty',
        xaxis_title='Terrain Difficulty',
        yaxis_title='Estimated Value ($ Millions)',
        showlegend=False
    )

    return fig
