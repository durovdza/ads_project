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
    driver.get('https://www.parkingzuerich.ch/freie-parkplaetze/')

    # Wait for the data to load (you may need to adjust the waiting time)
    time.sleep(10)

    # Extract parking data
    parking_articles = driver.find_elements(By.CSS_SELECTOR, '.ht_parkhaus')

    data = []
    for article in parking_articles:
        try:
            name = article.find_element(By.CSS_SELECTOR, '.ht_parkhausTitle h2').text.strip()
            freie_plaetze = article.find_element(By.CSS_SELECTOR, '.ht_freeplace').text.strip()
            lat_script = article.find_element(By.XPATH, './/script[contains(text(), "var lat")]').get_attribute('innerHTML')
            lat = lat_script.split('var lat = ')[1].split(';')[0]
            lng = lat_script.split('var lng = ')[1].split(';')[0]

            services_elements = article.find_elements(By.CSS_SELECTOR, '.ht_parkhausService img')
            services = [service.get_attribute('alt') for service in services_elements]

            payment_elements = article.find_elements(By.CSS_SELECTOR, '.ht_parkhaus_billing img')
            payment_methods = [payment.get_attribute('alt') for payment in payment_elements]

            data.append({
                'Name': name,
                'Freie Plätze': freie_plaetze,
                'Latitude': lat,
                'Longitude': lng,
                'Services': ', '.join(services),
                'Payment Methods': ', '.join(payment_methods)
            })
        except Exception as e:
            print(f"Fehler beim Extrahieren von Daten für einen Parkplatz: {e}")

    # Close the driver
    driver.quit()

    # Convert to DataFrame
    df = pd.DataFrame(data)

    return df

def clean_and_process_data(df):
    # Entferne NaN-Werte und Duplikate
    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)

    return df

def insert_data_to_mysql(connection, df, table_name):
    cursor = connection.cursor()
    try:
        # Erstelle die Tabelle im Schema 'ads', wenn sie nicht existiert
        cursor.execute(f"CREATE TABLE IF NOT EXISTS ads.{table_name} ("
                       f"`Name` TEXT, "
                       f"`Freie Plätze` TEXT, "
                       f"`Latitude` TEXT, "
                       f"`Longitude` TEXT, "
                       f"`Services` TEXT, "
                       f"`Payment Methods` TEXT)")

        # Füge die Daten in die Tabelle ein
        for index, row in df.iterrows():
            placeholders = ', '.join(['%s'] * len(row))
            query = f"INSERT INTO ads.{table_name} VALUES ({placeholders})"
            cursor.execute(query, tuple(row))

        connection.commit()
        print(f"Daten erfolgreich in die Tabelle 'ads.{table_name}' eingefügt")
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
                    # Tabelle im Schema 'ads' in MySQL-Datenbank einfügen
                    table_name = 'parking_data'
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