import mysql.connector
import pandas as pd

def fetch_data_from_mysql():
    # Verbindungsdaten (Beispiel - ersetze diese mit deinen echten Daten)
    config = {
        'user': 'root',
        'password': 'password',
        'host': '127.0.0.1',
        'database': 'ads_database',
        'raise_on_warnings': True
    }
    
    try:
        conn = mysql.connector.connect(**config)
        query = "SELECT * FROM ads_database"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Fehler beim Abrufen der Daten: {e}")
        return pd.DataFrame()

# Daten für das Modelltraining abrufen
data = fetch_data_from_mysql()
