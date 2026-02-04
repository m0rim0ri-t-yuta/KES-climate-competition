# Two Map Comparison: All Plants vs Large Plants (>360 MW)

## Overview
The updated `map_visualization.py` script now generates **two separate interactive maps** to provide different perspectives on US power infrastructure:

1. **All Power Plants Map** - Comprehensive view of all power generation facilities
2. **Large Power Plants Map** - Focused view of major power generation facilities (>360 MW)

---

## Map 1: All Power Plants
**Filename:** `data_centers_map_all_plants.html`

### Filtering Criteria
- **General Power Plants**: >10 MW capacity
- **Wind Power Plants**: >1 MW capacity
- **Solar Power Plants**: >1 MW capacity

### Statistics
| Category | Count |
|----------|-------|
| General Power Plants | 3,109 |
| Wind Power Plants | 1,345 |
| Solar Power Plants | 5,664 |
| **Total Power Facilities** | **10,118** |

### Use Cases
- **Comprehensive Analysis**: View the complete distribution of power generation infrastructure
- **Renewable Energy Trends**: See the widespread adoption of solar and wind power
- **Regional Patterns**: Identify areas with high density of smaller renewable installations
- **Infrastructure Planning**: Understand the full scope of power generation across the US

### Visual Characteristics
- **Dense Clustering**: Heavy concentration of orange (solar) and green (wind) markers
- **California**: Massive solar deployment visible along the coast and inland
- **Texas**: Balanced mix of all three power types
- **Midwest**: Dominated by wind farms (green circles)
- **East Coast**: Growing solar adoption

---

## Map 2: Large Power Plants (>360 MW)
**Filename:** `data_centers_map_large_plants.html`

### Filtering Criteria
- **General Power Plants**: >360 MW capacity
- **Wind Power Plants**: >360 MW capacity
- **Solar Power Plants**: >360 MW capacity

### Statistics
| Category | Count | Reduction from Map 1 |
|----------|-------|---------------------|
| General Power Plants | 810 | -74% (from 3,109) |
| Wind Power Plants | 29 | -98% (from 1,345) |
| Solar Power Plants | 13 | -99.8% (from 5,664) |
| **Total Power Facilities** | **852** | **-92% (from 10,118)** |

### Use Cases
- **Major Infrastructure Focus**: Identify the largest power generation facilities
- **Grid Backbone**: View the core power plants that provide the majority of electricity
- **Data Center Proximity**: Analyze large power plants near major data center hubs
- **Investment Analysis**: Focus on major power generation assets
- **Capacity Planning**: Understand where the bulk of power generation capacity is located

### Visual Characteristics
- **Clean, Uncluttered View**: Much easier to see individual facilities
- **Large Gray Circles**: Major coal, natural gas, nuclear, and hydro plants
- **Few Green Circles**: Only the largest wind farms (29 total)
- **Very Few Orange Circles**: Only 13 solar installations exceed 360 MW
- **Texas Prominence**: Large concentration of major power plants
- **Virginia Correlation**: Can clearly see relationship between data centers and nearby power infrastructure

---

## Key Insights from Comparison

### General Power Plants (Gray)
- **74% reduction** when filtering to >360 MW
- Large facilities are concentrated in:
  - **Texas** (diverse fuel mix)
  - **Southeast** (coal and nuclear)
  - **Northeast** (nuclear and natural gas)
  - **Pacific Northwest** (hydro)

### Wind Power (Green)
- **98% reduction** - most wind farms are smaller installations
- Only **29 wind farms** exceed 360 MW capacity
- Large wind farms concentrated in:
  - **Texas** (Panhandle and West Texas)
  - **Midwest** (Iowa, Kansas, Oklahoma)
  - **Great Plains** (North Dakota, South Dakota)

### Solar Power (Orange)
- **99.8% reduction** - solar is highly distributed with many small installations
- Only **13 solar plants** exceed 360 MW
- Large solar plants located in:
  - **California** (desert regions)
  - **Southwest** (Arizona, Nevada)
  - **Texas** (West Texas)

### Data Center Correlation
- **Virginia** (568 data centers) shows nearby large power infrastructure
- **Texas** (392 data centers) has abundant large-scale power generation
- **California** (288 data centers) relies on mix of large and distributed solar

---

## Technical Details

### Map Generation Function
Both maps use the same `create_map()` function with different filtering parameters:

```python
def create_map(df, gen_plants, wind_plants, solar_plants, title, output_file):
    # Creates choropleth + scatter geo overlay
    # Customizable title and output filename
```

### Circle Sizing
- **General Plants**: `size = capacity / 50`
- **Wind Plants**: `size = capacity / 20`
- **Solar Plants**: `size = capacity / 20`

### Color Scheme
- **Choropleth**: Viridis (purple → teal → green → yellow)
- **General Plants**: Gray (`rgba(100, 100, 100, 0.6)`)
- **Wind Plants**: Green (`rgba(34, 139, 34, 0.7)`)
- **Solar Plants**: Orange (`rgba(255, 165, 0, 0.7)`)

---

## Files Generated

1. **data_centers_map_all_plants.html** - All power plants (10,118 facilities)
2. **data_centers_map_large_plants.html** - Large plants only (852 facilities)

Both maps include:
- Interactive tooltips with plant name, location, and capacity
- Toggleable legend
- Zoom/pan controls
- Statistics summary at bottom
- Data center choropleth layer

---

## Recommendations

### Use Map 1 (All Plants) When:
- Analyzing renewable energy adoption trends
- Understanding distributed generation
- Studying regional energy diversity
- Planning new installations in relation to existing infrastructure

### Use Map 2 (Large Plants >360 MW) When:
- Focusing on major power generation assets
- Analyzing grid backbone infrastructure
- Studying data center power requirements
- Identifying potential large-scale energy partners
- Simplifying visualization for presentations

---

## Why 360 MW Threshold?

The 360 MW threshold was chosen to:
1. **Focus on Major Facilities**: Captures the largest power generation assets
2. **Reduce Visual Clutter**: 92% reduction in markers makes the map much clearer
3. **Grid Significance**: Plants >360 MW typically represent major grid infrastructure
4. **Data Center Scale**: Aligns with the power requirements of large data center campuses
5. **Industry Standard**: Common threshold for "large-scale" power generation

---

## Future Enhancements

Potential additions to both maps:
- [ ] Add energy source type filtering (coal, nuclear, natural gas, hydro)
- [ ] Include transmission line data
- [ ] Show renewable energy percentage by state
- [ ] Add time-series animation for capacity growth
- [ ] Include energy storage facilities (batteries)
- [ ] Calculate distance from data centers to nearest large power plants
- [ ] Add power purchase agreement (PPA) data if available
