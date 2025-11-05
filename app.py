from flask import Flask, render_template, request, redirect, url_for, flash
from models import BotiquinDB
from factory import MedicamentoFactory
from events import EventManager

app = Flask(__name__)
app.secret_key = "botiquin_inteligente_key"

# Inicializamos los componentes (Singletons)
db = BotiquinDB.get_instance()
event_manager = EventManager()

# Evento para verificar niveles bajos de medicamento
def on_medicamento_actualizado(medicamento):
    if medicamento["cantidad_restante"] <= 2:
        print(f"⚠️ Alerta: {medicamento['nombre']} está por agotarse ({medicamento['cantidad_restante']} unidades restantes)")

# Suscribir el evento
event_manager.subscribe("medicamento_actualizado", on_medicamento_actualizado)

@app.route("/")
def index():
    medicamentos = db.obtener_todos()
    return render_template("index.html", medicamentos=medicamentos)

@app.route("/agregar", methods=["POST"])
def agregar():
    nombre = request.form["nombre"]
    cantidad_total = int(request.form["cantidad_total"])
    consumo_diario = int(request.form["consumo_diario"])

    # Creamos medicamento mediante Factory
    factory = MedicamentoFactory()
    medicamento = factory.crear_medicamento(nombre, cantidad_total, consumo_diario)

    db.agregar_medicamento(medicamento)
    event_manager.emit("medicamento_actualizado", medicamento)
    flash("Medicamento agregado correctamente", "success")
    return redirect(url_for("index"))

@app.route("/consumir/<nombre>", methods=["POST"])
def consumir(nombre):
    medicamento = db.obtener_por_nombre(nombre)
    if medicamento:
        medicamento["cantidad_restante"] -= medicamento["consumo_diario"]
        if medicamento["cantidad_restante"] < 0:
            medicamento["cantidad_restante"] = 0
        event_manager.emit("medicamento_actualizado", medicamento)
        flash(f"Se registró el consumo diario de {nombre}.", "info")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
