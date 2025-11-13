from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_migrate import Migrate
from config import Config
from database import Database
from models import db, Medicamento, Usuario
from factory import MedicamentoFactory
from events import EventManager
from botiquin_facade import BotiquinFacade
from decorators import AlertaDecorator, RegistroDecorator


app = Flask(__name__)
app.config.from_object(Config)

# Inicialización de la base de datos
db_instance = Database.get_instance()
db_instance.db.init_app(app)
migrate = Migrate(app, db_instance.db)

event_manager = EventManager()
botequin = BotiquinFacade()

# Lista para almacenar alertas
alertas = []

# Evento de alerta
def alerta_stock_bajo(medicamento):
    if medicamento.cantidad_restante <= 2:
        alertas.append(f"⚠️ Stock bajo: {medicamento.nombre} tiene solo {medicamento.cantidad_restante} unidades")

event_manager.subscribe("medicamento_agregado", alerta_stock_bajo)
event_manager.subscribe("medicamento_actualizado", alerta_stock_bajo)


# --- Rutas de autenticación ---
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["nombre"]
        contraseña = request.form["contraseña"]

        if Usuario.query.filter_by(nombre=nombre).first():
            flash("El usuario ya existe", "danger")
            return redirect(url_for("registro"))

        nuevo_usuario = Usuario(nombre=nombre)
        nuevo_usuario.set_password(contraseña)

        db.session.add(nuevo_usuario)
        db.session.commit()
        event_manager.sesion("usuario_creado", {"usuario": nombre})
        flash("Usuario registrado correctamente. Inicia sesión.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nombre = request.form["nombre"]
        contraseña = request.form["contraseña"]

        usuario = Usuario.query.filter_by(nombre=nombre).first()

        if usuario and usuario.check_password(contraseña):
            session["usuario"] = usuario.nombre
            event_manager.emit("inicio_sesion", {"usuario": nombre})
            flash("Inicio de sesión exitoso", "success")
            return redirect(url_for("index"))
        else:
            flash("Credenciales incorrectas", "danger")
            return redirect(url_for("login"))
        
    return render_template("login.html")



@app.route("/logout")
def logout():
    session.pop("usuario", None)
    event_manager.emit("cierre_sesion", {"usuario": session.get("usuario", "Invitado")})
    flash("Sesión cerrada correctamente", "info")
    return redirect(url_for("login"))



# --- Rutas protegidas ---
def login_requerido(func):
    def wrapper(*args, **kwargs):
        if "usuario" not in session:
            flash("Debes iniciar sesión para acceder.", "warning")
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


@app.route("/")
@login_requerido
def index():
    usuario_actual = Usuario.query.filter_by(nombre=session["usuario"]).first()
    medicamentos = Medicamento.query.filter_by(usuario_id=usuario_actual.id).all()

    # Filtrar alertas solo de este usuario
    # obtener una copia de las alertas antes de limpiarlas
    alertas_usuario = list(alertas)
    alertas.clear()
    return render_template("index.html", medicamentos=medicamentos, usuario=session["usuario"], alertas=alertas_usuario)

@app.route("/agregar", methods=["POST"])
@login_requerido
def agregar():
    nombre = request.form["nombre"]
    cantidad_total = int(request.form["cantidad_total"])
    consumo_diario = int(request.form["consumo_diario"])
    tipo = request.form["tipo"]

    usuario_actual = Usuario.query.filter_by(nombre=session["usuario"]).first()
    botequin.agregar_medicamento(usuario_actual, nombre, cantidad_total, consumo_diario, tipo)
    flash("Medicamento agregado correctamente", "success")
    return redirect(url_for("index"))



@app.route("/consumir/<int:id>", methods=["POST"])
@login_requerido
def consumir(id):
    medicamento = Medicamento.query.get(id)
    if medicamento:
        medicamento.cantidad_restante -= medicamento.consumo_diario
        if medicamento.cantidad_restante < 0:
            medicamento.cantidad_restante = 0
        db.session.commit()

        event_manager.emit("medicamento_consumido", {"nombre": medicamento.nombre, "restante": medicamento.cantidad_restante})
        flash(f"Se registró el consumo de {medicamento.nombre}.", "info")

    return redirect(url_for("index"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
