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

# Read the data center CSV file
df = pd.read_csv('data_centers.csv')
df['State_Code'] = df['State'].map(state_abbrev)

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

# Process Generator data (non-renewable)
gen_df['Nameplate Capacity (MW)'] = pd.to_numeric(gen_df['Nameplate Capacity (MW)'], errors='coerce')
gen_capacity = gen_df.groupby('Plant Code')['Nameplate Capacity (MW)'].sum().reset_index()
gen_capacity.columns = ['Plant Code', 'total_capacity_mw']

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
plant_locations = plant_locations.merge(gen_capacity, on='Plant Code', how='left')
plant_locations = plant_locations.merge(wind_capacity, on='Plant Code', how='left')
plant_locations = plant_locations.merge(solar_capacity, on='Plant Code', how='left')

# Fill NaN values with 0
plant_locations['total_capacity_mw'] = plant_locations['total_capacity_mw'].fillna(0)
plant_locations['wind_capacity_mw'] = plant_locations['wind_capacity_mw'].fillna(0)
plant_locations['solar_capacity_mw'] = plant_locations['solar_capacity_mw'].fillna(0)

# Separate into different categories
gen_plants = plant_locations[(plant_locations['total_capacity_mw'] > 0) & 
                              (plant_locations['wind_capacity_mw'] == 0) & 
                              (plant_locations['solar_capacity_mw'] == 0)].copy()

wind_plants = plant_locations[plant_locations['wind_capacity_mw'] > 0].copy()
solar_plants = plant_locations[plant_locations['solar_capacity_mw'] > 0].copy()

print(f"Found {len(gen_plants)} general power plants")
print(f"Found {len(wind_plants)} wind power plants")
print(f"Found {len(solar_plants)} solar power plants")

print("\nCreating base choropleth map with px.choropleth...")

# Create the base choropleth map using plotly.express (like the reference code)
fig = px.choropleth(
    df,
    locations='State_Code',
    locationmode='USA-states',
    color='Data Centers',
    scope='usa',
    color_continuous_scale='Viridis',
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
gen_plants_json = gen_plants[['Longitude', 'Latitude', 'Plant Name', 'City', 'State', 'total_capacity_mw']].to_dict('records')
wind_plants_json = wind_plants[['Longitude', 'Latitude', 'Plant Name', 'City', 'State', 'wind_capacity_mw']].to_dict('records')
solar_plants_json = solar_plants[['Longitude', 'Latitude', 'Plant Name', 'City', 'State', 'solar_capacity_mw']].to_dict('records')

total_data_centers = df['Data Centers'].sum()

# Convert the figure to HTML with full Plotly.js
base_html = fig.to_html(include_plotlyjs='cdn')

# Inject our custom filter UI and JavaScript into the HTML
# Find the closing </body> tag and insert our code before it
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
            General: <span id="gen-count">0</span><br>
            Wind: <span id="wind-count">0</span><br>
            Solar: <span id="solar-count">0</span>
        </div>
    </div>
    
    <script>
        // Embedded power plant data
        const genPlantsData = {json.dumps(gen_plants_json)};
        const windPlantsData = {json.dumps(wind_plants_json)};
        const solarPlantsData = {json.dumps(solar_plants_json)};
        
        // Wait for the base map to load
        setTimeout(function() {{
            applyFilter();
        }}, 1000);
        
        function addPowerPlants(minCapacity) {{
            // Filter data
            const filteredGen = genPlantsData.filter(p => p.total_capacity_mw >= minCapacity);
            const filteredWind = windPlantsData.filter(p => p.wind_capacity_mw >= minCapacity);
            const filteredSolar = solarPlantsData.filter(p => p.solar_capacity_mw >= minCapacity);
            
            // Update stats
            document.getElementById('gen-count').textContent = filteredGen.length;
            document.getElementById('wind-count').textContent = filteredWind.length;
            document.getElementById('solar-count').textContent = filteredSolar.length;
            
            // Create power plant traces
            const newTraces = [];
            
            // General power plants
            if (filteredGen.length > 0) {{
                newTraces.push({{
                    type: 'scattergeo',
                    locationmode: 'USA-states',
                    lon: filteredGen.map(p => p.Longitude),
                    lat: filteredGen.map(p => p.Latitude),
                    text: filteredGen.map(p => 
                        `${{p['Plant Name']}}<br>${{p.City}}, ${{p.State}}<br>${{p.total_capacity_mw.toFixed(1)}} MW`
                    ),
                    marker: {{
                        size: filteredGen.map(p => p.total_capacity_mw / 50),
                        color: 'rgba(220, 20, 60, 0.6)',
                        line: {{
                            color: 'rgba(139, 0, 0, 0.8)',
                            width: 0.5
                        }},
                        sizemode: 'area',
                        sizemin: 3
                    }},
                    name: 'General Power Plants',
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
                        color: 'rgba(34, 139, 34, 0.7)',
                        line: {{
                            color: 'rgba(0, 100, 0, 0.9)',
                            width: 0.5
                        }},
                        sizemode: 'area',
                        sizemin: 3
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
                        color: 'rgba(255, 165, 0, 0.7)',
                        line: {{
                            color: 'rgba(255, 140, 0, 0.9)',
                            width: 0.5
                        }},
                        sizemode: 'area',
                        sizemin: 3
                    }},
                    name: 'Solar Power Plants',
                    hovertemplate: '<b>%{{text}}</b><extra></extra>'
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
print(f"  General: {len(gen_plants)}")
print(f"  Wind: {len(wind_plants)}")
print(f"  Solar: {len(solar_plants)}")
print(f"\n📊 Open the HTML file to use the interactive filter!")
print(f"   The data center choropleth is created with px.choropleth (like the reference code)")
print(f"   Power plant markers are added dynamically with JavaScript filtering")
print(f"\nTop 10 States by Data Center Count:")
top_10 = df.nlargest(10, 'Data Centers')
for idx, row in top_10.iterrows():
    print(f"  {row['State']}: {row['Data Centers']}")
