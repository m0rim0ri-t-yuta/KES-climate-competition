import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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

# Read the CSV file
df = pd.read_csv('data_centers.csv')

# Add state abbreviation column
df['State_Code'] = df['State'].map(state_abbrev)

# Create a choropleth map
fig = px.choropleth(
    df,
    locations='State_Code',
    locationmode='USA-states',
    color='Data Centers',
    scope='usa',
    color_continuous_scale='Viridis',
    labels={'Data Centers': 'Number of Data Centers'},
    title='Data Centers Distribution Across US States',
    hover_name='State',
    hover_data={'Data Centers': True, 'State_Code': False}
)

# Update layout for better visualization
fig.update_layout(
    title_font_size=24,
    title_x=0.5,
    geo=dict(
        showlakes=True,
        lakecolor='rgb(255, 255, 255)'
    ),
    height=700,
    width=1200
)

# Add annotation for total
total_data_centers = df['Data Centers'].sum()
fig.add_annotation(
    text=f'Total Data Centers: {total_data_centers}',
    xref='paper',
    yref='paper',
    x=0.5,
    y=-0.05,
    showarrow=False,
    font=dict(size=16, color='black')
)

# Save the map as an HTML file
fig.write_html('data_centers_map.html')
print(f"Map saved as 'data_centers_map.html'")
print(f"Total Data Centers: {total_data_centers}")

# Display top 10 states
print("\nTop 10 States by Data Center Count:")
top_10 = df.nlargest(10, 'Data Centers')
for idx, row in top_10.iterrows():
    print(f"{row['State']}: {row['Data Centers']}")

# Show the map in browser
fig.show()
