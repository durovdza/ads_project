from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/1_Daten_sammeln')
def daten_sammeln():
    return render_template('daten_sammeln.html')

@app.route('/2_Daten_aufbereiten')
def daten_aufbereiten():
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

if __name__ == '__main__':
    app.run(debug=True)
