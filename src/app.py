from flask import Flask, render_template
from scripts.data_collection.data_collection import collect_data
from scripts.data_preparation.data_preparation import clean_and_process_data, collect_data_and_store

app = Flask(__name__, template_folder='frontend/templates')


@app.route('/')
def index():
    return render_template('index.html')

# Daten sammeln
@app.route('/1_Daten_sammeln')
def daten_sammeln():
    data = collect_data()
    # Hier kannst du den Code einfügen, um die Daten in der Webanwendung anzuzeigen oder zu verarbeiten
    return render_template('daten_sammeln.html')

# Daten aufbereiten
@app.route('/2_Daten_aufbereiten')
def daten_aufbereiten():
    data = collect_data()
    df = clean_and_process_data(data)
    # Hier kannst du den Code einfügen, um die aufbereiteten Daten in der Webanwendung anzuzeigen oder zu verarbeiten
    return render_template('daten_aufbereiten.html')

@app.route('/3_Daten_verstehen')
def daten_verstehen():
    return render_template('daten_verstehen.html')

@app.route('/4_Daten_vorverarbeiten')
def daten_vorverarbeiten():
    return render_template('daten_vorverarbeiten.html')

@app.route('/5_Modell_trainieren')
def modell_trainieren():
    return render_template('modell_trainieren.html')

@app.route('/6_Modell_evaluieren')
def modell_evaluieren():
    return render_template('modell_evaluieren.html')

@app.route('/7_Modell_deployen')
def modell_deployen():
    return render_template('modell_deployen.html')

@app.route('/8_Diskussion&Ergebnisse')
def diskussion_ergebnisse():
    return render_template('diskussion_ergebnisse.html')

@app.route('/9_Schlussfolgerungen')
def schlussfolgerungen():
    return render_template('schlussfolgerungen.html')

def main():
    # Daten sammeln, aufbereiten und in die Datenbank einfüge
    collect_data_and_store()
    # Start der Flask-App
    app.run(debug=True)

if __name__ == '__main__':
    main()