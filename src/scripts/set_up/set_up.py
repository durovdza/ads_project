import os
import json

def get_mysql_credentials_from_user():
    host = input("MySQL Host: ")
    port = input("Port: ")
    user = input("MySQL User: ")
    password = input("MySQL Password: ")
    database = input("MySQL Database: ")
    
    credentials = {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "database": database
    }
    
    file_path = os.path.join("config", "config_mysql_credentials.json")
    with open(file_path, 'r') as f:
        template = json.load(f)
    
    # Ersetze Platzhalter in der Vorlage durch Benutzereingaben
    template.update(credentials)
    
    with open(file_path, 'w') as f:
        json.dump(template, f, indent=4)  # Schreibe die aktualisierten Daten zurück in die JSON-Datei

def get_openai_api_key_from_user():
    print("Bitte geben Sie den OpenAI API-Schlüssel ein:")
    
    api_key = input("OpenAI API Key: ")
    
    data = {
        "api_key": api_key
    }
    
    file_path = os.path.join("config", "config_openai_api.json")
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def get_mapbox_key_from_user():
    print("Bitte geben Sie den Mapbox API-Schlüssel ein:")
    
    api_key = input("Mapbox API Key: ")
    
    data = {
        "api_key": api_key
    }
    
    file_path = os.path.join("config", "config_mapbox_api.json")
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == '__main__':
    get_mysql_credentials_from_user()
    get_openai_api_key_from_user()