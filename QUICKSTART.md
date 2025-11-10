# Quick Start Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

### 1. Navigate to the project directory

```bash
cd exploration-planner
```

### 2. Create a virtual environment (recommended)

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Streamlit (web framework)
- Plotly (interactive charts)
- Folium (mapping)
- Pandas (data manipulation)
- NumPy (numerical computing)
- SciPy (optimization)
- GeoPy (geospatial calculations)

### 4. Verify installation

```bash
python test_installation.py
```

You should see "SUCCESS: All tests passed!"

## Running the Application

### Start the Streamlit app

```bash
streamlit run app.py
```

The application will automatically open in your default browser at `http://localhost:8501`.

## Example Workflows

### Scenario 1: Find the Best Site

1. Go to "Site Explorer"
2. Increase the "Estimated Value" weight to 0.30
3. Decrease "Environmental Risk" to 0.10
4. Check the rankings - highest value sites now rank higher
5. Select top site and run economic analysis

### Scenario 2: Plan a Survey Campaign

1. Go to "Mission Planner"
2. Set budget to $5,000,000
3. Set planning window to 90 days
4. Click "Generate Mission Plan"
5. Review the Gantt chart to see timeline
6. Check the route map to visualize robot paths
7. Download the plan for your team

### Scenario 3: Evaluate Fleet Needs

1. Go to "Capability Matching"
2. View the compatibility matrix
3. Go to "Equipment Gaps" tab
4. Review recommendations for fleet expansion
5. Note any deep sites that can't be reached

## Customization

### Modify Site Data

Edit `data/sites.json` to:
- Add new sites
- Update mineral concentrations
- Change jurisdictions
- Adjust estimated values

### Modify Robot Fleet

Edit `data/robots.json` to:
- Add new robots
- Update specifications
- Change availability status
- Modify day rates

### Adjust Scoring Weights

In the Site Explorer, use the sidebar sliders to adjust:
- Mineral Concentration importance
- Depth accessibility preference
- Distance from port impact
- Environmental risk tolerance
- Value prioritization
- Terrain difficulty concern
- Survey quality importance

## Troubleshooting

### Application won't start

**Error: `ModuleNotFoundError`**
- Solution: Run `pip install -r requirements.txt`

**Error: `streamlit: command not found`**
- Solution: Ensure virtual environment is activated

### Data loading errors

**Error: `FileNotFoundError: data/sites.json`**
- Solution: Ensure you're running from the `exploration-planner` directory

### Performance issues

**Slow map rendering:**
- This is normal with 15 sites; real deployments should use data filtering

**Gantt chart not displaying:**
- Ensure you've clicked "Generate Mission Plan" first
- Check that budget and time window allow for missions

## Getting Help

- Check the full [README.md](README.md) for detailed documentation
- Review the [Jupyter notebook](notebooks/analysis_demo.ipynb) for API examples
- Run `python test_installation.py` to diagnose issues

## Next Steps

1. Explore all five tabs to understand capabilities
2. Try different scoring weights to see how priorities change
3. Modify the sample data to match your use case
4. Export mission plans and share with your team
5. Review the source code in `src/` to understand algorithms

---

**Tip:** The application uses caching, so navigation between tabs is fast after the initial load.
