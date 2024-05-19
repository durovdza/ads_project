import mysql.connector
from mysql.connector import Error
import pandas as pd
import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords

# Funktion zur Herstellung einer Verbindung zur MySQL-Datenbank
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

# Funktion zum Lesen der MySQL-Anmeldeinformationen aus einer JSON-Datei
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

# Daten aus der Datenbank lesen und in einen DataFrame laden
def read_data_from_mysql(connection):
    try:
        query = "SELECT ID, NAME, BESCHREIBUNG FROM parkplatz_info"
        df = pd.read_sql(query, connection)
        return df
    except Error as e:
        print("Fehler beim Laden der Daten aus der MySQL-Datenbank:", e)
        return None

# Content-based Recommender-System erstellen
def content_based_recommender(df):
    # Deutsche Stoppwörter laden
    nltk.download('stopwords')
    german_stop_words = stopwords.words('german')
    
    # TF-IDF Vektorisierung der relevanten Textmerkmale
    tfidf_vectorizer = TfidfVectorizer(stop_words=german_stop_words)
    tfidf_matrix = tfidf_vectorizer.fit_transform(df['BESCHREIBUNG'])

    # Berechnung der Kosinus-Ähnlichkeit zwischen den Parkplätzen
    similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

    return similarity_matrix

# Empfehlungen für einen gegebenen Parkplatz generieren
def generate_recommendations(similarity_matrix, parkplatz_id, df, num_recommendations=5):
    parkplatz_index = df[df['ID'] == parkplatz_id].index
    if len(parkplatz_index) == 0:
        print("Die angegebene Parkplatz-ID wurde nicht in der DataFrame gefunden.")
        return None

    parkplatz_index = parkplatz_index[0]

    # Ähnlichkeiten des aktuellen Parkplatzes zu anderen Parkplätzen
    similar_parkplatz_indices = similarity_matrix[parkplatz_index].argsort()[::-1][1:num_recommendations+1]

    # Empfohlene Parkplätze
    recommendations = df.iloc[similar_parkplatz_indices]

    return recommendations

if __name__ == '__main__':
    # Pfad zur JSON-Datei mit MySQL-Anmeldeinformationen
    mysql_credentials_file = os.path.join("config", "config_mysql_credentials.json")

    # MySQL-Anmeldeinformationen aus der JSON-Datei lesen
    host, port, user, password, database = read_mysql_credentials(mysql_credentials_file)
    if host and port and user and password and database:
        # Verbindung zur MySQL-Datenbank herstellen
        connection = connect_to_mysql(host, port, user, password, database)
        if connection:
            # Daten aus der Datenbank lesen
            df = read_data_from_mysql(connection)
            if df is not None:
                print("Daten erfolgreich aus der Datenbank geladen:")
                print(df.head())

                # Content-based Recommender-System erstellen
                similarity_matrix = content_based_recommender(df)

                # Beispielhaft Empfehlungen generieren
                parkplatz_id = 'PH1024'
                print("Empfohlene Parkplätze für", df[df['ID'] == parkplatz_id]['NAME'].values[0])
                recommendations = generate_recommendations(similarity_matrix, parkplatz_id, df)
                if recommendations is not None:
                    print(recommendations[['ID', 'NAME']])

            # Verbindung schließen
            connection.close()
    else:
        print("Fehler beim Lesen der MySQL-Anmeldeinformationen aus der JSON-Datei.")
