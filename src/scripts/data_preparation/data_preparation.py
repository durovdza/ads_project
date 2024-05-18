import requests
import pandas as pd
import mysql.connector
from mysql.connector import Error
import json
import os

# Funktion zum Abrufen der Daten von der API
def get_data_from_api():
    url = 'https://www.ogd.stadt-zuerich.ch/wfs/geoportal/Oeffentlich_zugaengliche_Strassenparkplaetze_OGD?service=WFS&version=1.1.0&request=GetFeature&outputFormat=GeoJSON&typename=view_pp_ogd'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Fehler beim Abrufen der Daten:", response.status_code)
        return None

def clean_and_process_data(data):
    if data is not None and 'features' in data:
        features = data['features']
        cleaned_data = []

        for feature in features:
            properties = feature.get('properties', {})
            geometry = feature.get('geometry', {})
            coordinates = geometry.get('coordinates', [])
            
            # Extracting ID from properties
            id1 = properties.get('id1')
            # Überprüfen, ob erforderliche Felder vorhanden sind
            if 'parkdauer' in properties and 'art' in properties and 'id1' in properties and 'gebuehrenpflichtig' in properties and len(coordinates) == 2:
                cleaned_data.append({
                    'PARKDAUER': properties['parkdauer'],
                    'ART': properties['art'],
                    'ID_ART': id1,  # Using the extracted ID
                    'GEBUEHRENPFLICHTIG': properties['gebuehrenpflichtig'],
                    'GEOMETRIE': 'POINT({} {})'.format(coordinates[0], coordinates[1])  # Konvertierung der Koordinaten in das WKT-Format
                })

        df = pd.DataFrame(cleaned_data)
        # Entfernen von NaN-Werten und Duplikaten
        df.dropna(inplace=True)
        df.drop_duplicates(inplace=True)
        return df
    else:
        return None

    
def insert_data_to_mysql(connection, cleaned_data):
    if cleaned_data is not None:  
        cursor = connection.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS parking_data_public (
                    ID1 INT AUTO_INCREMENT PRIMARY KEY,
                    PARKDAUER INT,
                    ART VARCHAR(255),
                    ID_ART INT,
                    GEBUEHRENPFLICHTIG VARCHAR(255),
                    GEOMETRIE GEOMETRY
                )
            """)
            for index, row in cleaned_data.iterrows():  
                # Extract coordinates from the row
                geometry = row["GEOMETRIE"]
                # Einfügen der Daten in die Datenbank
                cursor.execute("""
                    INSERT INTO parking_data_public (
                        PARKDAUER,
                        ART,
                        ID_ART,
                        GEBUEHRENPFLICHTIG,
                        GEOMETRIE
                    ) VALUES (%s, %s, %s, %s, ST_GeomFromText(%s))
                """, (
                    row["PARKDAUER"],
                    row["ART"],
                    row["ID_ART"],
                    row["GEBUEHRENPFLICHTIG"],
                    geometry
                ))
            connection.commit()
            print("Daten erfolgreich in MySQL-Datenbank gespeichert")
        except Error as e:
            print("Fehler beim Einfügen von Daten:", e)
        finally:
            cursor.close()




# Funktion zum Lesen der MySQL-Verbindungsinformationen aus der JSON-Datei
def read_mysql_credentials(file_path):
    try:
        # JSON-Datei öffnen und Daten laden
        with open(file_path, 'r') as file:
            data = json.load(file)
        # Daten aus der JSON-Datei extrahieren
        host = data.get('host')
        port = data.get('port')
        user = data.get('user')
        password = data.get('password')
        database = data.get('database')
        return host, port, user, password, database
    except Exception as e:
        print("Fehler beim Lesen der JSON-Datei:", e)
        return None, None, None, None, None

# Funktion zum Sammeln von Daten, Aufbereiten und Speichern in der Datenbank
def collect_data_and_store():
    # Pfad zur JSON-Datei für die MySQL-Verbindungsinformationen
    mysql_credentials_file = os.path.join("config", "config_mysql_credentials.json")

    # MySQL-Verbindungsinformationen aus JSON-Datei lesen
    host, port, user, password, database = read_mysql_credentials(mysql_credentials_file)
    try:
        if host and port and user and password and database:
            # Verbindung zur MySQL-Datenbank herstellen
            connection = mysql.connector.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database
            )
            if connection.is_connected():
                print("MySQL-Verbindung erfolgreich hergestellt")
                # Daten von der API abrufen
                data = get_data_from_api()
                # Daten aufbereiten
                cleaned_data = clean_and_process_data(data)
                if cleaned_data is not None:
                    # Daten in die MySQL-Datenbank einfügen
                    insert_data_to_mysql(connection, cleaned_data)  # Remove unnecessary iteration
    except Error as e:
        print("Fehler bei der Verbindung zur MySQL-Datenbank:", e)
    finally:
        if connection.is_connected():
            connection.close()
            print("MySQL-Verbindung geschlossen")

if __name__ == '__main__':
    # Daten sammeln, aufbereiten und in die Datenbank einfügen
    collect_data_and_store()
