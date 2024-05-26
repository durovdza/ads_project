import asyncio
import aiohttp
import folium
import numpy as np
import pandas as pd
from geopy.geocoders import Nominatim
from sklearn.neighbors import KNeighborsClassifier
from folium.plugins import MarkerCluster
from PIL import Image
from io import BytesIO
import torch
import logging
from typing import Tuple, Optional, List
import os

# Logger einrichten
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Konfiguration auslagern
MAPBOX_ACCESS_TOKEN = os.path.join("config", "config_mysql_credentials.json")
USER_AGENT = "parking_locator"

# Funktion, um Daten von der Overpass API zu holen
async def fetch_osm_data(query: str) -> Optional[dict]:
    """Fetch data from the Overpass API based on the provided query."""
    overpass_url = "http://overpass-api.de/api/interpreter"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(overpass_url, params={'data': query}) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logging.error(f"Error fetching OSM data: {e}")
            return None

# Query für Parkplätze in Zürich
overpass_query = """
[out:json];
area[name="Zürich"]->.searchArea;
(
  node["amenity"="parking"](area.searchArea);
  way["amenity"="parking"](area.searchArea);
  relation["amenity"="parking"](area.searchArea);
);
out center;
"""

# Daten abrufen
osm_data = asyncio.run(fetch_osm_data(overpass_query))
if osm_data is None:
    raise SystemExit("Fehler beim Abrufen der OSM-Daten.")

# Extrahieren der Koordinaten
def extract_coordinates(osm_data: dict) -> List[Tuple[float, float]]:
    """Extract coordinates of parking locations from OSM data."""
    parking_locations = []
    for element in osm_data['elements']:
        if 'center' in element:
            lat = element['center']['lat']
            lon = element['center']['lon']
        elif 'lat' in element and 'lon' in element:
            lat = element['lat']
            lon = element['lon']
        else:
            continue
        parking_locations.append((lat, lon))
    return parking_locations

parking_locations = extract_coordinates(osm_data)

# In DataFrame umwandeln
parking_df = pd.DataFrame(parking_locations, columns=['latitude', 'longitude'])

# Funktion, um Satellitenbilder von Koordinaten zu erhalten (Mapbox)
async def fetch_satellite_image(lat: float, lon: float, zoom: int = 18, size: Tuple[int, int] = (256, 256), maptype: str = 'satellite') -> Optional[Image.Image]:
    """Fetch a satellite image from Mapbox for the given coordinates."""
    url = f"https://api.mapbox.com/styles/v1/mapbox/{maptype}-v9/static/{lon},{lat},{zoom}/{size[0]}x{size[1]}?access_token={MAPBOX_ACCESS_TOKEN}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                image_data = await response.read()
                return Image.open(BytesIO(image_data))
        except aiohttp.ClientError as e:
            logging.error(f"Error fetching satellite image: {e}")
            return None

# Beispielbild abrufen (dies sollte in einer Schleife für alle Parkplätze durchgeführt werden)
example_image = asyncio.run(fetch_satellite_image(parking_df.iloc[0]['latitude'], parking_df.iloc[0]['longitude']))
if example_image:
    example_image.save("example_parking_image.jpg")

# YOLOv5 Modell laden (z.B. YOLOv5s)
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

# Funktion zur Vorhersage von Parkplätzen in einem Bild
def detect_parking_lots(image: Image.Image) -> torch.Tensor:
    """Detect parking lots in an image using YOLOv5."""
    results = model(image)
    return results

# Beispiel: Parkplätze im Bild erkennen
if example_image:
    results = detect_parking_lots(example_image)
    results.save('runs/detect/exp')  # Speichern der Ergebnisse

# Funktion zur Geokodierung einer Adresse
def geocode_address(address: str) -> Optional[Tuple[float, float]]:
    """Geocode an address to get latitude and longitude."""
    try:
        geolocator = Nominatim(user_agent=USER_AGENT, timeout=10)
        location = geolocator.geocode(address)
        if location:
            return (location.latitude, location.longitude)
        else:
            return None
    except Exception as e:
        logging.error(f"Fehler beim Geocoding der Adresse: {e}")
        return None

# Funktion zur Vorhersage der nächsten Parkplätze
def get_nearest_parkings(address_or_current_location: str, parking_df: pd.DataFrame) -> Tuple[Optional[Tuple[float, float]], Optional[pd.DataFrame]]:
    """Predict the nearest parking locations to a given address."""
    user_location = geocode_address(address_or_current_location)
    if user_location is None:
        logging.error("Die eingegebene Adresse konnte nicht gefunden werden.")
        return None, None

    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(parking_df[['latitude', 'longitude']], np.arange(len(parking_df)))

    nearest_indices = knn.kneighbors([user_location], n_neighbors=5, return_distance=False)
    nearest_parkings = parking_df.iloc[nearest_indices[0]]
    
    return user_location, nearest_parkings

# Funktion zur Anzeige auf der Karte
def display_on_map(user_location: Tuple[float, float], nearest_parkings: pd.DataFrame) -> None:
    """Display the user's location and nearest parking locations on a map."""
    m = folium.Map(location=user_location, zoom_start=15)
    folium.Marker(location=user_location, popup="User Location", icon=folium.Icon(color='red', icon='home')).add_to(m)
    marker_cluster = MarkerCluster().add_to(m)

    for _, row in nearest_parkings.iterrows():
        folium.Marker(location=[row['latitude'], row['longitude']], popup="Parking Lot", icon=folium.Icon(color='blue', icon='info-sign')).add_to(marker_cluster)

    m.save('nearest_parkings_map.html')
    logging.info("Map saved as nearest_parkings_map.html")

# Hauptfunktion
def main() -> None:
    address = input("Bitte geben Sie die Adresse ein (z. B. Uraniastrasse 3, 8001 Zürich, Schweiz): ")
    user_location, nearest_parkings = get_nearest_parkings(address, parking_df)
    
    if nearest_parkings is not None:
        display_on_map(user_location, nearest_parkings)

if __name__ == '__main__':
    main()
