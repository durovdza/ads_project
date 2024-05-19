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


if __name__ == '__main__':
    get_mysql_credentials_from_user()
