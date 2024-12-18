import osmnx as ox
from shapely.geometry import Polygon
from rtree import index
import json
import random

place_name = "Gjerdrum, Norway"
building_tags = {"building": True}
field_tags = {"landuse": "meadow", "natural": "grassland"}

gdf_buildings = ox.features_from_place(place_name, tags=building_tags)
gdf_buildings = gdf_buildings[gdf_buildings.geometry.apply(lambda x: isinstance(x, Polygon))]
gdf_buildings_wgs84 = gdf_buildings.to_crs(epsg=4326)

gdf_fields = ox.features_from_place(place_name, tags=field_tags)
gdf_fields = gdf_fields[gdf_fields.geometry.apply(lambda x: isinstance(x, Polygon))]
gdf_fields_wgs84 = gdf_fields.to_crs(epsg=4326)

gdf_buildings_projected = gdf_buildings_wgs84.to_crs(epsg=32633)
gdf_fields_projected = gdf_fields_wgs84.to_crs(epsg=32633)

buffered_fields = gdf_fields_projected.copy()
buffered_fields["geometry"] = gdf_fields_projected.geometry.buffer(10)  # Buffer by 10 meters

field_index = index.Index()
for idx, row in buffered_fields.iterrows():
    print(f"Processing field {idx}")
    if row.geometry.is_valid and not row.geometry.is_empty:  # Check for valid and non-empty geometries
        bounds = tuple(map(float, row.geometry.bounds))  # Convert all elements to native float
        if len(bounds) == 4:
            building_id = idx[1]
            field_index.insert(int(building_id), bounds)  # Ensure building_id is an integer
        else:
            print(f"Invalid bounds for geometry at index {idx}: {bounds}")
    else:
        print(f"Invalid or empty geometry at index {idx}")

print(buffered_fields)

near_field_buildings = []
for idx, building in gdf_buildings_projected.iterrows():
    possible_field_matches_idx = list(field_index.intersection(building.geometry.bounds))
    print(f"Possible field matches for building {idx}: {possible_field_matches_idx}")
    print(f"Building bounds: {building.geometry.bounds}")

    possible_fields = buffered_fields.iloc[possible_field_matches_idx]

    for _, field in possible_fields.iterrows():
        if building.geometry.intersects(field.geometry) or building.geometry.distance(field.geometry) <= 10:
            near_field_buildings.append({
                "building_id": idx,
                "building_centroid_lat": building.geometry.centroid.y,
                "building_centroid_lon": building.geometry.centroid.x,
                "field_bounds": field.geometry.bounds
            })
            break

geojson = {
    "type": "FeatureCollection",
    "features": []
}

for entry in near_field_buildings:
    feature = {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [entry["building_centroid_lon"], entry["building_centroid_lat"]]
        },
        "properties": {
            "id": entry["building_id"],
            "field_bounds": entry["field_bounds"]
        }
    }
    geojson["features"].append(feature)

with open("buildings_near_fields.json", "w") as f:
    json.dump(geojson, f)

print(f"Number of buildings near fields: {len(near_field_buildings)}")
