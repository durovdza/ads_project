import requests
import mysql.connector

# API-Endpunkte der Stadt Zürich
search_url = 'https://data.stadt-zuerich.ch/api/3/action/datastore_search'

# Payload für die Abfrage
payload = {
    'resource_id': 'YOUR_RESOURCE_ID',  # ID der Ressource, die du abfragen möchtest
    'limit': 100  # Anzahl der Datensätze, die du abrufen möchtest
}

# Header für die Anfrage (falls erforderlich)
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer YOUR_ACCESS_TOKEN'  # Falls benötigt
}

# Funktion zum Abrufen und Verarbeiten der Daten
def fetch_and_process_data():
    response = requests.get(search_url, params=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()['result']['records']  # Extrahiere die Datensätze aus der Antwort
        return data
    else:
        print("Fehler beim Abrufen der Daten:", response.status_code)
        return None

# Funktion zum Einfügen von Daten in die MySQL-Datenbank
def insert_into_mysql(data):
    try:
        connection = mysql.connector.connect(
            host='YOUR_HOST',
            user='YOUR_USERNAME',
            password='YOUR_PASSWORD',
            database='YOUR_DATABASE'
        )

        cursor = connection.cursor()

        # Beispiel: Einfügen von Daten in eine Tabelle namens 'example_table'
        for record in data:
            # Annahme: Die Struktur der Daten entspricht der Struktur der Tabelle
            query = "INSERT INTO example_table (column1, column2, column3) VALUES (%s, %s, %s)"
            values = (record['field1'], record['field2'], record['field3'])
            cursor.execute(query, values)

        connection.commit()
        print("Daten erfolgreich in MySQL-Datenbank eingefügt")

    except Exception as e:
        print("Fehler beim Einfügen der Daten in die MySQL-Datenbank:", e)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Hauptfunktionsaufruf
def main():
    data = fetch_and_process_data()
    if data:
        insert_into_mysql(data)

if __name__ == "__main__":
    main()
