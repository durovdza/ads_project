import requests
import csv
import io
import os
import json

def collect_data():
    file_path = os.path.join("config", "config_data_sources.json")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        
    collected_data = {}
    for source, info in data.items():
        url = info['url']
        response = requests.get(url)
        print(f"Response status code from {source}: {response.status_code}")
        if response.status_code == 200:
            try:
                # Verarbeiten Sie CSV-Daten
                csv_data = response.content.decode('utf-8')
                csv_reader = csv.DictReader(io.StringIO(csv_data))
                collected_data[source] = [row for row in csv_reader]
            except Exception as e:
                print(f"Fehler beim Verarbeiten von CSV-Daten von {source}: {e}")
        else:
            print(f"Fehler beim Abrufen der Daten von {source}: {response.status_code}")
    
    return collected_data

# Testen Sie Ihre Funktion
collected_data = collect_data()
print(collected_data)  # Ausgabe der gesammelten Daten zur Überprüfung
