import mysql.connector
import pandas as pd
from mysql.connector import Error
import json
import os
import folium
from folium.plugins import MarkerCluster

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

def load_geographic_data_from_mysql(connection, table_name, limit, offset):
    try:
        query = f"SELECT BREITENGRAD, LAENGENGRAD FROM {table_name} LIMIT {limit} OFFSET {offset}"
        df = pd.read_sql(query, connection)
        return df
    except Error as e:
        print("Fehler beim Laden der geografischen Daten aus der MySQL-Datenbank:", e)
        return None

def explore_data(df):
    print("Erste 5 Zeilen des DataFrames:")
    print(df.head())
    
    print("\nInfo über den DataFrame:")
    print(df.info())

    print("\nStatistische Zusammenfassung des DataFrames:")
    print(df.describe())

def create_map(df):
    latitude = df['BREITENGRAD'].mean()
    longitude = df['LAENGENGRAD'].mean()
    map = folium.Map(location=[latitude, longitude], zoom_start=10)

    marker_cluster = MarkerCluster().add_to(map)
    
    for index, row in df.iterrows():
        folium.Marker([row['BREITENGRAD'], row['LAENGENGRAD']]).add_to(marker_cluster)
    
    return map

if __name__ == '__main__':
    mysql_credentials_file = os.path.join("config", "config_mysql_credentials.json")
    host, port, user, password, database = read_mysql_credentials(mysql_credentials_file)
    if host and port and user and password and database:
        connection = connect_to_mysql(host, port, user, password, database)
        if connection:
            table_name = 'parkplatz_info'
            limit = 50
            offset = 0
            all_data = []

            while True:
                df = load_geographic_data_from_mysql(connection, table_name, limit, offset)
                if df is None or df.empty:
                    break
                all_data.append(df)
                offset += limit

            if all_data:
                combined_df = pd.concat(all_data, ignore_index=True)
                explore_data(combined_df)
                map = create_map(combined_df)
                map.save("map.html")
                print("Karte erstellt und als 'map.html' gespeichert.")
            else:
                print("Keine geografischen Daten geladen.")
                
            connection.close()
