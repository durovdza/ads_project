import requests
import json
import os

def collect_data():
    file_path = os.path.join("DS_project", "config", "config_data_sources.json")
    
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
