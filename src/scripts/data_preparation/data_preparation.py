import requests
import pandas as pd
import mysql.connector
from mysql.connector import Error
import json
import os

def collect_data():
    file_path = os.path.join("config", "config_data_sources.json")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        
    collected_data = {}
    for source, info in data.items():
        url = info['url']
        response = requests.get(url)
        if response.status_code == 200:
            collected_data[source] = response.json()
        else:
            print(f"Fehler beim Abrufen der Daten von {source}: {response.status_code}")
    
    return collected_data

# Funktion zum Entfernen von NaN-Werten und Duplikaten sowie zur Datenaufbereitung
def clean_and_process_data(data):
    cleaned_data = {}

    if data is not None:
        # Iteriere über alle Datenquellen
        for source, info in data.items():
            # Erstelle ein leeres DataFrame für jede Datenquelle
            df = pd.DataFrame()

            # Lade die Spalteninformationen für jede Datenquelle
            try:
                columns = info["columns"]
            except KeyError:
                print(f"Spalteninformationen für Datenquelle '{source}' nicht gefunden.")
                continue
            
            # Extrahiere die Spaltennamen aus den Spalteninformationen
            column_names = [column["name"] for column in columns]

            # Füge die Spalteninformationen zum DataFrame hinzu
            df = df.append(pd.DataFrame(columns=column_names))

            # Entferne NaN-Werte und Duplikate für die jeweilige Datenquelle
            df.dropna(inplace=True)
            df.drop_duplicates(inplace=True)

            # Benenne das DataFrame entsprechend dem Namen der Datenquelle und füge es der bereinigten Datenstruktur hinzu
            cleaned_data[source] = df

        # Rückgabe der bereinigten Daten für alle Datenquellen
        return cleaned_data
    else:
        return None

def insert_data_to_mysql(connection, df, source):
    if df is not None:
        cursor = connection.cursor()
        try:
            # Extrahiere Spaltennamen und Datentypen aus dem DataFrame
            columns = ", ".join([f"{column} {df[column].dtype}" for column in df.columns])
            # Erstelle die CREATE TABLE-Anweisung dynamisch
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {source} ({columns})")

            # Erstelle die INSERT-Anweisung dynamisch basierend auf den Spaltennamen
            placeholders = ", ".join(["%s"] * len(df.columns))
            columns = ", ".join(df.columns)
            query = f"INSERT INTO {source} ({columns}) VALUES ({placeholders})"

            # Führe die INSERT-Anweisung für jede Zeile im DataFrame aus
            for index, row in df.iterrows():
                cursor.execute(query, tuple(row))

            connection.commit()
            print(f"Daten für Datenquelle '{source}' erfolgreich in MySQL-Datenbank gespeichert")
        except Error as e:
            print("Fehler beim Einfügen von Daten:", e)
        finally:
            cursor.close()

# Funktion zum Ausführen von SQL-Abfragen
def execute_sql_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print("Fehler bei der Ausführung der SQL-Abfrage:", e)
    finally:
        cursor.close()

# Funktion zum Anzeigen der Abfrageergebnisse
def display_query_results(results):
    if results:
        for row in results:
            print(row)
    else:
        print("Keine Ergebnisse gefunden.")

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
                data = collect_data()
                # Daten aufbereiten
                cleaned_data = clean_and_process_data(data)
                if cleaned_data is not None:
                    # Daten in die MySQL-Datenbank einfügen
                    for source, df in cleaned_data.items():
                        insert_data_to_mysql(connection, df, source)
                    # SQL-Abfrage ausführen
                    query = "SELECT * FROM ads_database LIMIT 10"
                    results = execute_sql_query(connection, query)
                    # Ergebnisse anzeigen
                    display_query_results(results)
    except Error as e:
        print("Fehler bei der Verbindung zur MySQL-Datenbank:", e)
    finally:
        if connection.is_connected():
            connection.close()
            print("MySQL-Verbindung geschlossen")

if __name__ == '__main__':
    # Daten sammeln, aufbereiten und in die Datenbank einfüge
    collect_data_and_store()