import pandas as pd
import mysql.connector
from mysql.connector import Error
import json
import os
from geopy.geocoders import Nominatim
from sklearn.neighbors import KNeighborsClassifier
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

def geocode_address(address):
    try:
        geolocator = Nominatim(user_agent="parking_locator", timeout=10)
        location = geolocator.geocode(address)
        if location:
            return (location.latitude, location.longitude)
        else:
            return None
    except Exception as e:
        print("Error geocoding address:", e)
        return None

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
            # Train KNN model
            knn = KNeighborsClassifier(n_neighbors=5)  # Adjust k as needed
            knn.fit(data_parking[['BREITENGRAD', 'LAENGENGRAD']], data_parking['NAME'])
            
            # Predict nearest parkings
            nearest_parkings_index = knn.kneighbors([user_location], n_neighbors=5, return_distance=False)
            nearest_parkings = data_parking.iloc[nearest_parkings_index[0]]
            print("Nearest Parkings:")
            print(nearest_parkings[['NAME', 'BREITENGRAD', 'LAENGENGRAD', 'PARKDAUER', 'ART']])
            
            return user_location, nearest_parkings
        else:
            print("No parking data available.")
            return None, None
    else:
        print("Could not geocode the address.")
        return None, None

def display_on_map(user_location, nearest_parkings):
    # Initialize map centered at user's location
    map_center = [user_location[0], user_location[1]]
    m = folium.Map(location=map_center, zoom_start=15)

    # Add user's location marker
    folium.Marker(location=map_center, popup="User Location", icon=folium.Icon(color='blue')).add_to(m)

    # Add nearest parking spots markers
    for index, parking in nearest_parkings.iterrows():
        folium.Marker(location=[parking['BREITENGRAD'], parking['LAENGENGRAD']],
                      popup=parking['NAME'],
                      icon=folium.Icon(color='green')).add_to(m)

    # Save map to HTML file
    m.save('nearest_parkings_map.html')
    print("Map saved as nearest_parkings_map.html")

if __name__ == '__main__':
    mysql_credentials_file = os.path.join("config", "config_mysql_credentials.json")
    host, port, user, password, database = read_mysql_credentials(mysql_credentials_file)
    if host and port and user and password and database:
        connection = connect_to_mysql(host, port, user, password, database)
        if connection:            
                     
            address = input("Please enter the address (e.g., Uraniastrasse 3, 8001 Zürich, Switzerland): ")
            user_location, nearest_parkings = get_nearest_parkings(address, connection)
                
            if nearest_parkings is not None:
                print("Nearest Parkings:")
                print(nearest_parkings)
                
                # Display results on map
                display_on_map(user_location, nearest_parkings)
                
            # Close the connection
            connection.close()
    else:
        print(f"Config file not found")
