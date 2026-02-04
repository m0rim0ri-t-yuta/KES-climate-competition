# Enhanced US Data Centers and Power Plants Visualization

## Overview
This interactive map combines data center distribution across US states with detailed power plant locations, showing general generators, wind farms, and solar installations.

## Data Sources
1. **Data Centers by State** - CSV file with counts for all 51 states/territories
2. **Power Plant Locations** - EIA-860 2024 Plant data with coordinates
3. **Generator Data** - EIA-860 2024 Generator capacity data
4. **Wind Power** - EIA-860 2024 Wind generator data
5. **Solar Power** - EIA-860 2024 Solar generator data

## Visualization Features

### Choropleth Layer (State-Level Data Centers)
- **Color Scale**: Dark purple (fewer) to bright yellow (most data centers)
- **Interactive**: Click or hover over states to see exact data center counts
- **Top States**: Virginia (568), Texas (392), California (288)

### Power Plant Markers

#### 🔘 General Power Plants (Gray Circles)
- **Color**: Gray with dark gray outline
- **Size**: Proportional to nameplate capacity (MW)
- **Count**: 3,109 plants (>10 MW capacity)
- **Scale**: Circle size = Capacity / 50
- **Examples**: Coal, natural gas, nuclear, hydro plants

#### 🟢 Wind Power Plants (Green Circles)
- **Color**: Green (rgba(34, 139, 34, 0.7))
- **Size**: Proportional to wind capacity (MW)
- **Count**: 1,345 wind farms (>1 MW capacity)
- **Scale**: Circle size = Capacity / 20
- **Distribution**: Concentrated in Midwest, Texas, and Great Plains

#### 🟠 Solar Power Plants (Orange Circles)
- **Color**: Orange (rgba(255, 165, 0, 0.7))
- **Size**: Proportional to solar capacity (MW)
- **Count**: 5,664 solar installations (>1 MW capacity)
- **Scale**: Circle size = Capacity / 20
- **Distribution**: Heavy concentration in Southwest and East Coast

## Key Statistics

### Data Centers
- **Total**: 3,958 data centers across 51 states/territories
- **Top 3 States**: Virginia (568), Texas (392), California (288)
- **Smallest**: Vermont (3), South Dakota (5), DC (6)

### Power Generation Infrastructure
- **General Power Plants**: 3,109 facilities
- **Wind Farms**: 1,345 installations
- **Solar Plants**: 5,664 installations
- **Total Power Facilities**: 10,118 mapped locations

## Geographic Insights

### Data Center Hotspots
1. **Mid-Atlantic** (Virginia): Highest concentration due to proximity to DC and favorable business climate
2. **Texas**: Second-highest, benefiting from low energy costs and business-friendly regulations
3. **California**: Tech hub with significant cloud infrastructure
4. **Illinois**: Major connectivity hub (Chicago)

### Renewable Energy Distribution
- **Wind Power**: Dominant in the Great Plains (Kansas, Oklahoma, Texas) and Midwest (Iowa, Minnesota)
- **Solar Power**: Concentrated in:
  - Southwest (California, Arizona, Nevada) - high solar irradiance
  - East Coast (North Carolina, Virginia) - policy incentives
  - Texas - diverse energy portfolio

### Energy-Data Center Correlation
- States with high data center counts (VA, TX, CA) also show significant power generation infrastructure
- Renewable energy installations are growing rapidly in data center-heavy regions
- Texas shows balanced distribution of all three power types

## Interactive Features
1. **Hover/Click States**: View data center counts
2. **Hover/Click Power Plants**: See plant name, location, and capacity
3. **Legend**: Toggle visibility of different power plant types
4. **Zoom/Pan**: Explore specific regions in detail
5. **Color Bar**: Reference for data center density

## Technical Implementation
- **Framework**: Plotly (Python)
- **Map Type**: Choropleth + Scatter Geo overlay
- **Projection**: Albers USA (optimized for US territories)
- **Data Processing**: Pandas for Excel/CSV handling
- **Output**: Interactive HTML file

## How to Use
1. Open `data_centers_map.html` in any modern web browser
2. Use mouse to hover over states and power plants for details
3. Click legend items to show/hide specific power plant types
4. Use Plotly controls (top-right) to zoom, pan, or reset view
5. Download static image using camera icon

## Color Legend
- **Choropleth (States)**: Purple → Teal → Green → Yellow (increasing data centers)
- **Gray Circles**: General power plants (fossil, nuclear, hydro)
- **Green Circles**: Wind power installations
- **Orange Circles**: Solar power installations

## File Structure
```
Data Center/
├── data_centers.csv              # State-level data center counts
├── map_visualization.py          # Python script to generate map
├── data_centers_map.html         # Interactive visualization output
└── eia8602024/                   # EIA power plant data
    ├── 2___Plant_Y2024.xlsx      # Plant locations (lat/lon)
    ├── 3_1_Generator_Y2024.xlsx  # General generator capacity
    ├── 3_2_Wind_Y2024.xlsx       # Wind generator capacity
    └── 3_3_Solar_Y2024.xlsx      # Solar generator capacity
```

## Future Enhancements
- Add transmission line data
- Include energy consumption by data centers
- Show renewable energy percentage by state
- Add time-series animation for capacity growth
- Include energy storage facilities (batteries)
