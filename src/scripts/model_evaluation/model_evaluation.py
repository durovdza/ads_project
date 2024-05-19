import pandas as pd
import mysql.connector
from mysql.connector import Error
import json
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt

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

def read_data_from_mysql(connection, query):
    try:
        data = pd.read_sql(query, connection)
        return data
    except Exception as e:
        print(f"Fehler beim Lesen der Daten aus der MySQL-Datenbank: {e}")
        return None

def train_and_evaluate_model(X_train, X_test, y_train, y_test):
    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    return model, y_pred

def calculate_metrics(y_true, y_pred):
    r2 = r2_score(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    return r2, mae, mse

def plot_results(y_true, y_pred):
    plt.scatter(y_true, y_pred)
    plt.xlabel("Actual Values")
    plt.ylabel("Predicted Values")
    plt.title("Actual vs. Predicted Values")
    plt.show()

def main():
    mysql_credentials_file = os.path.join("config", "config_mysql_credentials.json")
    host, port, user, password, database = read_mysql_credentials(mysql_credentials_file)
    if host and port and user and password and database:
        connection = connect_to_mysql(host, port, user, password, database)
        if connection:
            query = "SELECT * FROM parkplatz_info"
            data = read_data_from_mysql(connection, query)
            if data is not None:
                # Annahme: Sie haben bereits eine Tabelle "parkplatz_info" mit den benötigten Daten in Ihrer MySQL-Datenbank

                # Abhängig von Ihrer Datenstruktur und Ihrem Modell müssen Sie möglicherweise Ihre Features und Zielvariablen auswählen
                X = data.drop(columns=['ZIELVARIABLE'])  # Features
                y = data['ZIELVARIABLE']  # Zielvariable

                # Teilen Sie die Daten in Trainings- und Testsets auf
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

                # Trainieren und evaluieren Sie das Modell
                model, y_pred = train_and_evaluate_model(X_train, X_test, y_train, y_test)

                # Berechnen Sie die Modellmetriken
                r2, mae, mse = calculate_metrics(y_test, y_pred)
                print("R^2 Score:", r2)
                print("Mean Absolute Error:", mae)
                print("Mean Squared Error:", mse)

                # Visualisieren Sie die Ergebnisse
                plot_results(y_test, y_pred)

            # Schließen Sie die Verbindung
            connection.close()
    else:
        print(f"Konfigurationsdatei nicht gefunden")

if __name__ == "__main__":
    main()
