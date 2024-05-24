from flask import Flask, render_template, request, jsonify, send_file
import subprocess
import json
import os
import mysql.connector

app = Flask(__name__, template_folder=os.path.join("src", "frontend", "templates"), static_folder=os.path.join("src", "frontend", "static"))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/parkplaetze')
def api_parkplaetze():
    return jsonify([
        {"ID": "1", "NAME": "Parkplatz A", "ADRESSE": "Adresse A", "FREIE PLÄTZE": "5", "PREIS": "2 CHF/h", "PARKDAUER": 24, "BREITENGRAD": 47.3769, "LAENGENGRAD": 8.5417},
        {"ID": "2", "NAME": "Parkplatz B", "ADRESSE": "Adresse B", "FREIE PLÄTZE": "10", "PREIS": "1.5 CHF/h", "PARKDAUER": 12, "BREITENGRAD": 47.3768, "LAENGENGRAD": 8.5416},
    ])

@app.route('/karte')
def karte():
    #script_path = os.path.join("src", "scripts", "data_understanding", "karte_erstellen.py")
    #try:
    #    subprocess.run(['python', script_path], check=True)
    #except subprocess.CalledProcessError as e:
    #    return f"Error: {e.stderr}", 500
    return send_file(os.path.join("src", "scripts", "data_understanding", "map.html"))

@app.route('/knn_karte', methods=['POST'])
def knn_karte():
    data = request.json
    adresse = data.get('adresse')
    if not adresse:
        return jsonify({"error": "Adresse nicht angegeben"}), 400

    geo_data = {"adresse": adresse}
    #with open(os.path.join("src", "scripts", "model_training", "data.json"), 'w') as f:
    #    json.dump(geo_data, f)

    #script_path = os.path.join("src", "scripts", "model_training", "KNN_modell.py")
    #try:
    #    subprocess.run(['python', script_path], check=True)
    #except subprocess.CalledProcessError as e:
    #    return f"Error: {e.stderr}", 500
    return send_file(os.path.join("src", "scripts", "model_training", "nearest_parkings_map.html"))

if __name__ == '__main__':
    app.run(debug=True)
