from flask import Flask, render_template, request, jsonify, send_file
import json
import os
import mysql.connector
from mysql.connector import Error
import pandas as pd
from openai import OpenAI
import sys
sys.path.append(r'C:\Users\smaie\ads_project\src\scripts\data_understanding')
from data_understanding_nlp_openai import perform_search
sys.path.append(r'C:\Users\smaie\ads_project\src\scripts\model_training')
from KNN_modell import KNN_map
sys.path.append(r'C:\Users\smaie\ads_project\src\scripts\data_understanding')
from data_understanding_map import map_generating

app = Flask(__name__, template_folder=os.path.join("src", "frontend", "templates"), static_folder=os.path.join("src", "frontend", "static"))

# Initialize OpenAI API
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

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

def load_data_from_mysql(connection, table_name, show_available, offset, limit):
    try:
        query = f"SELECT * FROM {table_name} WHERE 1=1"
        
        if show_available:
            query += " AND `FREIE_PLÄTZE` > 0"
        
        query += f" ORDER BY art ASC, id LIMIT {limit} OFFSET {offset}"
        print("Executing query:", query)  # Debugging line to print the query
        df = pd.read_sql(query, connection)
        return df
    except Error as e:
        print("Fehler beim Laden der Daten aus der MySQL-Datenbank:", e)
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/parkplaetze')
def api_parkplaetze():
    credentials_file = r'C:\Users\smaie\ads_project\config\config_mysql_credentials.json'  # Using raw string to avoid escape sequence issues
    table_name = "parkplatz_info"  # Updated with your database name

    host, port, user, password, database = read_mysql_credentials(credentials_file)
    if host and port and user and password and database:
        connection = connect_to_mysql(host, port, user, password, database)
        if connection:
            try:
                page = int(request.args.get('page', 1))
                limit = 20
                offset = (page - 1) * limit
                show_available = request.args.get('show_available') == 'true'
                df = load_data_from_mysql(connection, table_name, show_available, offset, limit)
                if df is not None:
                    return df.to_json(orient='records')
                else:
                    return jsonify({"error": "Fehler beim Laden der Daten"}), 500
            except Exception as e:
                print("Fehler bei der Datenverarbeitung:", e)
                return jsonify({"error": "Fehler bei der Datenverarbeitung"}), 500
        else:
            return jsonify({"error": "Fehler bei der Verbindung zur Datenbank"}), 500
    else:
        return jsonify({"error": "Fehler beim Lesen der Anmeldeinformationen"}), 500

@app.route('/api/search', methods=['POST'])
def api_search():
    data = request.json
    prompt = data.get('prompt')
    if not prompt:
        return jsonify({"error": "Kein Suchbegriff angegeben"}), 400

    try:
        analysis = perform_search(prompt)
        return jsonify({"analysis": analysis})
    except Exception as e:
        print("Fehler bei der Verarbeitung der Suchanfrage:", e)
        return jsonify({"error": "Fehler bei der Verarbeitung der Suchanfrage"}), 500

@app.route('/karte')
def karte():
    map_generating
    try:
        return send_file(r'C:\Users\smaie\ads_project\src\scripts\data_understanding\map.html')
    except Exception as e:
        print("Fehler beim Senden der Datei:", e)
        return jsonify({"error": "Fehler beim Senden der Datei"}), 500

@app.route('/knn_karte', methods=['POST'])
def knn_karte():
    KNN_map()
    data = request.json
    adresse = data.get('adresse')
    if not adresse:
        return jsonify({"error": "Adresse nicht angegeben"}), 400

    try:
        geo_data = {"adresse": adresse}
        return send_file(r'C:\Users\smaie\ads_project\src\scripts\model_training\KNN_map.html')
    except Exception as e:
        print("Fehler beim Senden der KNN-Karte:", e)
        return jsonify({"error": "Fehler beim Senden der KNN-Karte"}), 500

if __name__ == '__main__':
    app.run(debug=True)
