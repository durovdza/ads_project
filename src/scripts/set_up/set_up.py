import json
import subprocess
import sys

def create_and_activate_virtualenv():
    try:
        # Erstelle die virtuelle Umgebung
        subprocess.check_call([sys.executable, '-m', 'venv', 'venv'])
        print("Virtuelle Umgebung erfolgreich erstellt.")

        # Aktiviere die virtuelle Umgebung (abhängig vom Betriebssystem)
        if sys.platform.startswith('win'):
            subprocess.check_call(['venv\\Scripts\\activate'], shell=True)
        else:
            subprocess.check_call(['source', 'venv/bin/activate'], shell=True)
        
        print("Virtuelle Umgebung erfolgreich aktiviert.")
    except subprocess.CalledProcessError:
        print("Fehler beim Erstellen oder Aktivieren der virtuellen Umgebung.")

def install_requirements():
    try:
        subprocess.check_call(['pip', 'install', '-r', 'DS_project/requirements.txt'])
        print("Abhängigkeiten erfolgreich installiert.")
    except subprocess.CalledProcessError:
        print("Fehler beim Installieren der Abhängigkeiten.")

def get_mysql_credentials_from_user():
    host = input("MySQL Host: ")
    port = input("Port (default 3306): ") or "3306"
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
    
    with open('DS_project/config/config_mysql_credentials.json', 'r') as f:
        template = json.load(f)
    
    # Ersetze Platzhalter in der Vorlage durch Benutzereingaben
    template.update(credentials)
    
    with open('DS_project/config/config_mysql_credentials.json', 'w') as f:
        json.dump(template, f, indent=4)  # Schreibe die aktualisierten Daten zurück in die JSON-Datei

def get_openai_api_key_from_user():
    print("Bitte geben Sie den OpenAI API-Schlüssel ein:")
    
    api_key = input("OpenAI API Key: ")
    
    data = {
        "api_key": api_key
    }
    
    with open('DS_project/config/config_openai_api.json', 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == '__main__':
    create_and_activate_virtualenv()
    install_requirements()
    get_mysql_credentials_from_user()
    get_openai_api_key_from_user()