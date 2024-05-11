from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# Angenommen, 'data' enthält die Spalten 'average_salary' und 'political_orientation'
X = data[['average_salary']]
y = data['political_orientation']

# Daten aufteilen
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Modell initialisieren und trainieren
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Vorhersagen treffen und bewerten
predictions = model.predict(X_test)
print(classification_report(y_test, predictions))
