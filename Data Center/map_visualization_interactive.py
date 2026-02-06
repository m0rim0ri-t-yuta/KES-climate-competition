import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

# State name to abbreviation mapping
state_abbrev = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
    'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
    'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
    'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
    'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
    'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
    'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY',
    'District of Columbia': 'DC'
}

print("Loading data files...")

# Read the geocoded data center CSV file
df = pd.read_csv('datacenters_with_coords.csv')
# Extract state from address for state mapping
df['State'] = df['Address'].str.extract(r',\s*([A-Z]{2})[,\s]', expand=False)
df['State_Code'] = df['State']

# Load Power Plant location data (EIA-860)
plant_df = pd.read_excel('eia8602024/2___Plant_Y2024.xlsx', header=1)
print(f"Loaded {len(plant_df)} power plants")

# Load Generator data
gen_df = pd.read_excel('eia8602024/3_1_Generator_Y2024.xlsx', header=1)
print(f"Loaded {len(gen_df)} generators")

# Load Wind data
wind_df = pd.read_excel('eia8602024/3_2_Wind_Y2024.xlsx', header=1)
print(f"Loaded {len(wind_df)} wind generators")

# Load Solar data
solar_df = pd.read_excel('eia8602024/3_3_Solar_Y2024.xlsx', header=1)
print(f"Loaded {len(solar_df)} solar generators")


print("\nProcessing power plant data...")

# Clean plant location data
plant_df['Latitude'] = pd.to_numeric(plant_df['Latitude'], errors='coerce')
plant_df['Longitude'] = pd.to_numeric(plant_df['Longitude'], errors='coerce')
plant_df = plant_df.dropna(subset=['Latitude', 'Longitude'])

# Process Generator data (Split into Nuclear, Gas, and Others)
gen_df['Nameplate Capacity (MW)'] = pd.to_numeric(gen_df['Nameplate Capacity (MW)'], errors='coerce')

# Nuclear
nuc_df = gen_df[gen_df['Energy Source 1'] == 'NUC']
nuc_capacity = nuc_df.groupby('Plant Code')['Nameplate Capacity (MW)'].sum().reset_index()
nuc_capacity.columns = ['Plant Code', 'nuclear_capacity_mw']

# Gas (Natural Gas)
# Using 'NG' for Natural Gas. 'OG' is Other Gas, but usually NG is the main one.
gas_df = gen_df[gen_df['Energy Source 1'] == 'NG']
gas_capacity = gas_df.groupby('Plant Code')['Nameplate Capacity (MW)'].sum().reset_index()
gas_capacity.columns = ['Plant Code', 'gas_capacity_mw']

# Other (Everything else in gen_df: Coal, Hydro, Oil, etc.)
# We exclude NUC and NG to get "Other General"
other_gen_df = gen_df[~gen_df['Energy Source 1'].isin(['NUC', 'NG'])]
other_capacity = other_gen_df.groupby('Plant Code')['Nameplate Capacity (MW)'].sum().reset_index()
other_capacity.columns = ['Plant Code', 'other_capacity_mw']


# Process Wind data
wind_df['Nameplate Capacity (MW)'] = pd.to_numeric(wind_df['Nameplate Capacity (MW)'], errors='coerce')
wind_capacity = wind_df.groupby('Plant Code')['Nameplate Capacity (MW)'].sum().reset_index()
wind_capacity.columns = ['Plant Code', 'wind_capacity_mw']

# Process Solar data
solar_df['Nameplate Capacity (MW)'] = pd.to_numeric(solar_df['Nameplate Capacity (MW)'], errors='coerce')
solar_capacity = solar_df.groupby('Plant Code')['Nameplate Capacity (MW)'].sum().reset_index()
solar_capacity.columns = ['Plant Code', 'solar_capacity_mw']

# Merge location data with capacity data
plant_locations = plant_df[['Plant Code', 'Plant Name', 'State', 'City', 'Latitude', 'Longitude']].copy()

# Merge all capacity types
plant_locations = plant_locations.merge(nuc_capacity, on='Plant Code', how='left')
plant_locations = plant_locations.merge(gas_capacity, on='Plant Code', how='left')
plant_locations = plant_locations.merge(other_capacity, on='Plant Code', how='left')
plant_locations = plant_locations.merge(wind_capacity, on='Plant Code', how='left')
plant_locations = plant_locations.merge(solar_capacity, on='Plant Code', how='left')

# Fill NaN values with 0
plant_locations['nuclear_capacity_mw'] = plant_locations['nuclear_capacity_mw'].fillna(0)
plant_locations['gas_capacity_mw'] = plant_locations['gas_capacity_mw'].fillna(0)
plant_locations['other_capacity_mw'] = plant_locations['other_capacity_mw'].fillna(0)
plant_locations['wind_capacity_mw'] = plant_locations['wind_capacity_mw'].fillna(0)
plant_locations['solar_capacity_mw'] = plant_locations['solar_capacity_mw'].fillna(0)

# Calculate Total Capacity primarily for filtering valid plants (avoid 0 capacity)
plant_locations['total_capacity_mw'] = (
    plant_locations['nuclear_capacity_mw'] + 
    plant_locations['gas_capacity_mw'] + 
    plant_locations['other_capacity_mw'] + 
    plant_locations['wind_capacity_mw'] + 
    plant_locations['solar_capacity_mw']
)

# Separate into different categories
# We define distinct sets. A plant might have multiple types (hybrid), but usually dominant.
# For map simplicity, we can categorize by presence.
# If a plant has >0 capacity in a category, it's included in that list.
# This means a hybrid plant might appear as two dots (likely overplotted), or we prioritize.
# Given the typical distinct nature (Wind farm vs Nuke plant), simple filtering is fine.

nuclear_plants = plant_locations[plant_locations['nuclear_capacity_mw'] > 0].copy()
gas_plants = plant_locations[plant_locations['gas_capacity_mw'] > 0].copy()
wind_plants = plant_locations[plant_locations['wind_capacity_mw'] > 0].copy()
solar_plants = plant_locations[plant_locations['solar_capacity_mw'] > 0].copy()

# For "General", we mean specifically the "Other" category (Coal, Hydro, etc.)
# Renaming 'other_capacity_mw' to be used for 'General' display
gen_plants = plant_locations[plant_locations['other_capacity_mw'] > 0].copy()


print(f"Found {len(nuclear_plants)} nuclear power plants")
print(f"Found {len(gas_plants)} gas power plants")
print(f"Found {len(gen_plants)} general (coal/hydro/other) power plants")
print(f"Found {len(wind_plants)} wind power plants")
print(f"Found {len(solar_plants)} solar power plants")

print("\nCreating base choropleth map with px.choropleth...")

# Aggregate data centers by state for the choropleth
state_summary = df.groupby('State_Code').size().reset_index(name='Data Centers')
state_summary['State'] = state_summary['State_Code']

# Create the base choropleth map using plotly.express
fig = px.choropleth(
    state_summary,
    locations='State_Code',
    locationmode='USA-states',
    color='Data Centers',
    scope='usa',
    # Custom Columbia Blue Color Scheme
    # Light (#EDF4F9) -> Dark (#003366)
    color_continuous_scale=[
        '#EDF4F9', # 6. Pale Azure (Background)
        '#D9E8F0', # 5. Sky Mist
        '#C4D8E2', # 4. Columbia Blue (Base)
        '#5F8EB0', # 3. Medium Blue
        '#2C5E8A', # 2. Royal Blue
        '#003366'  # 1. Deep Blue (Important)
    ],
    labels={'Data Centers': 'Number of Data Centers'},
    title='US Data Centers and Power Plants Distribution (Interactive Filter)',
    hover_name='State',
    hover_data={'Data Centers': True, 'State_Code': False}
)

# Update layout
fig.update_layout(
    title_font_size=24,
    title_x=0.5,
    geo=dict(
        showlakes=True,
        lakecolor='rgb(255, 255, 255)'
    ),
    height=800,
    showlegend=True,
    legend=dict(
        x=0.02,
        y=0.98,
        bgcolor='rgba(255, 255, 255, 0.8)',
        bordercolor='rgba(0, 0, 0, 0.3)',
        borderwidth=1
    )
)

# Prepare data as JSON for JavaScript filtering
# IMPORTANT: Replace NaN with None so json.dumps outputs 'null' instead of 'NaN' (which is valid JS but can cause issues)
# Or better, drop rows with missing coordinates for plotting
nuclear_plants = nuclear_plants.dropna(subset=['Latitude', 'Longitude'])
gas_plants = gas_plants.dropna(subset=['Latitude', 'Longitude'])
gen_plants = gen_plants.dropna(subset=['Latitude', 'Longitude'])
wind_plants = wind_plants.dropna(subset=['Latitude', 'Longitude'])
solar_plants = solar_plants.dropna(subset=['Latitude', 'Longitude'])
df_clean = df.dropna(subset=['Latitude', 'Longitude'])

nuc_plants_json = nuclear_plants[['Longitude', 'Latitude', 'Plant Name', 'City', 'State', 'nuclear_capacity_mw']].fillna(0).to_dict('records')
gas_plants_json = gas_plants[['Longitude', 'Latitude', 'Plant Name', 'City', 'State', 'gas_capacity_mw']].fillna(0).to_dict('records')
gen_plants_json = gen_plants[['Longitude', 'Latitude', 'Plant Name', 'City', 'State', 'other_capacity_mw']].fillna(0).to_dict('records')
wind_plants_json = wind_plants[['Longitude', 'Latitude', 'Plant Name', 'City', 'State', 'wind_capacity_mw']].fillna(0).to_dict('records')
solar_plants_json = solar_plants[['Longitude', 'Latitude', 'Plant Name', 'City', 'State', 'solar_capacity_mw']].fillna(0).to_dict('records')
dc_points_json = df_clean[['Longitude', 'Latitude', 'Data Center Name', 'Provider', 'Address']].fillna('').to_dict('records')

total_data_centers = len(df)

# Convert the figure to HTML with full Plotly.js
base_html = fig.to_html(include_plotlyjs='cdn')

# Inject our custom filter UI and JavaScript into the HTML
filter_ui_and_script = f"""
    <div id="filter-container" style="position: fixed; bottom: 20px; left: 20px; background: white; padding: 10px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); z-index: 1000; min-width: 200px;">
        <h3 style="margin-top: 0; margin-bottom: 8px; color: #333; font-size: 14px;">🔍 Filter Power Plants</h3>
        
        <div style="margin-bottom: 8px;">
            <label style="display: block; margin-bottom: 3px; font-weight: bold; color: #555; font-size: 11px;">Minimum Capacity (MW):</label>
            <div style="display: flex; align-items: center; gap: 6px;">
                <input type="number" id="capacity-filter" value="10" min="0" step="10" style="flex: 1; padding: 4px; border: 1px solid #ddd; border-radius: 4px; font-size: 12px;">
                <button onclick="applyFilter()" style="padding: 4px 10px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 11px; font-weight: bold;">Apply</button>
            </div>
        </div>
        
        <div style="margin-bottom: 8px;">
            <label style="display: block; margin-bottom: 3px; font-weight: bold; color: #555; font-size: 11px;">Quick Presets:</label>
            <div style="display: flex; gap: 3px; flex-wrap: wrap;">
                <button onclick="setFilter(10)" style="padding: 3px 8px; background-color: #2196F3; color: white; border: none; border-radius: 3px; cursor: pointer; font-size: 10px;">10</button>
                <button onclick="setFilter(50)" style="padding: 3px 8px; background-color: #2196F3; color: white; border: none; border-radius: 3px; cursor: pointer; font-size: 10px;">50</button>
                <button onclick="setFilter(100)" style="padding: 3px 8px; background-color: #2196F3; color: white; border: none; border-radius: 3px; cursor: pointer; font-size: 10px;">100</button>
                <button onclick="setFilter(200)" style="padding: 3px 8px; background-color: #2196F3; color: white; border: none; border-radius: 3px; cursor: pointer; font-size: 10px;">200</button>
                <button onclick="setFilter(360)" style="padding: 3px 8px; background-color: #2196F3; color: white; border: none; border-radius: 3px; cursor: pointer; font-size: 10px;">360</button>
                <button onclick="setFilter(500)" style="padding: 3px 8px; background-color: #2196F3; color: white; border: none; border-radius: 3px; cursor: pointer; font-size: 10px;">500</button>
            </div>
        </div>
        
        <div style="margin-top: 6px; padding: 6px; background-color: #f0f0f0; border-radius: 4px; font-size: 11px; color: #333;">
            <strong>Current Filter:</strong> ≥ <span id="current-value">10</span> MW
        </div>
        
        <div style="margin-top: 6px; padding: 6px; background-color: #e8f5e9; border-radius: 4px; font-size: 10px; color: #2e7d32;">
            <strong>Visible Plants:</strong><br>
            <span style="display:inline-block; width:10px; height:10px; background-color:rgba(255, 0, 255, 0.9); border-radius:50%; margin-right:4px;"></span> Nuclear: <span id="nuc-count">0</span><br>
            <span style="display:inline-block; width:10px; height:10px; background-color:rgba(0, 191, 255, 0.9); border-radius:50%; margin-right:4px;"></span> Gas/LNG: <span id="gas-count">0</span><br>
            <span style="display:inline-block; width:10px; height:10px; background-color:rgba(255, 69, 0, 0.9); border-radius:50%; margin-right:4px;"></span> General: <span id="gen-count">0</span><br>
            <span style="display:inline-block; width:10px; height:10px; background-color:rgba(50, 205, 50, 0.9); border-radius:50%; margin-right:4px;"></span> Wind: <span id="wind-count">0</span><br>
            <span style="display:inline-block; width:10px; height:10px; background-color:rgba(255, 215, 0, 0.9); border-radius:50%; margin-right:4px;"></span> Solar: <span id="solar-count">0</span><br>
            <span style="display:inline-block; width:10px; height:10px; background-color:black; margin-right:4px;"></span> Data Centers: <span id="dc-count">0</span>
        </div>
    </div>
    
    <script>
        // Embedded power plant data
        const nucPlantsData = {json.dumps(nuc_plants_json)};
        const gasPlantsData = {json.dumps(gas_plants_json)};
        const genPlantsData = {json.dumps(gen_plants_json)};
        const windPlantsData = {json.dumps(wind_plants_json)};
        const solarPlantsData = {json.dumps(solar_plants_json)};
        const dcPointsData = {json.dumps(dc_points_json)};
        
        // Wait for the base map to load
        setTimeout(function() {{
            applyFilter();
        }}, 1000);
        
        function addPowerPlants(minCapacity) {{
            // Filter data
            // Note: DC CSV doesn't have capacity, so we show all of them or could enable separate toggle.
            // For now, we show all available valid points.
            const filteredNuc = nucPlantsData.filter(p => p.nuclear_capacity_mw >= minCapacity);
            const filteredGas = gasPlantsData.filter(p => p.gas_capacity_mw >= minCapacity);
            const filteredGen = genPlantsData.filter(p => p.other_capacity_mw >= minCapacity);
            const filteredWind = windPlantsData.filter(p => p.wind_capacity_mw >= minCapacity);
            const filteredSolar = solarPlantsData.filter(p => p.solar_capacity_mw >= minCapacity);
            const filteredDC = dcPointsData; // Show all DCs as they don't have MW data in this CSV
            
            // Update stats
            document.getElementById('nuc-count').textContent = filteredNuc.length;
            document.getElementById('gas-count').textContent = filteredGas.length;
            document.getElementById('gen-count').textContent = filteredGen.length;
            document.getElementById('wind-count').textContent = filteredWind.length;
            document.getElementById('solar-count').textContent = filteredSolar.length;
            document.getElementById('dc-count').textContent = filteredDC.length;
            
            // Create power plant traces
            const newTraces = [];
            
            // Nuclear Power Plants
            if (filteredNuc.length > 0) {{
                newTraces.push({{
                    type: 'scattergeo',
                    locationmode: 'USA-states',
                    lon: filteredNuc.map(p => p.Longitude),
                    lat: filteredNuc.map(p => p.Latitude),
                    text: filteredNuc.map(p => 
                        `${{p['Plant Name']}}<br>${{p.City}}, ${{p.State}}<br>${{p.nuclear_capacity_mw.toFixed(1)}} MW (Nuclear)`
                    ),
                    marker: {{
                        size: filteredNuc.map(p => p.nuclear_capacity_mw / 50),
                        color: 'rgba(255, 0, 255, 0.9)', // Vivid Magenta
                        line: {{
                            color: 'rgba(255, 255, 255, 0.8)',
                            width: 1
                        }},
                        sizemode: 'area',
                        sizemin: 6
                    }},
                    name: 'Nuclear',
                    hovertemplate: '<b>%{{text}}</b><extra></extra>'
                }});
            }}
            
            // Gas / LNG Power Plants
            if (filteredGas.length > 0) {{
                newTraces.push({{
                    type: 'scattergeo',
                    locationmode: 'USA-states',
                    lon: filteredGas.map(p => p.Longitude),
                    lat: filteredGas.map(p => p.Latitude),
                    text: filteredGas.map(p => 
                        `${{p['Plant Name']}}<br>${{p.City}}, ${{p.State}}<br>${{p.gas_capacity_mw.toFixed(1)}} MW (Nat. Gas)`
                    ),
                    marker: {{
                        size: filteredGas.map(p => p.gas_capacity_mw / 50),
                        color: 'rgba(0, 191, 255, 0.9)', // Deep Sky Blue
                        line: {{
                            color: 'rgba(255, 255, 255, 0.8)',
                            width: 0.5
                        }},
                        sizemode: 'area',
                        sizemin: 4
                    }},
                    name: 'Natural Gas / LNG',
                    hovertemplate: '<b>%{{text}}</b><extra></extra>'
                }});
            }}
            
            // General power plants (Others)
            if (filteredGen.length > 0) {{
                newTraces.push({{
                    type: 'scattergeo',
                    locationmode: 'USA-states',
                    lon: filteredGen.map(p => p.Longitude),
                    lat: filteredGen.map(p => p.Latitude),
                    text: filteredGen.map(p => 
                        `${{p['Plant Name']}}<br>${{p.City}}, ${{p.State}}<br>${{p.other_capacity_mw.toFixed(1)}} MW`
                    ),
                    marker: {{
                        size: filteredGen.map(p => p.other_capacity_mw / 50),
                        color: 'rgba(255, 69, 0, 0.9)', // Red-Orange (Vivid)
                        line: {{
                            color: 'rgba(255, 255, 255, 0.8)',
                            width: 0.5
                        }},
                        sizemode: 'area',
                        sizemin: 4
                    }},
                    name: 'Other (Coal, Hydro, etc.)',
                    hovertemplate: '<b>%{{text}}</b><extra></extra>'
                }});
            }}
            
            // Wind power plants
            if (filteredWind.length > 0) {{
                newTraces.push({{
                    type: 'scattergeo',
                    locationmode: 'USA-states',
                    lon: filteredWind.map(p => p.Longitude),
                    lat: filteredWind.map(p => p.Latitude),
                    text: filteredWind.map(p => 
                        `${{p['Plant Name']}}<br>${{p.City}}, ${{p.State}}<br>${{p.wind_capacity_mw.toFixed(1)}} MW (Wind)`
                    ),
                    marker: {{
                        size: filteredWind.map(p => p.wind_capacity_mw / 20),
                        color: 'rgba(50, 205, 50, 0.9)', // Lime Green
                        line: {{
                            color: 'rgba(255, 255, 255, 0.5)',
                            width: 0.5
                        }},
                        sizemode: 'area',
                        sizemin: 4
                    }},
                    name: 'Wind Power Plants',
                    hovertemplate: '<b>%{{text}}</b><extra></extra>'
                }});
            }}
            
            // Solar power plants
            if (filteredSolar.length > 0) {{
                newTraces.push({{
                    type: 'scattergeo',
                    locationmode: 'USA-states',
                    lon: filteredSolar.map(p => p.Longitude),
                    lat: filteredSolar.map(p => p.Latitude),
                    text: filteredSolar.map(p => 
                        `${{p['Plant Name']}}<br>${{p.City}}, ${{p.State}}<br>${{p.solar_capacity_mw.toFixed(1)}} MW (Solar)`
                    ),
                    marker: {{
                        size: filteredSolar.map(p => p.solar_capacity_mw / 20),
                        color: 'rgba(255, 215, 0, 0.9)', // Gold (Vivid)
                        line: {{
                            color: 'rgba(255, 255, 255, 0.5)',
                            width: 0.5
                        }},
                        sizemode: 'area',
                        sizemin: 4
                    }},
                    name: 'Solar Power Plants',
                    hovertemplate: '<b>%{{text}}</b><extra></extra>'
                }});
            }}

            // Data Centers (Black Squares)
            if (filteredDC.length > 0) {{
                newTraces.push({{
                    type: 'scattergeo',
                    locationmode: 'USA-states',
                    lon: filteredDC.map(p => p.Longitude),
                    lat: filteredDC.map(p => p.Latitude),
                    text: filteredDC.map(p => 
                        `<b>${{p['Data Center Name']}}</b><br>${{p.Provider}}<br>${{p.Address}}`
                    ),
                    marker: {{
                        size: 6,
                        symbol: 'square',
                        color: 'black',
                        line: {{
                            color: 'white',
                            width: 1
                        }}
                    }},
                    name: 'Individual Data Centers',
                    hovertemplate: '%{{text}}<extra></extra>'
                }});
            }}
            
            // Get the map element (Plotly creates a div with class 'plotly-graph-div')
            const mapDiv = document.querySelector('.plotly-graph-div');
            
            if (mapDiv && mapDiv.data) {{
                // Delete existing power plant traces (keep only the choropleth which is trace 0)
                const tracesToDelete = [];
                for (let i = 1; i < mapDiv.data.length; i++) {{
                    tracesToDelete.push(i);
                }}
                if (tracesToDelete.length > 0) {{
                    Plotly.deleteTraces(mapDiv, tracesToDelete);
                }}
                
                // Add new power plant traces
                if (newTraces.length > 0) {{
                    Plotly.addTraces(mapDiv, newTraces);
                }}
            }}
        }}
        
        function setFilter(value) {{
            document.getElementById('capacity-filter').value = value;
            applyFilter();
        }}
        
        function applyFilter() {{
            const minCapacity = parseFloat(document.getElementById('capacity-filter').value) || 0;
            document.getElementById('current-value').textContent = minCapacity;
            addPowerPlants(minCapacity);
        }}
        
        // Allow Enter key to apply filter
        document.getElementById('capacity-filter').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') {{
                applyFilter();
            }}
        }});
    </script>
</body>
"""

# Replace the closing </body> tag with our custom content
custom_html = base_html.replace('</body>', filter_ui_and_script)

# Write the custom HTML file
output_file = 'data_centers_map_interactive.html'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(custom_html)

print(f"\n✅ Interactive map saved as '{output_file}'")
print(f"Total Data Centers: {total_data_centers}")
print(f"\nPower Plants Loaded:")
print(f"  Nuclear: {len(nuclear_plants)}")
print(f"  Gas/LNG: {len(gas_plants)}")
print(f"  General (Other): {len(gen_plants)}")
print(f"  Wind: {len(wind_plants)}")
print(f"  Solar: {len(solar_plants)}")

print(f"\n📊 Open the HTML file to use the interactive filter!")
print(f"   Now includes Nuclear (Purple) and Gas/LNG (Blue) facilities!")

print(f"\nTop 10 States by Data Center Count:")
top_10 = state_summary.nlargest(10, 'Data Centers')
for idx, row in top_10.iterrows():
    print(f"  {row['State']}: {row['Data Centers']}")
