import osmnx as ox
from shapely.geometry import Polygon
from rtree import index
import geopandas as gpd
import json

# Define location and tags
place_name = "Gjerdrum, Norway"
tags = {"building": True}

# Load and filter building data
gdf_buildings = ox.features_from_place(place_name, tags=tags)
gdf_buildings = gdf_buildings[gdf_buildings.geometry.apply(lambda x: isinstance(x, Polygon))]
gdf_buildings_wgs84 = gdf_buildings.to_crs(epsg=4326)

# Reset index to ensure it is an integer
gdf_buildings_wgs84 = gdf_buildings_wgs84.reset_index(drop=True)

# Re-project geometries to a projected CRS (e.g., UTM)
gdf_buildings_projected = gdf_buildings_wgs84.to_crs(epsg=32633)  # Replace 32633 with the appropriate EPSG code for your area

# Buffer buildings slightly
buffered_buildings = gdf_buildings_projected.copy()
buffered_buildings['geometry'] = gdf_buildings_projected.geometry.buffer(0.5)  # Buffer by 0.5 meters

# Re-project back to WGS84 if needed
buffered_buildings = buffered_buildings.to_crs(epsg=4326)

# Create spatial index for efficient searching
spatial_index = index.Index()

# Insert geometries into the spatial index
for idx, row in buffered_buildings.iterrows():
    print(idx, row.geometry.bounds)
    spatial_index.insert(idx, row.geometry.bounds)

# Data storage
close_buildings = []
building_coordinates = []

# Vectorized pair checking
for idx, building1 in buffered_buildings.iterrows():
    possible_matches_idx = list(spatial_index.intersection(building1.geometry.bounds))
    possible_matches = buffered_buildings.iloc[possible_matches_idx]

    # Filter out self and check for intersections
    for idx2, building2 in possible_matches.iterrows():
        if idx != idx2 and building1.geometry.intersects(building2.geometry):
            # Avoid redundant computations
            centroid1 = building1.geometry.centroid
            bounds1 = building1.geometry.bounds
            centroid2 = building2.geometry.centroid
            bounds2 = building2.geometry.bounds

            building_coordinates.append({
                "building1_id": idx,
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

            close_buildings.append((idx, idx2))

# Convert the building coordinates to a JSON format suitable for Google Maps
geojson = {
    "type": "FeatureCollection",
    "features": []
}

for building in building_coordinates:
    feature1 = {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [building["building1_centroid_lon"], building["building1_centroid_lat"]]
        },
        "properties": {
            "id": building["building1_id"],
            "min_lat": building["building1_min_lat"],
            "min_lon": building["building1_min_lon"],
            "max_lat": building["building1_max_lat"],
            "max_lon": building["building1_max_lon"]
        }
    }
    feature2 = {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [building["building2_centroid_lon"], building["building2_centroid_lat"]]
        },
        "properties": {
            "id": building["building2_id"],
            "min_lat": building["building2_min_lat"],
            "min_lon": building["building2_min_lon"],
            "max_lat": building["building2_max_lat"],
            "max_lon": building["building2_max_lon"]
        }
    }
    geojson["features"].append(feature1)
    geojson["features"].append(feature2)

# Save the GeoJSON to a file
with open("close_building_coordinates.json", "w") as f:
    json.dump(geojson, f)

print(f"Number of pairs of buildings that are close: {len(close_buildings)}")
