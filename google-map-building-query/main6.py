import osmnx as ox
import cv2
import numpy as np
from ultralytics import YOLO
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import box
import pandas as pd


def get_osm_terrain_data(place_name, elevation_threshold=500):
    """
    Fetch OSM data for the specified area and filter mountainous regions.
    :param place_name: Name of the area to search (e.g., "Alps, Austria").
    :param elevation_threshold: Elevation threshold for mountainous regions (in meters).
    :return: GeoDataFrame containing mountainous areas.
    """
    print(f"Fetching terrain data for {place_name}...")
    # Fetch OSM data
    gdf = ox.features_from_place(place_name, tags={"natural": "peak"})

    # Filter by elevation if available
    if "ele" in gdf.columns:
        gdf["ele"] = pd.to_numeric(gdf["ele"], errors="coerce")
        mountains = gdf[gdf["ele"] > elevation_threshold]
    else:
        mountains = gdf

    print(f"Found {len(mountains)} peaks above {elevation_threshold}m.")
    return mountains


def fetch_and_save_image(place_name, save_path="terrain_image.jpg"):
    """
    Plot and save a map of the place boundary using OSM data.
    :param place_name: Name of the location.
    :param save_path: Path to save the map image.
    """
    print(f"Generating map for {place_name}...")

    # Fetch the place boundary
    gdf = ox.geocode_to_gdf(place_name)

    # Plot the boundary
    fig, ax = plt.subplots(figsize=(8, 8))
    gdf.boundary.plot(ax=ax, edgecolor="black")
    ax.set_title(f"Boundary of {place_name}")
    ax.set_axis_off()

    # Save the image
    fig.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"Map saved to {save_path}.")
    return save_path


def detect_people(image_path, model_path="yolov8n.pt"):
    """
    Detect people in the given image using a YOLO model.
    :param image_path: Path to the input image.
    :param model_path: Path to the YOLO model weights.
    :return: YOLO detection results.
    """
    print(f"Detecting people in {image_path}...")
    # Load the YOLO model
    model = YOLO(model_path)
    # Perform detection
    results = model(image_path)
    return results[0]


def overlay_results(image_path, results, output_path="output_image.jpg"):
    """
    Overlay bounding boxes on the image for detected people.
    :param image_path: Path to the input image.
    :param results: YOLO detection results.
    :param output_path: Path to save the output image.
    """
    image = cv2.imread(image_path)
    for box in results.boxes:
        x1, y1, x2, y2 = box.xyxy[0]
        conf = box.conf[0]
        cls = box.cls[0]
        if int(cls) == 0:  # Class 0 is 'person' in the YOLO model
            cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.putText(image, f"Person {conf:.2f}", (int(x1), int(y1) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    cv2.imwrite(output_path, image)
    print(f"Results saved to {output_path}.")
    return output_path


def main():
    # Define place and parameters
    place_name = "Alps, Austria"
    elevation_threshold = 1500  # Elevation in meters

    # Step 1: Fetch OSM terrain data
    mountains = get_osm_terrain_data(place_name, elevation_threshold)

    # Step 2: Generate and save a map of the region
    image_path = fetch_and_save_image(place_name)

    # Step 3: Perform object detection
    detection_results = detect_people(image_path)

    # Step 4: Overlay results and save output
    output_path = overlay_results(image_path, detection_results)

    # Display results
    output_image = cv2.imread(output_path)
    plt.figure(figsize=(12, 8))
    plt.title("Detected People in Mountainous Area")
    plt.imshow(cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB))
    plt.axis("off")
    plt.show()


if __name__ == "__main__":
    main()
