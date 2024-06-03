# OBTAINING LONDON BOROUGH DATA/DETERMINING A LOCATION'S BOROUGH
import geopandas as gpd
from shapely.geometry import Point
import os


def get_boroughs_data():
    # Load GeoJSON file with borough boundaries
    current_dir = os.path.dirname(os.path.abspath(__file__))
    relative_path = os.path.join(
        current_dir, "..", "..", "static", "geojson", "london_boroughs.geojson"
    )
    return gpd.read_file(relative_path)


def find_borough(lat, lng, boroughs_data):
    # Create a Point object for the cafe
    cafe_location = Point(lng, lat)

    # Find the borough containing the cafe
    for _, borough in boroughs_data.iterrows():
        if cafe_location.within(borough["geometry"]):
            return borough["name"]
    else:
        return "N/A"


# # --------------------EXAMPLE--------------------------------
# boroughs_data = get_boroughs_data()

# locations = [
#     {"name": "East London Mosque", "latitude": 51.5160, "longitude": -0.0632},
#     {"name": "Hyde Park", "latitude": 51.5074, "longitude": -0.1657},
#     {"name": "Surrey Quays", "latitude": 51.4943, "longitude": -0.0478},
#     {"name": "Big Ben", "latitude": 51.5007, "longitude": -0.1246},
# ]

# for location in locations:
#     print(find_borough(location["latitude"], location["longitude"], boroughs_data))
