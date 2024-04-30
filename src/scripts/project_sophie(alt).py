import requests
import pandas as pd
import mysql.connector
from mysql.connector import Error

# Funktion zum Abrufen der Daten von der API
def get_data_from_api():
    url = 'https://data.stadt-zuerich.ch/api/3/action/datastore_search?resource_id=e40b8714-4067-4b09-a022-cba9b6178bd9&limit=10000'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Fehler beim Abrufen der Daten:", response.status_code)
        return None

# Funktion zum Entfernen von NaN-Werten und Duplikaten sowie zur Datenaufbereitung
def clean_and_process_data(data):
    if data is not None:
        df = pd.DataFrame(data["result"]["records"])
        # Entfernen von NaN-Werten und Duplikaten
        df.dropna(inplace=True)
        df.drop_duplicates(inplace=True)
        # Weitere Datenaufbereitung hier, falls erforderlich
        return df
    else:
        return None

# Funktion zum Speichern der Daten in MySQL-Datenbank
def insert_data_to_mysql(connection, df):
    if df is not None:
        cursor = connection.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ads_database (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    Abstimmungs_Datum DATE,
                    Nr_Politische_Ebene INT,
                    Name_Politische_Ebene VARCHAR(255),
                    Abstimmungs_Text TEXT,
                    Nr_Resultat_Gebiet INT,
                    Name_Resultat_Gebiet VARCHAR(255),
                    Nr_Wahlkreis_StZH INT,
                    Name_Wahlkreis_StZH VARCHAR(255),
                    Stimmberechtigt INT,
                    Ja INT,
                    Nein INT,
                    Stimmbeteiligung FLOAT,
                    Ja_Anteil FLOAT,
                    Nein_Anteil FLOAT,
                    Ja_Stände VARCHAR(255),
                    Nein_Stände VARCHAR(255)
                )
            """)
            for index, row in df.iterrows():
                # Einfügen der Daten in die Datenbank
                cursor.execute("""
                    INSERT INTO ads_database (
                        Abstimmungs_Datum,
                        Nr_Politische_Ebene,
                        Name_Politische_Ebene,
                        Abstimmungs_Text,
                        Nr_Resultat_Gebiet,
                        Name_Resultat_Gebiet,
                        Nr_Wahlkreis_StZH,
                        Name_Wahlkreis_StZH,
                        Stimmberechtigt,
                        Ja,
                        Nein,
                        Stimmbeteiligung,
                        Ja_Anteil,
                        Nein_Anteil,
                        Ja_Stände,
                        Nein_Stände
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    row["Abstimmungs_Datum"],
                    row["Nr_Politische_Ebene"],
                    row["Name_Politische_Ebene"],
                    row["Abstimmungs_Text"],
                    row["Nr_Resultat_Gebiet"],
                    row["Name_Resultat_Gebiet"],
                    row["Nr_Wahlkreis_StZH"],
                    row["Name_Wahlkreis_StZH"],
                    row["Stimmberechtigt"],
                    row["Ja"],
                    row["Nein"],
                    row["Stimmbeteiligung (%)"],
                    row["Ja (%)"],
                    row["Nein (%)"],
                    row.get("StaendeJa", ""),  # Using row.get() to handle missing key
                    row.get("SteandeNein", "")  # Using row.get() to handle missing key
                ))
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

# Funktion zum Auslesen der MySQL-Anmeldeinformationen aus einer Textdatei
def read_mysql_credentials(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
        host = lines[0].split(": ")[1].strip()
        port = int(lines[1].split(": ")[1].strip())
        user = lines[2].split(": ")[1].strip()
        password = lines[3].split(": ")[1].strip()
        database = lines[4].split(": ")[1].strip()
    return host, port, user, password, database

# Hauptfunktion
def main():
    # MySQL-Verbindungsinformationen aus Datei lesen
    host, port, user, password, database = read_mysql_credentials('DS_project\mysql_credentials.txt')
    try:
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

if __name__ == "__main__":
    main()
