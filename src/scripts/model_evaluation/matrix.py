import pandas as pd
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, accuracy_score, precision_score, recall_score, f1_score
import matplotlib.pyplot as plt

# Daten einlesen
data = {
    'Nummer': [
        1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 6, 6, 6, 6, 6
    ],
    'Adresse': [
        'Bahnhofstrasse 1, 8001 Zürich, Schweiz', 'Bahnhofstrasse 1, 8001 Zürich, Schweiz',
        'Bahnhofstrasse 1, 8001 Zürich, Schweiz', 'Bahnhofstrasse 1, 8001 Zürich, Schweiz',
        'Bahnhofstrasse 1, 8001 Zürich, Schweiz', 'Löwenstrasse 15, 8001 Zürich, Schweiz',
        'Löwenstrasse 15, 8001 Zürich, Schweiz', 'Löwenstrasse 15, 8001 Zürich, Schweiz',
        'Löwenstrasse 15, 8001 Zürich, Schweiz', 'Löwenstrasse 15, 8001 Zürich, Schweiz',
        'Limmatquai 52, 8001 Zürich, Schweiz', 'Limmatquai 52, 8001 Zürich, Schweiz',
        'Limmatquai 52, 8001 Zürich, Schweiz', 'Limmatquai 52, 8001 Zürich, Schweiz',
        'Limmatquai 52, 8001 Zürich, Schweiz', 'Seefeldstrasse 45, 8008 Zürich, Schweiz',
        'Seefeldstrasse 45, 8008 Zürich, Schweiz', 'Seefeldstrasse 45, 8008 Zürich, Schweiz',
        'Seefeldstrasse 45, 8008 Zürich, Schweiz', 'Seefeldstrasse 45, 8008 Zürich, Schweiz',
        'Uraniastrasse 9, 8001 Zürich, Schweiz', 'Uraniastrasse 9, 8001 Zürich, Schweiz',
        'Uraniastrasse 9, 8001 Zürich, Schweiz', 'Uraniastrasse 9, 8001 Zürich, Schweiz',
        'Uraniastrasse 9, 8001 Zürich, Schweiz'
    ],
    'Latitude': [
        47.367194, 47.368535, 47.366766, 47.371174, 47.370639, 47.353687, 47.354591, 47.356532, 47.354357, 47.361218,
        47.368535, 47.368007, 47.374123, 47.371174, 47.374539, 47.361447, 47.366329, 47.365298, 47.367069, 47.368139,
        47.374123, 47.374539, 47.375021, 47.376561, 47.375961
    ],
    'Longitude': [
        8.539930, 8.540993, 8.537401, 8.539456, 8.537715, 8.601819, 8.601895, 8.601032, 8.598604, 8.601002,
        8.540993, 8.544763, 8.540614, 8.539456, 8.540965, 8.554246, 8.552265, 8.553745, 8.547935, 8.549759,
        8.540614, 8.540965, 8.537212, 8.538668, 8.541179
    ],
    'Count': [
        3, 335, 168, 7, 47, 7, 16, 118, 39, 37, 335, 6, 1, 7, 20, 86, 25, 10, 1, 55, 1, 20, 10, 19, 71
    ],
    'Ergebnis Opensource': [
        'Korrekt', 'FALSCH', 'FALSCH', 'FALSCH', 'FALSCH', 'FALSCH', 'FALSCH', 'FALSCH', 'FALSCH', 'FALSCH',
        'FALSCH', 'Korrekt', 'Korrekt', 'Korrekt', 'Korrekt', 'Korrekt', 'FALSCH', 'FALSCH', 'FALSCH', 'FALSCH',
        'Korrekt', 'Korrekt', 'FALSCH', 'FALSCH', 'FALSCH'
    ]
}

df = pd.DataFrame(data)

# True Labels und Predicted Labels erstellen
true_labels = df['Ergebnis Opensource'].apply(lambda x: 1 if x == 'Korrekt' else 0)
predicted_labels = df['Count'].apply(lambda x: 1 if x <= 10 else 0) # Beispiel für eine Vorhersage

# Confusion Matrix berechnen
cm = confusion_matrix(true_labels, predicted_labels)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['FALSCH', 'Korrekt'])

# Confusion Matrix anzeigen
disp.plot()
plt.show()

# Berechnung der Gütemaße
accuracy = accuracy_score(true_labels, predicted_labels)
precision = precision_score(true_labels, predicted_labels)
recall = recall_score(true_labels, predicted_labels)
f1 = f1_score(true_labels, predicted_labels)

# Ausgabe der Gütemaße
print(f'Accuracy: {accuracy:.2f}')
print(f'Precision: {precision:.2f}')
print(f'Recall: {recall:.2f}')
print(f'F1-Score: {f1:.2f}')
