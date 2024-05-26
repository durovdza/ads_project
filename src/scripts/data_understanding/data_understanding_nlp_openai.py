import os
import json
import mysql.connector
from mysql.connector import Error
from openai import OpenAI
import pandas as pd

# OpenAI API initialisieren
client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

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

def ask_chatgpt(prompt, data):
    messages = [
        {"role": "system", "content": "Du bist ein Datenanalyst. Analysiere die folgende Datenbank."},
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": f"Hier sind die Daten der Parkhäuser: {data}"}
    ]
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    content = completion.choices[0].message.content
    return content

def perform_search(prompt):
    # Lese die MySQL-Anmeldedaten
    mysql_credentials_file = r'C:\Users\smaie\ads_project\config\config_mysql_credentials.json'
    host, port, user, password, database = read_mysql_credentials(mysql_credentials_file)    

    # Verbinde zur MySQL-Datenbank
    connection = connect_to_mysql(host, port, user, password, database)

    if connection:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM parkplatz_info WHERE ART = 'Parkhaus'"
        cursor.execute(query)
        parkplaetze = cursor.fetchall()

        if parkplaetze:
            # Wandeln die Daten in einen DataFrame um
            df = pd.DataFrame(parkplaetze)
            data_json = df.to_json(orient='records')
            
            # Sende den Prompt und die Daten an OpenAI
            analysis = ask_chatgpt(prompt, data_json)

            cursor.close()
            connection.close()

            return analysis
        else:
            cursor.close()
            connection.close()
            return "Keine Parkhäuser gefunden."
    else:
        return "Keine Verbindung zur Datenbank möglich."
