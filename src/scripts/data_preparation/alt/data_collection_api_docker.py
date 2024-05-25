import os
import requests
import pandas as pd
import mysql.connector
from mysql.connector import Error

# Funktion zum Abrufen der Daten von der API
def get_data_from_api():
    url = 'https://www.ogd.stadt-zuerich.ch/wfs/geoportal/Oeffentlich_zugaengliche_Strassenparkplaetze_OGD?service=WFS&version=1.1.0&request=GetFeature&outputFormat=GeoJSON&typename=view_pp_ogd'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print("Daten erfolgreich von der API abgerufen")
        return data
    else:
        print("Fehler beim Abrufen der Daten:", response.status_code)
        return None

# Funktion zum Bereinigen und Verarbeiten der Daten
def clean_and_process_data(data):
    if data is not None and 'features' in data:
        features = data['features']
        cleaned_data = []

        for feature in features:
            properties = feature.get('properties', {})
            geometry = feature.get('geometry', {})
            coordinates = geometry.get('coordinates', [])
            
            # Extracting ID from properties and adding "SP" prefix
            id1 = properties.get('id1')
            id_with_prefix = f"SP{id1}" if id1 is not None else None

            # Überprüfen, ob erforderliche Felder vorhanden sind
            if 'parkdauer' in properties and 'art' in properties and id_with_prefix and 'gebuehrenpflichtig' in properties and len(coordinates) == 2:
                cleaned_data.append({
                    'ID': id_with_prefix,
                    'ART': 'Strassenparkplatz',
                    'NAME': properties['art'],
                    'PREIS': properties['gebuehrenpflichtig'],
                    'FREIE_PLÄTZE': 'keine Angabe',
                    'PARKDAUER': properties['parkdauer'],
                    'BREITENGRAD': coordinates[1],
                    'LAENGENGRAD': coordinates[0],
                    'DIENSTLEISTUNGEN': '',
                    'ZAHLUNGSMETHODEN': '',
                    'BESCHREIBUNG': '',
                    'BESCHREIBUNG_BILD': '',
                    'EINFAHRTSHÖHE': '',
                    'ANZAHL_PARKPLÄTZE': 0,
                })

        df = pd.DataFrame(cleaned_data)
        # Entfernen von NaN-Werten und Duplikaten
        df.dropna(inplace=True)
        df.drop_duplicates(inplace=True)
        print("Daten erfolgreich bereinigt und verarbeitet")
        print(df.head())  # Zeige die ersten Zeilen des DataFrames an
        print(df.dtypes)  # Zeige die Datentypen der Spalten an
        return df
    else:
        print("Keine Daten zum Bereinigen und Verarbeiten vorhanden")
        return None

# Funktion zum Einfügen der Daten in die MySQL-Datenbank
def insert_data_to_mysql(connection, cleaned_data):
    if cleaned_data is not None:
        cursor = connection.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS parkplatz_info (
                    ID VARCHAR(255) PRIMARY KEY,
                    ART TEXT,
                    NAME VARCHAR(255),
                    PREIS VARCHAR(255),
                    FREIE_PLÄTZE VARCHAR(255),
                    PARKDAUER INT,
                    BREITENGRAD DOUBLE,
                    LAENGENGRAD DOUBLE,
                    DIENSTLEISTUNGEN TEXT,
                    ZAHLUNGSMETHODEN TEXT,
                    BESCHREIBUNG TEXT,
                    BESCHREIBUNG_BILD TEXT,
                    EINFAHRTSHÖHE TEXT,
                    ANZAHL_PARKPLÄTZE INT
                )
            """)
            for index, row in cleaned_data.iterrows():
                try:
                    cursor.execute("""
                        INSERT INTO parkplatz_info (
                            ID,
                            ART,
                            NAME,
                            PREIS,
                            FREIE_PLÄTZE,
                            PARKDAUER,
                            BREITENGRAD,
                            LAENGENGRAD,
                            DIENSTLEISTUNGEN,
                            ZAHLUNGSMETHODEN,
                            BESCHREIBUNG,
                            BESCHREIBUNG_BILD,
                            EINFAHRTSHÖHE,
                            ANZAHL_PARKPLÄTZE
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        row["ID"],
                        row["ART"],
                        row["NAME"],
                        row["PREIS"],
                        row["FREIE_PLÄTZE"],
                        row["PARKDAUER"],
                        row["BREITENGRAD"],
                        row["LAENGENGRAD"],
                        row["DIENSTLEISTUNGEN"],
                        row["ZAHLUNGSMETHODEN"],
                        row["BESCHREIBUNG"],
                        row["BESCHREIBUNG_BILD"],
                        row["EINFAHRTSHÖHE"],
                        row["ANZAHL_PARKPLÄTZE"]
                    ))
                    print(f"Erfolgreich eingefügt: {row['ID']}")
                except mysql.connector.Error as e:
                    print(f"Fehler beim Einfügen von {row['ID']}: {e}")
            connection.commit()
            print("Daten erfolgreich in MySQL-Datenbank gespeichert")
        except mysql.connector.Error as e:
            print("Fehler beim Einfügen von Daten:", e)
        finally:
            cursor.close()
    else:
        print("Keine bereinigten Daten zum Einfügen in die Datenbank vorhanden")

# Funktion zum Sammeln von Daten, Aufbereiten und Speichern in der Datenbank
def collect_data_and_store():
    try:
        # Verbindung zur MySQL-Datenbank herstellen
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', 3306),
            user=os.getenv('DB_USER', 'user'),
            password=os.getenv('DB_PASSWORD', 'password'),
            database=os.getenv('DB_DATABASE', 'mydatabase')
        )
        if connection.is_connected():
            print("MySQL-Verbindung erfolgreich hergestellt")
            # Daten von der API abrufen
            data = get_data_from_api()
            # Daten aufbereiten
            cleaned_data = clean_and_process_data(data)
            if cleaned_data is not None:
                # Daten in die MySQL-Datenbank einfügen
                insert_data_to_mysql(connection, cleaned_data)
    except Error as e:
        print("Fehler bei der Verbindung zur MySQL-Datenbank:", e)
    finally:
        if connection.is_connected():
            connection.close()
            print("MySQL-Verbindung geschlossen")

if __name__ == '__main__':
    # Daten sammeln, aufbereiten und in die Datenbank einfügen
    collect_data_and_store()
