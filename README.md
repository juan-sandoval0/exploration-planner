# Deep-Sea Critical Minerals Exploration Planner

An advanced planning and optimization tool for deep-sea mining operations that combines exploration site analysis with robotics operations planning. This application helps prioritize potential mining sites and optimize ROV/AUV deployment for exploration missions.

## Overview

The Deep-Sea Exploration Planner is designed for critical minerals mining companies to:

- Evaluate and rank potential mining sites using multi-criteria analysis
- Manage a fleet of deep-sea robots (ROVs/AUVs) with varying capabilities
- Match robot capabilities to site requirements
- Optimize mission scheduling to maximize coverage within budget and time constraints
- Track exploration coverage and identify gaps

## Features

### 1. Site Prioritization Engine

- **Multi-Criteria Scoring**: Evaluates sites based on 7 weighted criteria:
  - Mineral concentration (0-100)
  - Depth accessibility
  - Distance from port
  - Environmental sensitivity
  - Estimated mineral value
  - Seabed terrain difficulty
  - Existing survey data quality

- **Adjustable Weights**: Users can customize criterion weights via interactive sliders to align with business priorities

- **Economic Viability Calculator**: Calculates NPV, ROI, and profitability metrics based on:
  - Extraction, refining, and transport costs
  - Site-specific difficulty multipliers
  - Estimated tonnage and mineral prices

- **Priority Categorization**: Sites automatically categorized as:
  - High Priority (score ≥70, ROI >50%)
  - Medium Priority (score ≥50, ROI >25%)
  - Further Study Needed (score ≥35)
  - Low Priority / Not Viable

### 2. Fleet Management Dashboard

- Complete robot database with specifications:
  - Type (ROV, AUV, Hybrid)
  - Depth ratings (up to 11,000m)
  - Sensor packages
  - Endurance and speed
  - Operational status
  - Day rates

- Real-time status tracking (Available, In Maintenance, Deployed, Retired)
- Maintenance scheduling
- Fleet capability overview

### 3. Robot-Site Capability Matching

- **Compatibility Analysis**:
  - Depth rating verification with safety margins
  - Sensor requirement matching
  - Operational status checks
  - Compatibility scoring (0-100)

- **Compatibility Matrix**: Interactive heatmap showing all robot-site pairs

- **Equipment Gap Identification**:
  - Sites unreachable by current fleet
  - Missing sensor capabilities
  - Recommendations for fleet expansion

### 4. Mission Planning Optimizer

- **Greedy Scheduling Algorithm** that optimizes:
  - Robot-to-site assignments
  - Mission sequencing
  - Transit route planning
  - Cost minimization

- **Constraints**:
  - Budget limits
  - Time windows
  - Robot availability and maintenance schedules
  - Endurance limits
  - No overlapping missions per robot

- **Visualizations**:
  - Gantt chart timeline
  - Interactive route maps
  - Cost breakdown by robot
  - Coverage statistics

### 5. Coverage Analytics

- Track survey quality by region
- Identify high-value sites needing surveys
- Coverage statistics by jurisdiction
- Survey quality distribution analysis

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/exploration-planner.git
cd exploration-planner
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`.

### Navigation

The application consists of five main sections accessible via the sidebar:

#### 1. Site Explorer

- View global map of all potential mining sites
- Adjust scoring criteria weights
- Examine site rankings and detailed analytics
- Perform individual site economic analysis

**Usage Tips:**
- Adjust weight sliders to match your business priorities
- Click on map markers to see site details
- Use the radar chart to understand score composition
- Modify economic parameters to test different scenarios

#### 2. Fleet Management

- View complete robot inventory
- Check robot availability and status
- Review robot specifications and sensor capabilities
- Track maintenance schedules

**Usage Tips:**
- Filter by status to find available robots
- Compare day rates and capabilities
- Plan maintenance windows

#### 3. Capability Matching

- View compatibility matrix for all robot-site combinations
- Perform detailed compatibility analysis for specific pairs
- Identify equipment gaps in the fleet

**Usage Tips:**
- Look for green cells (high compatibility) in the matrix
- Review detailed compatibility to understand limitations
- Use gap analysis to inform fleet expansion decisions

#### 4. Mission Planner

- Configure mission parameters (budget, time window, vessel speed)
- Generate optimized mission schedules
- View mission timeline (Gantt chart)
- Explore mission routes on interactive map
- Download mission plans as JSON

**Usage Tips:**
- Start with default parameters and adjust based on results
- Increase budget to improve coverage
- Try different prioritization strategies (score vs. value)
- Export mission plans for integration with other systems

#### 5. Coverage Analytics

- Review exploration coverage statistics
- Identify survey gaps by jurisdiction
- Find priority targets for future surveys

**Usage Tips:**
- Focus on high-value sites with low survey quality
- Plan surveys to balance jurisdictional coverage
- Use analytics to justify survey investments

## Technical Architecture

### Project Structure

```
exploration-planner/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── .gitignore             # Git ignore rules
├── data/
│   ├── sites.json         # Sample mining site data
│   ├── robots.json        # Robot fleet data
│   └── missions.json      # Mission storage (generated)
├── src/
│   ├── scoring.py         # Site prioritization engine
│   ├── matching.py        # Robot-site compatibility logic
│   ├── optimizer.py       # Mission scheduling optimizer
│   └── visualization.py   # Plotting and mapping functions
├── notebooks/             # (Optional) Jupyter notebooks
└── screenshots/           # Application screenshots
```

### Core Modules

**scoring.py**: Implements the `SitePrioritizationEngine` class
- Multi-criteria normalization and weighted scoring
- Economic viability calculations (NPV, ROI)
- Priority categorization logic

**matching.py**: Implements the `RobotSiteMatcher` class
- Depth compatibility verification
- Sensor requirement matching
- Compatibility scoring algorithm
- Equipment gap analysis

**optimizer.py**: Implements the `MissionOptimizer` class
- Greedy mission scheduling algorithm
- Transit time calculations using geodesic distance
- Mission duration estimation
- Cost calculations including vessel and operational costs
- Route sequence generation

**visualization.py**: Visualization utilities
- Interactive Folium maps with site markers
- Plotly charts (bar, radar, heatmap, scatter, Gantt)
- Route visualization with color-coded robot paths

### Data Model

**Site Data Structure:**
```json
{
  "site_id": "SITE_001",
  "name": "Clarion-Clipperton Zone Alpha",
  "latitude": 14.5,
  "longitude": -130.2,
  "depth_m": 4500,
  "mineral_concentration": 85,
  "distance_from_port_km": 3200,
  "environmental_sensitivity": 45,
  "jurisdiction": "International Waters",
  "estimated_value_millions": 450,
  "terrain_difficulty": 35,
  "survey_data_quality": 60,
  "mineral_types": ["Polymetallic Nodules", "Manganese", "Nickel"]
}
```

**Robot Data Structure:**
```json
{
  "robot_id": "ROV_001",
  "name": "DeepSeeker Alpha",
  "type": "ROV",
  "max_depth_m": 6000,
  "sensors": ["magnetometer", "side_scan_sonar", "HD_camera"],
  "endurance_hours": 24,
  "speed_knots": 3,
  "status": "Available",
  "day_rate_usd": 50000,
  "current_location": {"lat": 15.0, "lon": -125.0}
}
```

### Algorithms

**Site Scoring Algorithm:**
1. Normalize each criterion to 0-100 scale
2. Apply inverse normalization for cost-type criteria (depth, distance, etc.)
3. Calculate weighted sum: `score = Σ(normalized_i × weight_i)`
4. Sort sites by composite score

**Mission Optimization (Greedy):**
1. Sort sites by priority (score or value)
2. For each site in order:
   - Find best compatible available robot
   - Calculate transit time and mission duration
   - Calculate total cost
   - Check budget and time constraints
   - Schedule mission if feasible
   - Update robot availability
3. Return mission schedule and statistics

**Distance Calculation:**
- Uses Haversine formula via `geopy.distance.geodesic`
- Accounts for Earth's curvature for accurate long-distance calculations
- Converts to transit time based on vessel speed

## Sample Data

The application includes 15 realistic deep-sea mining sites:

- **Pacific Ocean**: Clarion-Clipperton Zone, Peru Basin, Cook Islands EEZ
- **Atlantic Ocean**: Mid-Atlantic Ridge
- **Indian Ocean**: Indian Ocean Ridge
- **Regional EEZs**: New Zealand, Chile, Papua New Guinea, United States, Canada, Portugal, Ecuador

And 7 robots with diverse capabilities:

- **ROVs**: 3 work-class ROVs (4,000-6,000m depth rating)
- **AUVs**: 3 autonomous survey vehicles (3,000-7,000m depth rating)
- **Hybrid**: 1 ultra-deep hybrid ROV/AUV (11,000m depth rating)

## Future Enhancements

### Planned Features

1. **Advanced Optimization**
   - Genetic algorithm for mission scheduling
   - Multi-objective optimization (cost vs. coverage vs. time)
   - Weather window integration
   - Dynamic re-scheduling for mission delays

2. **Risk Assessment**
   - Environmental impact scoring
   - Regulatory compliance tracking
   - Technical risk evaluation
   - Financial risk modeling

3. **3D Visualization**
   - 3D bathymetric maps
   - Underwater terrain visualization
   - Robot depth profiles during missions

4. **Machine Learning**
   - Mineral concentration prediction from survey data
   - Mission duration prediction based on historical data
   - Optimal weight recommendation for site scoring

5. **Integration Capabilities**
   - API endpoints for external systems
   - Real-time robot telemetry integration
   - GIS data import/export
   - Database backend for production deployment

6. **Collaborative Features**
   - Multi-user access with role-based permissions
   - Mission review and approval workflows
   - Annotation and commenting on sites
   - Shared mission plans

7. **Reporting**
   - Automated report generation (PDF/Excel)
   - Executive dashboards
   - ROI analysis reports
   - Environmental compliance reports

### Known Limitations

- Current optimizer uses greedy algorithm (not globally optimal)
- No weather/seasonal constraints in scheduling
- Simplified cost model (doesn't include mobilization, insurance, etc.)
- No multi-vessel support
- Survey area assumed constant (25 km²)

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (if available)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines for Python code
- Use docstrings for all functions and classes
- Add type hints where appropriate
- Keep functions focused and modular

## License

This project is provided as-is for demonstration purposes.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/) for the web interface
- Visualizations powered by [Plotly](https://plotly.com/) and [Folium](https://python-visualization.github.io/folium/)
- Geospatial calculations using [GeoPy](https://geopy.readthedocs.io/)
- Optimization algorithms using [SciPy](https://scipy.org/)

## Contact

For questions or support, please open an issue on GitHub.

---

**Note**: This is a demonstration application with synthetic data. All site locations, mineral estimates, and economic figures are illustrative and should not be used for actual mining operations.
