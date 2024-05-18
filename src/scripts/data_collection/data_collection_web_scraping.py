import time
import pandas as pd
import mysql.connector
from mysql.connector import Error
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def collect_data():
    # Chrome service
    service = Service(executable_path=r'C:\Users\smaie\chromedriver-win64\chromedriver.exe')
    # Chrome options
    opts = Options()
    opts.add_argument("--headless")  # Run Chrome in headless mode

    # Start Chrome driver
    driver = webdriver.Chrome(service=service, options=opts)

    # Website to scrape
    driver.get('https://opendata.swiss/de/dataset/median-einkommen-steuerpflichtiger-naturlicher-personen-nach-jahr-steuertarif-und-stadtquartier/resource/1e16f1e5-d78c-4a20-9462-19bbda54d79f')

    # Wait for the table to load (you may need to adjust the waiting time)
    time.sleep(30)

    # Extract table data
    table = driver.find_element(By.XPATH, '/html/body/div/div/div[4]/div[1]/div[5]')
    table_html = table.get_attribute('outerHTML')

    # Read HTML table into a pandas dataframe
    df = pd.read_html(table_html)[0]

    # Close the driver
    driver.quit()

    return df

def clean_and_process_data(df):
    # Entferne NaN-Werte und Duplikate
    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)

    return df

def insert_data_to_mysql(connection, df, table_name):
    cursor = connection.cursor()
    try:
        # Erstelle die Tabelle, wenn sie nicht existiert
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join([f'{col} TEXT' for col in df.columns])})")

        # Füge die Daten in die Tabelle ein
        for index, row in df.iterrows():
            placeholders = ', '.join(['%s'] * len(row))
            query = f"INSERT INTO {table_name} VALUES ({placeholders})"
            cursor.execute(query, tuple(row))

        connection.commit()
        print(f"Daten erfolgreich in die Tabelle '{table_name}' eingefügt")
    except Error as e:
        print("Fehler beim Einfügen von Daten:", e)
    finally:
        cursor.close()

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

def collect_data_and_store():
    # Pfad zur JSON-Datei für die MySQL-Verbindungsinformationen
    mysql_credentials_file = os.path.join("config", "config_mysql_credentials.json")

    # MySQL-Verbindungsinformationen aus JSON-Datei lesen
    host, port, user, password, database = read_mysql_credentials(mysql_credentials_file)
    try:
        if host and port and user and password and database:
            # Verbindung zur MySQL-Datenbank herstellen
            connection = connect_to_mysql(host, port, user, password, database)
            if connection:
                # Daten sammeln
                df = collect_data()
                # Daten bereinigen und verarbeiten
                df_cleaned = clean_and_process_data(df)
                if not df_cleaned.empty:
                    # Tabelle in MySQL-Datenbank einfügen
                    table_name = 'median_income_data'
                    insert_data_to_mysql(connection, df_cleaned, table_name)
    except Error as e:
        print("Fehler bei der Verbindung zur MySQL-Datenbank:", e)
    finally:
        if connection.is_connected():
            connection.close()
            print("MySQL-Verbindung geschlossen")

if __name__ == '__main__':
    # Daten sammeln, aufbereiten und in die Datenbank einfügen
    collect_data_and_store()
