from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

# Ein einfaches künstliches neuronales Netzwerk
model = Sequential([
    Dense(64, activation='relu', input_shape=(X_train.shape[1],)),
    Dense(32, activation='relu'),
    Dense(1, activation='sigmoid')  # Annahme: binäre Klassifikation
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model.fit(X_train, y_train, epochs=10, batch_size=32, validation_split=0.2)

# Modell bewerten
loss, accuracy = model.evaluate(X_test, y_test)
print(f'Genauigkeit des Modells: {accuracy:.2f}')
