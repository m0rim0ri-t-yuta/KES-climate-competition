import pandas as pd
import pgeocode
import re
import numpy as np
import os
from geopy.geocoders import ArcGIS
from geopy.extra.rate_limiter import RateLimiter
import time
import signal
import sys

print("=== Comprehensive Geocoder (Zip + Grouped City Lookup) ===")
input_file = 'datacenters_final_structure(Sheet1).csv'
output_file = 'datacenters_with_coords.csv' 

# 1. Load Data
try:
    df = pd.read_csv(input_file, encoding='utf-8')
except UnicodeDecodeError:
    df = pd.read_csv(input_file, encoding='latin-1')
print(f"Loaded {len(df)} total entries.")

# Initialize Columns if not present
if 'Latitude' not in df.columns: df['Latitude'] = np.nan
if 'Longitude' not in df.columns: df['Longitude'] = np.nan

# 2. Extract Zip Codes (Phase 1: Fast)
def extract_zip(address):
    if pd.isna(address): return None
    matches = re.findall(r'\b\d{5}\b', str(address))
    if matches: return matches[-1]
    return None

print("Phase 1: Zip Code Lookup...")
df['Zip'] = df['Address'].apply(extract_zip)
valid_zips = df['Zip'].dropna().unique()

nomi = pgeocode.Nominatim('us')
if len(valid_zips) > 0:
    zip_res = nomi.query_postal_code(valid_zips)
    zip_map = zip_res.set_index('postal_code')[['latitude', 'longitude']].to_dict('index')
    
    # Apply Zip Coordinates
    for idx, row in df.iterrows():
        # Only if empty
        if pd.isna(row['Latitude']) and row['Zip'] in zip_map:
            lat = zip_map[row['Zip']]['latitude']
            lon = zip_map[row['Zip']]['longitude']
            if not np.isnan(lat):
                df.at[idx, 'Latitude'] = lat
                df.at[idx, 'Longitude'] = lon

done_count = df['Latitude'].notna().sum()
print(f"  -> Phase 1 Complete. Resolved: {done_count}/{len(df)}")

# Helper to save progress
def save_progress():
    final_df = df.dropna(subset=['Latitude', 'Longitude'])
    final_df.to_csv(output_file, index=False)
    # print(f"  (Saved progress: {len(final_df)} records)")

# Handle Interrupts
def signal_handler(sig, frame):
    print("\nInterrupted! Saving current progress...")
    save_progress()
    print("Saved. Exiting.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# 3. Grouped Address Lookup (Phase 2: Fallback using ArcGIS)
# Identify remaining items
df_missing = df[df['Latitude'].isna()].copy()
unique_addresses = df_missing['Address'].dropna().unique()

print(f"\nPhase 2: Grouped Address Lookup (Using ArcGIS for speed)")
print(f"  Remaining items: {len(df_missing)}")
print(f"  Unique locations to search: {len(unique_addresses)}")

if len(unique_addresses) > 0:
    print("  Starting Geocoding for unique locations...")
    
    geolocator = ArcGIS(user_agent="dc_geocoder_grouped_v3")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=0.1)
    
    addr_map = {}
    
    for i, addr in enumerate(unique_addresses):
        try:
            query = addr
            if "USA" not in str(query) and "United States" not in str(query):
                query = f"{query}, USA"
            
            # Print progress every 5 items
            if i % 5 == 0:
                print(f"  [{i+1}/{len(unique_addresses)}] {str(query)[:40]}...             ", end="\r")
            
            loc = geocode(query)
            if loc:
                addr_map[addr] = (loc.latitude, loc.longitude)
                
                # Apply immediately to main DF to ensure up-to-date state for saving
                # Note: This is slow to iterate whole DF every time.
                # Optimized: Just update the specific rows LATER?
                # No, for 'save_progress' to work, 'df' needs to be updated.
                # Iterating 2000 rows is instant in memory.
                
                # Update all matching rows
                # Using boolean indexing is faster
                # df.loc[df['Address'] == addr, 'Latitude'] = loc.latitude
                # df.loc[df['Address'] == addr, 'Longitude'] = loc.longitude
                # But 'Address' un-indexed search might be slightly slow if done 1000 times? 
                # 2000 rows is tiny. It's fine.
                mask = df['Address'] == addr
                df.loc[mask, 'Latitude'] = loc.latitude
                df.loc[mask, 'Longitude'] = loc.longitude
            
            if i % 20 == 0 and i > 0:
                save_progress()
                
        except Exception as e:
             pass 
    
    print("\n  Phase 2 Complete.")

# 4. Save Final
save_progress()
final_df = df.dropna(subset=['Latitude', 'Longitude'])
print("-" * 50)
print(f"Total Geocoded: {len(final_df)} / {len(df)} ({len(final_df)/len(df)*100:.1f}%)")
print(f"Saved to {output_file}")
