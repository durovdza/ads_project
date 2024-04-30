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
    
    with open('config\config_mysql_credentials.json', 'r') as f:
        template = json.load(f)
    
    # Ersetze Platzhalter in der Vorlage durch Benutzereingaben
    template.update(credentials)
    
    with open('config\config_mysql_credentials.json', 'w') as f:
        json.dump(template, f, indent=4)  # Schreibe die aktualisierten Daten zurück in die JSON-Datei

def get_openai_api_key_from_user():
    print("Bitte geben Sie den OpenAI API-Schlüssel ein:")
    
    api_key = input("OpenAI API Key: ")
    
    data = {
        "api_key": api_key
    }
    
    with open('config\config_openai_api.json', 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == '__main__':

    get_mysql_credentials_from_user()
    get_openai_api_key_from_user()