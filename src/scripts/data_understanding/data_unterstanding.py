import mysql.connector
import pandas as pd
from mysql.connector import Error
import json
import os
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

def load_geographic_data_from_mysql(connection, table_name):
    try:
        # Annahme: Ihre Tabelle enthält Spalten 'BREITENGRAD' und 'LAENGENGRAD' für die Koordinaten
        query = f"SELECT BREITENGRAD, LAENGENGRAD FROM {table_name} LIMIT 50"
        df = pd.read_sql(query, connection)
        return df
    except Error as e:
        print("Fehler beim Laden der geografischen Daten aus der MySQL-Datenbank:", e)
        return None

def load_data_from_mysql(connection, table_name):
    try:
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, connection)
        return df
    except Error as e:
        print("Fehler beim Laden der Daten aus der MySQL-Datenbank:", e)
        return None

def explore_data(df):
    # Hier können Sie Ihre explorative Datenanalyse durchführen
    # Zum Beispiel:
    print("Erste 5 Zeilen des DataFrames:")
    print(df.head())
    
    print("\nInfo über den DataFrame:")
    print(df.info())

    print("\nStatistische Zusammenfassung des DataFrames:")
    print(df.describe())

    # Führen Sie weitere Analyseoperationen durch, wie z.B. Visualisierungen usw.

def create_map(df):
    # Erstellt eine Karte mit dem Mittelpunkt basierend auf dem Durchschnitt der Koordinaten
    latitude = df['BREITENGRAD'].mean()
    longitude = df['LAENGENGRAD'].mean()
    map = folium.Map(location=[latitude, longitude], zoom_start=10)
    
    # Markiert jeden Punkt auf der Karte
    for index, row in df.iterrows():
        folium.Marker([row['BREITENGRAD'], row['LAENGENGRAD']]).add_to(map)
    
    return map

if __name__ == '__main__':
    mysql_credentials_file = os.path.join("config", "config_mysql_credentials.json")
    host, port, user, password, database = read_mysql_credentials(mysql_credentials_file)
    if host and port and user and password and database:
        connection = connect_to_mysql(host, port, user, password, database)
        if connection:
            table_name = 'parkplatz_info'
            df = load_geographic_data_from_mysql(connection, table_name)
            if df is not None:
                explore_data(df)
                # Erstellen Sie die Karte und speichern Sie sie als HTML-Datei
                map = create_map(df)
                map.save("map.html")
                print("Karte erstellt und als 'map.html' gespeichert.")
            else:
                print("Fehler beim Laden der geografischen Daten aus der MySQL-Datenbank.")
            connection.close()  # Verbindung schließen
