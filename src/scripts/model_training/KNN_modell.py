import pandas as pd
import mysql.connector
from mysql.connector import Error
import json
import os
from geopy.geocoders import Nominatim
from sklearn.neighbors import KNeighborsClassifier, BallTree
import folium
from folium.plugins import MarkerCluster
from sklearn.cluster import DBSCAN
import numpy as np

def connect_to_mysql(host, port, user, password, database):
    try:
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        if connection.is_connected():
            print("MySQL-Verbindung erfolgreich hergestellt")
            return connection
    except Error as e:
        print("Fehler bei der Verbindung zur MySQL-Datenbank:", e)
        return None

def read_mysql_credentials(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        host = data.get('host')
        port = data.get('port')
        user = data.get('user')
        password = data.get('password')
        database = data.get('database')
        return host, port, user, password, database
    except Exception as e:
        print("Fehler beim Lesen der JSON-Datei:", e)
        return None, None, None, None, None

def read_data_from_mysql(connection, query):
    try:
        data = pd.read_sql(query, connection)
        return data
    except Exception as e:
        print(f"Fehler beim Lesen der Daten aus der MySQL-Datenbank: {e}")
        return None

def geocode_address(address):
    try:
        geolocator = Nominatim(user_agent="parking_locator", timeout=10)
        location = geolocator.geocode(address)
        if location:
            return (location.latitude, location.longitude)
        else:
            return None
    except Exception as e:
        print("Fehler beim Geocoding der Adresse:", e)
        return None

def get_nearest_parkings(address_or_current_location, connection):
    if not address_or_current_location.strip():
        # No address provided, use current location
        locator = Nominatim(user_agent="parking_locator")
        location = locator.geocode("")

        if location:
            user_location = (location.latitude, location.longitude)
            print("Aktueller Standort:", user_location)
        else:
            print("Aktueller Standort konnte nicht ermittelt werden.")
            return None, None, None, None
    else:
        user_location = geocode_address(address_or_current_location)
        if user_location is None:
            print("Die eingegebene Adresse konnte nicht gefunden werden.")
            return None, None, None, None
        else:
            print(f"Koordinaten der Adresse '{address_or_current_location}': {user_location}")

    query_parking_data = """
    SELECT `NAME`, `BREITENGRAD`, `LAENGENGRAD`, `PARKDAUER`, `ART`
    FROM ads.parkplatz_info
    WHERE `ART` IN ('Parkhaus', 'Strassenparkplatz')
    """
    
    data_parking = read_data_from_mysql(connection, query_parking_data)
    
    if data_parking is not None and not data_parking.empty:
        # Separate Strassenparkplatz and Parkhaus
        strassenparkplatz_data = data_parking[data_parking['ART'] == 'Strassenparkplatz']
        parkhaus_data = data_parking[data_parking['ART'] == 'Parkhaus']
        
        clustered_parking = []
        if not strassenparkplatz_data.empty:
            # Cluster Strassenparkplatz data using DBSCAN
            coords = strassenparkplatz_data[['BREITENGRAD', 'LAENGENGRAD']].values
            kms_per_radian = 6371.0088
            epsilon = 0.05 / kms_per_radian  # 50 meters

            db = DBSCAN(eps=epsilon, min_samples=1, algorithm='ball_tree', metric='haversine').fit(np.radians(coords))
            cluster_labels = db.labels_
            
            strassenparkplatz_data['cluster'] = cluster_labels
            
            for cluster in strassenparkplatz_data['cluster'].unique():
                cluster_group = strassenparkplatz_data[strassenparkplatz_data['cluster'] == cluster]
                center_lat = cluster_group['BREITENGRAD'].mean()
                center_lon = cluster_group['LAENGENGRAD'].mean()
                count = len(cluster_group)
                clustered_parking.append((center_lat, center_lon, count))
        
        # Combine clustered Strassenparkplatz and Parkhaus data
        combined_data = pd.DataFrame(clustered_parking, columns=['BREITENGRAD', 'LAENGENGRAD', 'COUNT'])
        parkhaus_data['COUNT'] = 1  # Each Parkhaus is considered as a single unit
        parkhaus_data_subset = parkhaus_data[['BREITENGRAD', 'LAENGENGRAD', 'COUNT']]
        combined_data = pd.concat([combined_data, parkhaus_data_subset], ignore_index=True)
        
        # Train KNN model
        knn = KNeighborsClassifier(n_neighbors=5)  # Adjust k as needed
        knn.fit(combined_data[['BREITENGRAD', 'LAENGENGRAD']], combined_data.index)
        
        # Predict nearest parkings
        nearest_parkings_index = knn.kneighbors([user_location], n_neighbors=5, return_distance=False)
        nearest_parkings = combined_data.iloc[nearest_parkings_index[0]]
        print("Nahegelegene Parkplätze:")
        print(nearest_parkings)
        
        return user_location, nearest_parkings, strassenparkplatz_data, parkhaus_data
    else:
        print("Keine Parkplatzdaten verfügbar.")
        return None, None, None, None
        

def display_on_map(user_location, nearest_parkings, strassenparkplatz_data, parkhaus_data):
    # Initialize map centered at user's location with custom tile style
    map_center = [user_location[0], user_location[1]]
    m = folium.Map(location=map_center, zoom_start=15)  # Start with a default zoom level
    
    # Add user's location marker
    folium.Marker(location=map_center, popup="User Location", icon=folium.Icon(color='red', icon='home')).add_to(m)
    
    # Add MarkerCluster for better visualization of clustered points
    marker_cluster = MarkerCluster().add_to(m)

    # Add nearest parking markers
    for index, row in nearest_parkings.iterrows():
        if row['COUNT'] > 1:
            # This is a clustered Strassenparkplatz
            popup_text = f"""
            <b>Parking Zone (Strassenparkplatz)</b><br>
            <b>Anzahl Parkplätze:</b> {row['COUNT']}
            """
            folium.Marker(location=[row['BREITENGRAD'], row['LAENGENGRAD']], popup=popup_text, 
                          icon=folium.Icon(color='blue', icon='info-sign')).add_to(marker_cluster)
        else:
            # This is a Parkhaus
            parkhaus_row = parkhaus_data[(parkhaus_data['BREITENGRAD'] == row['BREITENGRAD']) & 
                                         (parkhaus_data['LAENGENGRAD'] == row['LAENGENGRAD'])].iloc[0]
            popup_text = f"""
            <b>Name:</b> {parkhaus_row['NAME']}<br>
            <b>Latitude:</b> {parkhaus_row['BREITENGRAD']}<br>
            <b>Longitude:</b> {parkhaus_row['LAENGENGRAD']}<br>
            <b>Parkdauer:</b> {parkhaus_row['PARKDAUER']}<br>
            <b>Art:</b> {parkhaus_row['ART']}
            """
            folium.Marker(location=[row['BREITENGRAD'], row['LAENGENGRAD']],
                          popup=popup_text,
                          icon=folium.Icon(color='green', icon='info-sign')).add_to(marker_cluster)

    # Calculate bounds to include all markers
    if not nearest_parkings.empty:
        min_lat, max_lat = min(nearest_parkings['BREITENGRAD']), max(nearest_parkings['BREITENGRAD'])
        min_lon, max_lon = min(nearest_parkings['LAENGENGRAD']), max(nearest_parkings['LAENGENGRAD'])
        m.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]])

    # Save map to HTML file
    m.save('nearest_parkings_map.html')
    print("Map saved as nearest_parkings_map.html")

def get_html():
    mysql_credentials_file = os.path.join("config", "config_mysql_credentials.json")
    host, port, user, password, database = read_mysql_credentials(mysql_credentials_file)
    if host and port and user and password and database:
        connection = connect_to_mysql(host, port, user, password, database)
        if connection:
            address = input("Bitte geben Sie die Adresse ein (z. B. Uraniastrasse 3, 8001 Zürich, Schweiz): ")
            
            user_location, nearest_parkings, strassenparkplatz_data, parkhaus_data = get_nearest_parkings(address, connection)
            
            if nearest_parkings is not None:
                print("Nahegelegene Parkplätze:")
                print(nearest_parkings)
                
                # Ergebnisse auf der Karte anzeigen
                display_on_map(user_location, nearest_parkings, strassenparkplatz_data, parkhaus_data)
                
            # Verbindung schließen
            connection.close()
    else:
        print(f"Konfigurationsdatei nicht gefunden")


if __name__ == '__main__':
    get_html()