from shapely.geometry import Polygon
import osmnx as ox
import pandas as pd
import webbrowser
from rtree import index

# Define location and tags
place_name = "Gjerdrum, Norway"
tags = {"building": True}

gdf_buildings = ox.features_from_place(place_name, tags=tags)
gdf_buildings = gdf_buildings[gdf_buildings.geometry.apply(lambda x: isinstance(x, Polygon))]
gdf_buildings_wgs84 = gdf_buildings.to_crs(epsg=4326)

buffered_buildings = gdf_buildings_wgs84.copy()
buffered_buildings['geometry'] = gdf_buildings_wgs84.geometry.buffer(0.5)  # Buffer by 0.5 meters (adjust as needed)

spatial_index = index.Index()

def get_building_id(row, fallback_id):
    if 'ref:bygningsnr' in row and pd.notna(row['ref:bygningsnr']):
        return int(row['ref:bygningsnr'])
    return fallback_id  # Use a sequential or unique fallback ID

id_to_index = {}

for idx, geometry in buffered_buildings.iterrows():
    bounds = tuple(map(float, geometry['geometry'].bounds))  # Convert bounds to float
    fallback_id = idx if isinstance(idx, int) else hash(idx)  # Ensure the fallback ID is an integer
    building_id = get_building_id(geometry, fallback_id)

    id_to_index[building_id] = idx
    spatial_index.insert(building_id, bounds)

close_buildings = []
building_coordinates = []

length = 0
for idx1, building1 in buffered_buildings.iterrows():
    building1_id = get_building_id(building1, hash(idx1))  # Use the same ID logic for querying
    possible_matches = list(spatial_index.intersection(building1['geometry'].bounds))

    for building2_id in possible_matches:
        if building1_id != building2_id:
            idx2 = id_to_index.get(building2_id)
            if idx2 is None:
                continue  # Skip if mapping is invalid

            building2 = buffered_buildings.loc[idx2]  # Access row by original index
            if building1['geometry'].intersects(building2['geometry']):
                close_buildings.append((idx1, idx2))  # Append valid DataFrame indices

                centroid1 = building1.geometry.centroid
                bounds1 = building1.geometry.bounds  # (minx, miny, maxx, maxy)
                centroid2 = building2.geometry.centroid
                bounds2 = building2.geometry.bounds  # (minx, miny, maxx, maxy)

                building_coordinates.append({
                    "building1_id": idx1,
                    "building1_centroid_lat": centroid1.y,
                    "building1_centroid_lon": centroid1.x,
                    "building1_min_lat": bounds1[1],
                    "building1_min_lon": bounds1[0],
                    "building1_max_lat": bounds1[3],
                    "building1_max_lon": bounds1[2],
                    "building2_id": idx2,
                    "building2_centroid_lat": centroid2.y,
                    "building2_centroid_lon": centroid2.x,
                    "building2_min_lat": bounds2[1],
                    "building2_min_lon": bounds2[0],
                    "building2_max_lat": bounds2[3],
                    "building2_max_lon": bounds2[2],
                })

                length += 1
                if length > 10:
                    break
    if length > 10:
        break

if close_buildings:
    print("Found the following pairs of buildings that are close:")
    for pair in close_buildings:
        print(f"Building {pair[0]} and Building {pair[1]} are close.")
else:
    print("No buildings are close to each other based on the specified buffer.")

building_coordinates_df = pd.DataFrame(building_coordinates)

building_coordinates_df.to_csv("close_building_coordinates.csv", index=False)

for idx, row in building_coordinates_df.iterrows():
    webbrowser.open(f"https://www.google.com/maps/@{row['building1_centroid_lat']},{row['building1_centroid_lon']},21z?entry=ttu&g_ep=EgoyMDI0MTIxMS4wIKXMDSoASAFQAw%3D%3D")
    webbrowser.open(f"https://www.google.com/maps/@{row['building2_centroid_lat']},{row['building2_centroid_lon']},21z?entry=ttu&g_ep=EgoyMDI0MTIxMS4wIKXMDSoASAFQAw%3D%3D")
