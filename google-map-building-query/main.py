from shapely.geometry import Polygon
import osmnx as ox
from rtree import index
import matplotlib.pyplot as plt
import pandas as pd  # Ensure pandas is imported

# Define location and tags
place_name = "Gjerdrum, Norway"
tags = {"building": True}

# Load building data
gdf_buildings = ox.features_from_place(place_name, tags=tags)

# Filter out non-polygon geometries
gdf_buildings = gdf_buildings[gdf_buildings.geometry.apply(lambda x: isinstance(x, Polygon))]

# Reproject the data to a projected CRS (UTM in meters, using EPSG:32633 as an example)
gdf_buildings = gdf_buildings.to_crs(epsg=32633)

# Buffer the polygons slightly to create a 'proximity' zone
buffered_buildings = gdf_buildings.copy()
buffered_buildings['geometry'] = gdf_buildings.geometry.buffer(0.5)  # Buffer by 0.5 meters (adjust as needed)

# Create a spatial index for the buffered buildings
spatial_index = index.Index()

# Function to get or generate a unique ID
def get_building_id(row, fallback_id):
    if 'ref:bygningsnr' in row and pd.notna(row['ref:bygningsnr']):
        return int(row['ref:bygningsnr'])
    return fallback_id  # Use a sequential or unique fallback ID

# Create a mapping of building_id to DataFrame index
id_to_index = {}

# Add geometries to the spatial index and populate the mapping
for idx, geometry in buffered_buildings.iterrows():
    bounds = tuple(map(float, geometry['geometry'].bounds))  # Convert bounds to float
    fallback_id = idx if isinstance(idx, int) else hash(idx)  # Ensure the fallback ID is an integer
    building_id = get_building_id(geometry, fallback_id)

    # Map the building_id to the original DataFrame index
    id_to_index[building_id] = idx
    spatial_index.insert(building_id, bounds)

# Check if any buildings are within a certain distance
close_buildings = []
length = 0

for idx1, building1 in buffered_buildings.iterrows():
    building1_id = get_building_id(building1, hash(idx1))  # Use the same ID logic for querying
    possible_matches = list(spatial_index.intersection(building1['geometry'].bounds))

    for building2_id in possible_matches:
        if building1_id != building2_id:
            # Retrieve the DataFrame index for building2 using the mapping
            idx2 = id_to_index.get(building2_id)
            if idx2 is None:
                continue  # Skip if mapping is invalid

            building2 = buffered_buildings.loc[idx2]  # Access row by original index
            if building1['geometry'].intersects(building2['geometry']):
                print(f"   - Buildings {idx1} and {idx2} are close.")
                close_buildings.append((idx1, idx2))  # Append valid DataFrame indices

                print("Building 1: ", building1["geometry"].bounds)

                length += 1
                if length > 10:
                    break
    if length > 10:
        break

print(f"Number of pairs of buildings that are close: {len(close_buildings)}")

# Output the results
if close_buildings:
    print("Found the following pairs of buildings that are close:")
    for pair in close_buildings:
        print(f"Building {pair[0]} and Building {pair[1]} are close.")
else:
    print("No buildings are close to each other based on the specified buffer.")

# Visualize the buildings and highlights on the map
fig, ax = plt.subplots(figsize=(10, 10))
gdf_buildings.plot(ax=ax, color='lightblue', edgecolor='black')
for pair in close_buildings:
    building1 = gdf_buildings.loc[pair[0]]  # Use .loc with valid indices
    building2 = gdf_buildings.loc[pair[1]]

    # Draw lines or highlight close buildings
    ax.plot([building1.geometry.centroid.x, building2.geometry.centroid.x],
            [building1.geometry.centroid.y, building2.geometry.centroid.y],
            color='red', linewidth=2)


plt.show()
