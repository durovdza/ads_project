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
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import re

def collect_data():
    service = Service(executable_path=r'C:\Users\smaie\chromedriver-win64\chromedriver.exe')
    opts = Options()
    opts.add_argument("--headless")

    driver = webdriver.Chrome(service=service, options=opts)
    driver.get('https://www.parkingzuerich.ch/freie-parkplaetze/')
    time.sleep(10)

    parking_articles = driver.find_elements(By.CSS_SELECTOR, '.ht_parkhaus')

    data = []
    for article in parking_articles:
        try:
            id = "PH" + article.get_attribute('key')
            name = article.find_element(By.CSS_SELECTOR, '.ht_parkhausTitle h2').text.strip()
            freie_plaetze = article.find_element(By.CSS_SELECTOR, '.ht_freeplace').text.strip()
            lat_script = article.find_element(By.XPATH, './/script[contains(text(), "var lat")]').get_attribute('innerHTML')
            lat = lat_script.split('var lat = ')[1].split(';')[0]
            lng = lat_script.split('var lng = ')[1].split(';')[0]
            
            

            parkdauer_element = article.find_element(By.CSS_SELECTOR, '.ht_parkhausTime')
            parkdauer_text = parkdauer_element.text.strip()
            parkdauer_match = re.search(r'\d+', parkdauer_text)
            if parkdauer_match:
                parkdauer = int(parkdauer_match.group())
            else:
                parkdauer = 0  # Setzen Sie parkdauer auf None, wenn kein numerischer Wert gefunden wurde

            dienstleistungen_elements = article.find_elements(By.CSS_SELECTOR, '.ht_parkhausService img')
            dienstleistungen = [dienstleistung.get_attribute('alt') for dienstleistung in dienstleistungen_elements]

            zahlungsmethoden_elements = article.find_elements(By.CSS_SELECTOR, '.ht_parkhaus_billing img')
            zahlungsmethoden = [zahlungsmethode.get_attribute('alt') for zahlungsmethode in zahlungsmethoden_elements]

            beschreibung = article.find_element(By.CSS_SELECTOR, '.ht_openDropDesc p').text.strip()
            bild_url = article.find_element(By.CSS_SELECTOR, '.ht_openDropDesc img').get_attribute('src')

            einfahrtshoehe = article.find_element(By.XPATH, '//span[contains(text(), "Einfahrtshöhe")]/following-sibling::span').text.strip()
            anzahl_parkplaetze = 0

            data.append({
                'ID': id,
                'ART': 'Parkhaus',
                'NAME': name,
                'PREIS': 'gebührenpflichtig',
                'FREIE_PLÄTZE': freie_plaetze,
                'PARKDAUER': parkdauer,
                'BREITENGRAD': lat,
                'LAENGENGRAD': lng,
                'DIENSTLEISTUNGEN': ', '.join(dienstleistungen),
                'ZAHLUNGSMETHODEN': ', '.join(zahlungsmethoden),
                'BESCHREIBUNG': beschreibung,
                'BESCHREIBUNG BILD': bild_url,
                'EINFAHRTSHÖHE': einfahrtshoehe,
                'ANZAHL_PARKPLÄTZE': anzahl_parkplaetze
            })
        except Exception as e:
            print(f"Fehler beim Extrahieren von Daten für einen Parkplatz: {e}")

    driver.quit()
    return data

def insert_data_to_mysql(connection, df, table_name):
    cursor = connection.cursor()
    try:
        cursor.execute(f"CREATE TABLE IF NOT EXISTS ads.{table_name} ("
                       f"`ID` VARCHAR(255) PRIMARY KEY, "
                       f"`ART` TEXT, "
                       f"`NAME` VARCHAR(225), "
                       f"`PREIS` VARCHAR(225), "
                       f"`FREIE_PLÄTZE` VARCHAR(225), "
                       f"`PARKDAUER` VARCHAR(225), "
                       f"`BREITENGRAD` DOUBLE, "
                       f"`LAENGENGRAD` DOUBLE, "
                       f"`DIENSTLEISTUNGEN` TEXT, "
                       f"`ZAHLUNGSMETHODEN` TEXT, "
                       f"`BESCHREIBUNG` TEXT, "
                       f"`BESCHREIBUNG_BILD` TEXT, "
                       f"`EINFAHRTSHÖHE` TEXT, "
                       f"`ANZAHL_PARKPLÄTZE` INT)")

        for row in df:
            placeholders = ', '.join(['%s'] * len(row))
            query = f"INSERT INTO ads.{table_name} VALUES ({placeholders})"
            values = tuple('NULL' if val is None else val for val in row.values())  # Ersetze None durch 'NULL'
            cursor.execute(query, values)

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

def collect_data_and_store():
    mysql_credentials_file = os.path.join("config", "config_mysql_credentials.json")
    host, port, user, password, database = read_mysql_credentials(mysql_credentials_file)
    try:
        if host and port and user and password and database:
            connection = connect_to_mysql(host, port, user, password, database)
            if connection:
                data = collect_data()
                if data:
                    table_name = 'parkplatz_info'
                    insert_data_to_mysql(connection, data, table_name)
                else:
                    print("Keine Daten zum Einfügen in die Datenbank vorhanden.")
    except Exception as e:
        print("Fehler beim Sammeln und Speichern von Daten:", e)
    finally:
        if connection and connection.is_connected():
            connection.close()
            print("MySQL-Verbindung geschlossen")

if __name__ == '__main__':
    collect_data_and_store()
