import plotly.graph_objects as go
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time

print("Loading data files...")

# Load Data Center data
dc_df = pd.read_excel('data center.xlsx')
print(f"Loaded {len(dc_df)} data centers")

# Load Power Plant location data (EIA-860)
plant_df = pd.read_excel('eia8602024/2___Plant_Y2024.xlsx', header=1)
print(f"Loaded {len(plant_df)} power plants")

# Load Power Plant generator data (EIA-860)
# Using header=1 because the first row contains the form description
power_df = pd.read_excel('eia8602024/3_1_Generator_Y2024.xlsx', 
                         sheet_name='Operable', 
                         header=1)
print(f"Loaded {len(power_df)} power generators")

# Initialize geocoder
geolocator = Nominatim(user_agent="data_center_mapper")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

# Geocode Data Centers
print("\nGeocoding data centers...")
dc_locations = []

for idx, row in dc_df.iterrows():
    city = row['City']
    zip_code = row['Zip Code']
    company = row['Company']
    campus = row['Campus Name']
    capacity = row['Estimated Capacity']
    
    # Try to geocode using city and zip
    location = None
    try:
        location = geocode(f"{city}, {zip_code}, USA")
        if location:
            dc_locations.append({
                'company': company,
                'campus': campus,
                'city': city,
                'zip': zip_code,
                'capacity': capacity,
                'lat': location.latitude,
                'lon': location.longitude
            })
            print(f"  ✓ {company} - {campus} ({city})")
        else:
            print(f"  ✗ Could not geocode: {company} - {campus} ({city})")
    except Exception as e:
        print(f"  ✗ Error geocoding {company} - {campus}: {e}")

dc_geo_df = pd.DataFrame(dc_locations)
print(f"\nSuccessfully geocoded {len(dc_geo_df)} out of {len(dc_df)} data centers")

# Process Power Plant data
# Aggregate by state to get total capacity
print("\nProcessing power plant data...")

# Clean and convert capacity to numeric
power_df['Nameplate Capacity (MW)'] = pd.to_numeric(power_df['Nameplate Capacity (MW)'], errors='coerce')

# Group by state and sum capacity
state_capacity = power_df.groupby('State')['Nameplate Capacity (MW)'].sum().reset_index()
state_capacity.columns = ['state', 'total_capacity_mw']

print(f"Aggregated power data for {len(state_capacity)} states")
print(f"Total US power capacity: {state_capacity['total_capacity_mw'].sum():.0f} MW")

# Process individual power plant locations
print("\nProcessing individual power plant locations...")

# Clean plant location data
plant_df['Latitude'] = pd.to_numeric(plant_df['Latitude'], errors='coerce')
plant_df['Longitude'] = pd.to_numeric(plant_df['Longitude'], errors='coerce')

# Remove plants without valid coordinates
plant_locations = plant_df[['Plant Code', 'Plant Name', 'State', 'City', 'Latitude', 'Longitude']].copy()
plant_locations = plant_locations.dropna(subset=['Latitude', 'Longitude'])

# Merge with generator data to get total capacity per plant
plant_capacity = power_df.groupby('Plant Code')['Nameplate Capacity (MW)'].sum().reset_index()
plant_capacity.columns = ['Plant Code', 'total_capacity_mw']

plant_locations = plant_locations.merge(plant_capacity, on='Plant Code', how='left')
plant_locations['total_capacity_mw'] = plant_locations['total_capacity_mw'].fillna(0)

# Filter to only show plants with significant capacity (>10 MW) to avoid clutter
plant_locations = plant_locations[plant_locations['total_capacity_mw'] > 10]

print(f"Found {len(plant_locations)} power plants with coordinates (>10 MW capacity)")

# State center coordinates (approximate)
state_coords = {
    'AK': (64.2008, -149.4937), 'AL': (32.3182, -86.9023), 'AR': (34.7465, -92.2896),
    'AZ': (34.0489, -111.0937), 'CA': (36.7783, -119.4179), 'CO': (39.5501, -105.7821),
    'CT': (41.6032, -73.0877), 'DE': (38.9108, -75.5277), 'FL': (27.6648, -81.5158),
    'GA': (32.1656, -82.9001), 'HI': (19.8968, -155.5828), 'IA': (41.8780, -93.0977),
    'ID': (44.0682, -114.7420), 'IL': (40.6331, -89.3985), 'IN': (40.2672, -86.1349),
    'KS': (39.0119, -98.4842), 'KY': (37.8393, -84.2700), 'LA': (30.9843, -91.9623),
    'MA': (42.4072, -71.3824), 'MD': (39.0458, -76.6413), 'ME': (45.2538, -69.4455),
    'MI': (44.3148, -85.6024), 'MN': (46.7296, -94.6859), 'MO': (37.9643, -91.8318),
    'MS': (32.3547, -89.3985), 'MT': (46.8797, -110.3626), 'NC': (35.7596, -79.0193),
    'ND': (47.5515, -101.0020), 'NE': (41.4925, -99.9018), 'NH': (43.1939, -71.5724),
    'NJ': (40.0583, -74.4057), 'NM': (34.5199, -105.8701), 'NV': (38.8026, -116.4194),
    'NY': (43.2994, -74.2179), 'OH': (40.4173, -82.9071), 'OK': (35.4676, -97.5164),
    'OR': (43.8041, -120.5542), 'PA': (41.2033, -77.1945), 'RI': (41.5801, -71.4774),
    'SC': (33.8361, -81.1637), 'SD': (43.9695, -99.9018), 'TN': (35.5175, -86.5804),
    'TX': (31.9686, -99.9018), 'UT': (39.3210, -111.0937), 'VA': (37.4316, -78.6569),
    'VT': (44.5588, -72.5778), 'WA': (47.7511, -120.7401), 'WI': (43.7844, -88.7879),
    'WV': (38.5976, -80.4549), 'WY': (43.0760, -107.2903)
}

# Add coordinates to state capacity data
state_capacity['lat'] = state_capacity['state'].map(lambda x: state_coords.get(x, (None, None))[0])
state_capacity['lon'] = state_capacity['state'].map(lambda x: state_coords.get(x, (None, None))[1])
state_capacity = state_capacity.dropna(subset=['lat', 'lon'])

# Create the map
print("\nCreating map visualization...")
fig = go.Figure()

# Plot Power Plants by State (as circles sized by capacity)
fig.add_trace(go.Scattergeo(
    locationmode='USA-states',
    lon=state_capacity['lon'],
    lat=state_capacity['lat'],
    text=state_capacity['state'] + '<br>' + 
         state_capacity['total_capacity_mw'].round(0).astype(str) + ' MW',
    marker=dict(
        size=state_capacity['total_capacity_mw'] / 500,  # Scale factor
        color='lightblue',
        line_color='darkblue',
        line_width=1,
        sizemode='area',
        opacity=0.6
    ),
    name='Power Generation by State',
    hovertemplate='<b>%{text}</b><extra></extra>'
))

# Plot Individual Power Plants
fig.add_trace(go.Scattergeo(
    locationmode='USA-states',
    lon=plant_locations['Longitude'],
    lat=plant_locations['Latitude'],
    text=plant_locations['Plant Name'] + '<br>' +
         plant_locations['City'] + ', ' + plant_locations['State'] + '<br>' +
         plant_locations['total_capacity_mw'].round(1).astype(str) + ' MW',
    marker=dict(
        size=plant_locations['total_capacity_mw'] / 100,  # Scale factor
        color='green',
        line_color='darkgreen',
        line_width=0.5,
        sizemode='area',
        opacity=0.5
    ),
    name='Individual Power Plants',
    hovertemplate='<b>%{text}</b><extra></extra>'
))

# Plot Data Centers
if len(dc_geo_df) > 0:
    # Extract capacity numbers from strings like "1,400 MW+"
    dc_geo_df['capacity_num'] = dc_geo_df['capacity'].str.extract(r'([\d,]+)')[0].str.replace(',', '').astype(float)
    
    fig.add_trace(go.Scattergeo(
        locationmode='USA-states',
        lon=dc_geo_df['lon'],
        lat=dc_geo_df['lat'],
        text=dc_geo_df['company'] + '<br>' + 
             dc_geo_df['campus'] + '<br>' +
             dc_geo_df['city'] + '<br>' +
             dc_geo_df['capacity'],
        marker=dict(
            size=dc_geo_df['capacity_num'] / 50,  # Scale by capacity
            color='red',
            symbol='diamond',
            line_color='darkred',
            line_width=1,
            opacity=0.8
        ),
        name='Data Centers',
        hovertemplate='<b>%{text}</b><extra></extra>'
    ))

fig.update_layout(
    title={
        'text': 'US Data Centers & Power Plants (Individual Locations + State Totals)',
        'x': 0.5,
        'xanchor': 'center'
    },
    geo=dict(
        scope='usa',
        projection_type='albers usa',
        showland=True,
        landcolor='rgb(243, 243, 243)',
        coastlinecolor='rgb(204, 204, 204)',
        showlakes=True,
        lakecolor='rgb(255, 255, 255)',
    ),
    height=700,
    showlegend=True
)

print("\nOpening map in browser...")
fig.show()

# Save to HTML file
output_file = 'us_data_centers_power_map.html'
fig.write_html(output_file)
print(f"\nMap saved to: {output_file}")