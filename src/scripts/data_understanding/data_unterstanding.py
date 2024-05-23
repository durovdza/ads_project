import mysql.connector
import pandas as pd
from mysql.connector import Error
import json
import os
import folium
from folium.plugins import MarkerCluster
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

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

def load_data_from_mysql(connection, table_name, limit, offset):
    try:
        query = f"SELECT * FROM {table_name} LIMIT {limit} OFFSET {offset}"
        df = pd.read_sql(query, connection)
        return df
    except Error as e:
        print("Fehler beim Laden der Daten aus der MySQL-Datenbank:", e)
        return None

def explore_data(df):
    print("Erste 5 Zeilen des DataFrames:")
    print(df.head())
    
    print("\nInfo über den DataFrame:")
    print(df.info())

    print("\nStatistische Zusammenfassung des DataFrames:")
    print(df.describe(include='all'))

def create_map(df):
    latitude = df['BREITENGRAD'].mean()
    longitude = df['LAENGENGRAD'].mean()
    map = folium.Map(location=[latitude, longitude], zoom_start=10)

    marker_cluster = MarkerCluster().add_to(map)
    
    for index, row in df.iterrows():
        folium.Marker([row['BREITENGRAD'], row['LAENGENGRAD']]).add_to(marker_cluster)
    
    return map

def visualize_distribution(df):
    numerical_columns = ['PREIS', 'FREIE_PLÄTZE', 'PARKDAUER', 'EINFAHRTSHÖHE', 'ANZAHL_PARKPLÄTZE']
    for column in numerical_columns:
        plt.figure(figsize=(8, 6))
        sns.histplot(df[column], bins=20, kde=True)
        plt.title(f'{column} Verteilung')
        plt.xlabel(column)
        plt.ylabel('Häufigkeit')
        plt.show()

def text_analysis(df, column):
    if column in df.columns:
        print(f"Textanalyse für Spalte '{column}':")
        print(df[column].describe())
        # Weitere Textanalysen könnten hier durchgeführt werden

def cluster_analysis(df):
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df[['BREITENGRAD', 'LAENGENGRAD']])
    kmeans = KMeans(n_clusters=3)
    df['Cluster'] = kmeans.fit_predict(scaled_data)
    plt.figure(figsize=(8, 6))
    sns.scatterplot(data=df, x='BREITENGRAD', y='LAENGENGRAD', hue='Cluster', palette='viridis', legend='full')
    plt.title('Clusteranalyse der geografischen Daten')
    plt.xlabel('Breitengrad')
    plt.ylabel('Längengrad')
    plt.show()

def image_analysis(df, column):
    if column in df.columns:
        # Hier könnten Bildanalysen durchgeführt werden, falls erforderlich
        pass

if __name__ == '__main__':
    mysql_credentials_file = os.path.join("config", "config_mysql_credentials.json")
    host, port, user, password, database = read_mysql_credentials(mysql_credentials_file)
    if host and port and user and password and database:
        connection = connect_to_mysql(host, port, user, password, database)
        if connection:
            table_name = 'parkplatz_info'
            limit = 50
            offset = 0
            all_data = []

            while True:
                df = load_data_from_mysql(connection, table_name, limit, offset)
                if df is None or df.empty:
                    break
                all_data.append(df)
                offset += limit

            if all_data:
                combined_df = pd.concat(all_data, ignore_index=True)
                explore_data(combined_df)
                visualize_distribution(combined_df)
                for column in ['ART', 'NAME', 'DIENSTLEISTUNGEN', 'ZAHLUNGSMETHODEN', 'BESCHREIBUNG']:
                    text_analysis(combined_df, column)
                cluster_analysis(combined_df)
                for column in ['BESCHREIBUNG_BILD']:
                    image_analysis(combined_df, column)
                map = create_map(combined_df)
                map.save("map.html")
                print("Karte erstellt und als 'map.html' gespeichert.")
            else:
                print("Keine Daten geladen.")
                
            connection.close()
