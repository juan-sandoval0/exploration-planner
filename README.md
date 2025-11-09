# Exploration Planner

I created a planning and optimization tool for deep-sea mining operations that combines exploration site analysis w/ robotics operations planning. This application helps prioritize potential mining sites and optimize ROV/AUV deployment for exploration missions.

## Overview

The Deep-Sea Exploration Planner is designed to:

- Evaluate and rank potential mining sites w/ multi-criteria analysis
- Manage a fleet of ROVs/AUVs with different capabilities
- Match robot capabilities to site requirements
- Optimize mission scheduling to maximize coverage within budget/coverage constraints
- Track exploration coverage and identify gaps

## Features

### 1. Site Prioritization Engine

- **Multi-Criteria Scoring**: Evaluates sites based on 7 weighted criteria based on research into the industry:
  - Mineral concentration (0-100)
  - Depth accessibility
  - Distance from port
  - Environmental sensitivity
  - Estimated mineral value
  - Seabed terrain difficulty
  - Existing survey data quality

- **Adjustable Weights**: Users can customize criterion weights w/ interactive sliders to align with business priorities

- **Economic Viability Calculator**: Calculates NPV, ROI, and profitability based on:
  - Extraction, refining, and transport costs
  - Difficulty multipliers depending on the sites
  - Estimated tonnage and mineral prices (sythetic, random in demo)

- **Priority Categorization**: Sites categorized as:
  - High Priority (score ≥70, ROI >50%)
  - Medium Priority (score ≥50, ROI >25%)
  - Further Study Needed (score ≥35)
  - Low Priority / Not Viable

### 2. Fleet Management Dashboard

- Robot database with specifications:
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
  - Depth rating verification w/ safety margins
  - Sensor requirement matching
  - Operational status checks
  - Compatibility scoring (0-100)

- **Compatibility Matrix**: My favorite part! Heatmap showing all robot-site pairs

- **Equipment Gap Identification**:
  - Sites unreachable by current fleet
  - Missing sensor capabilities
  - Recommendations for fleet expansion

### 4. Mission Planning Optimizer

- **Scheduling Algorithm** that optimizes:
  - Robot-to-site assignments
  - Mission sequencing
  - Transit route planning
  - Cost minimization

   This is a greedy scheduling algorithm but could be upgraded in next steps.

- **Constraints**:
  - Budget limits
  - Time windows
  - Robot availability and maintenance schedules
  - Endurance limits
  - No overlapping missions per robot

### 5. Coverage Analytics

- Track survey quality by region
- Identify high-value sites that need surveys
- Coverage statistics by site
- Survey quality distribution analysis

## Installation

### Prereqs

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

### Navigation

The application consists of five main sections accessible via the sidebar:

#### 1. Site Explorer

- View map of all potential sites
- Adjust scoring criteria weights
- Examine site rankings and detailed analytics
- Perform individual site economic analysis

#### 2. Fleet Management

- View complete robot inventory
- Check robot availability and status
- Review robot specifications and sensor capabilities
- Track maintenance schedules

**You can:**
- Filter by status to find available robots
- Compare day rates & capabilities
- Plan maintenance windows

#### 3. Capability Matching

- View compatibility matrix for all robot-site combinations
- Identify equipment gaps in the fleet

#### 4. Mission Planner

- Configure mission parameters (budget, time window, vessel speed)
- Generate optimized mission schedules
- Explore mission routes on interactive map
- Download mission plans as JSON

#### 5. Coverage Analytics

- Look at exploration coverage statistics
- Identify survey gaps by jurisdiction
- Find priority targets for future surveys

## Architecture

### Project Structure

```
exploration-planner/
├── app.py                  # Streamlit application
├── requirements.txt        # Python dependencies
├── README.md              
├── .gitignore             
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
- Cost calculations (includes vessel and operational costs)
- Route sequence generation

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

**Mission Optimization:**
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
- Uses Haversine formula w/ `geopy.distance.geodesic`
- Converts to transit time based on vessel speed

## Sample Data

I included 15 realistic deep-sea mining sites:

- **Pacific Ocean**: Clarion-Clipperton Zone, Peru Basin, Cook Islands EEZ
- **Atlantic Ocean**: Mid-Atlantic Ridge
- **Indian Ocean**: Indian Ocean Ridge
- **Regional EEZs**: New Zealand, Chile, Papua New Guinea, United States, Canada, Portugal, Ecuador

And 7 robots with diverse capabilities:

- **ROVs**: 3 work-class ROVs (4,000-6,000m depth rating)
- **AUVs**: 3 autonomous survey vehicles (3,000-7,000m depth rating)
- **Hybrid**: 1 ultra-deep hybrid ROV/AUV (11,000m depth rating)

### Some Limitations

- Optimizer uses greedy algorithm (not globally optimal)
- No weather/seasonal constraints in scheduling
- Simplified cost model (doesn't include mobilization, insurance)
- No multi-vessel support
- Survey area assumed constant at 25 km²

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (if available)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is provided as-is for demonstration purposes.

## Acknowledgments

- Built w/ [Streamlit](https://streamlit.io/) for the web interface
- Visualizations powered by [Plotly](https://plotly.com/) and [Folium](https://python-visualization.github.io/folium/)
- Geospatial calculations using [GeoPy](https://geopy.readthedocs.io/)
- Optimization algorithms using [SciPy](https://scipy.org/)

## Contact

For questions or support, contact juansd@stanford.edu

---

**Note**: This is a demonstration application with synthetic data. All site locations, mineral estimates, and economic figures are illustrative!
