import requests
import pandas as pd
import mysql.connector
from mysql.connector import Error
from scripts.data_collection.data_collection import collect_data
import json


# Funktion zum Entfernen von NaN-Werten und Duplikaten sowie zur Datenaufbereitung
def clean_and_process_data(data):
    if data is not None:
        # Lade die JSON-Daten und überprüfe, ob die Spalteninformationen vorhanden sind
        try:
            columns = data["abstimmungsresultate"]["columns"]
        except KeyError:
            print("Spalteninformationen nicht gefunden.")
            return None
        
        # Extrahiere die Spaltennamen aus den Spalteninformationen
        column_names = [column["name"] for column in columns]

        # Erstelle ein leeres DataFrame mit den extrahierten Spaltennamen
        df = pd.DataFrame(columns=column_names)

        # Entferne NaN-Werte und Duplikate
        df.dropna(inplace=True)
        df.drop_duplicates(inplace=True)

        # Weitere Verarbeitung hier, falls erforderlich
        return df
    else:
        return None

def insert_data_to_mysql(connection, df):
    if df is not None:
        cursor = connection.cursor()
        try:
            # Extrahiere Spaltennamen und Datentypen aus dem DataFrame
            columns = ", ".join([f"{column} {df[column].dtype}" for column in df.columns])
            # Erstelle die CREATE TABLE-Anweisung dynamisch
            cursor.execute(f"CREATE TABLE IF NOT EXISTS ads_database ({columns})")

            # Erstelle die INSERT-Anweisung dynamisch basierend auf den Spaltennamen
            placeholders = ", ".join(["%s"] * len(df.columns))
            columns = ", ".join(df.columns)
            query = f"INSERT INTO ads_database ({columns}) VALUES ({placeholders})"

            # Führe die INSERT-Anweisung für jede Zeile im DataFrame aus
            for index, row in df.iterrows():
                cursor.execute(query, tuple(row))

            connection.commit()
            print("Daten erfolgreich in MySQL-Datenbank gespeichert")
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
    # MySQL-Verbindungsinformationen aus JSON-Datei lesen
    host, port, user, password, database = read_mysql_credentials('ADS_project\\config\\config_mysql_credentials.json')
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
                df = clean_and_process_data(data)
                if df is not None:
                    # Daten in die MySQL-Datenbank einfügen
                    insert_data_to_mysql(connection, df)
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