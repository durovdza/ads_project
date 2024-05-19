import pandas as pd
import mysql.connector
from mysql.connector import Error
import json
import os
from sqlalchemy import create_engine
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import folium

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
        print(f"Error reading data from MySQL database: {e}")
        return None

def check_table_structure(connection, table_name):
    try:
        cursor = connection.cursor()
        cursor.execute(f"DESCRIBE {table_name}")
        result = cursor.fetchall()
        print(f"Structure of table {table_name}:")
        for row in result:
            print(row)
    except Error as e:
        print(f"Error describing table {table_name}: {e}")

def geocode_address(address):
    geolocator = Nominatim(user_agent="parking_locator")
    location = geolocator.geocode(address)
    if location:
        return (location.latitude, location.longitude)
    else:
        return None

def calculate_distances(user_location, parkings):
    distances = []
    for index, parking in parkings.iterrows():
        parking_location = (parking['BREITENGRAD'], parking['LAENGENGRAD'])
        distance = geodesic(user_location, parking_location).meters
        distances.append(distance)
    parkings['Distance'] = distances
    return parkings

def get_nearest_parkings(address, connection):
    user_location = geocode_address(address)
    if user_location:
        print(f"Coordinates of the address: {user_location}")
        
        query_parking_data = """
        SELECT `NAME`, `BREITENGRAD`, `LAENGENGRAD`, `PARKDAUER`, `ART`
        FROM ads.parkplatz_info
        """
        
        data_parking = read_data_from_mysql(connection, query_parking_data)
        
        if data_parking is not None and not data_parking.empty:
            data_parking = calculate_distances(user_location, data_parking)
            nearest_parkings = data_parking.sort_values(by='Distance').head(5)
            print("Nearest Parkings:")
            print(nearest_parkings[['NAME', 'Distance', 'PARKDAUER', 'ART']])
            
            return user_location, nearest_parkings
        else:
            print("No parking data available.")
            return None, None
    else:
        print("Could not geocode the address.")
        return None, None


def visualize_on_map(user_location, nearest_parkings):
    map = folium.Map(location=user_location, zoom_start=15)
    folium.Marker(user_location, popup="User Location", icon=folium.Icon(color='red')).add_to(map)
    
    for _, row in nearest_parkings.iterrows():
        parking_location = (row['BREITENGRAD'], row['LAENGENGRAD'])
        popup_text = f"{row['NAME']}\nDistanz: {row['Distance']:.2f} m\nPARKDAUER: {row['PARKDAUER']}\nART: {row['ART']}"
        folium.Marker(parking_location, popup=popup_text).add_to(map)
    
    map.save('nearest_parkings_map.html')
    print("Map saved as 'nearest_parkings_map.html'")

if __name__ == '__main__':
    mysql_credentials_file = os.path.join("config", "config_mysql_credentials.json")
    host, port, user, password, database = read_mysql_credentials(mysql_credentials_file)
    if host and port and user and password and database:
        connection = connect_to_mysql(host, port, user, password, database)
        if connection:            
                     
            address = input("Please enter the address (e.g., Uraniastrasse 3, 8001 Zürich, Switzerland): ")
            user_location, nearest_parkings = get_nearest_parkings(address, connection)
                
            if nearest_parkings is not None:
                visualize_on_map(user_location, nearest_parkings)
                
            # Schließen Sie die Verbindung
            connection.close()
    else:
        print(f"Config file not found")

