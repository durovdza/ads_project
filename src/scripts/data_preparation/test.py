import pandas as pd

# Pfad zur CSV-Datei
csv_file_path = "C:\\Users\\smaie\\Downloads\\96f68393-152b-11ef-b380-005056b0ce82\\data\\taz.view_pp_ogd.csv"

# CSV-Datei einlesen
df = pd.read_csv(csv_file_path)

# Die ersten paar Zeilen des DataFrame anzeigen
print(df.head())