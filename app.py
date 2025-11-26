from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_migrate import Migrate
from config import Config
from database import Database
from models import db, Medicamento, Usuario
from factory import MedicamentoFactory
from events import EventManager
from botiquin_facade import BotiquinFacade
from decorators import AlertaDecorator, RegistroDecorator, ProyeccionDecorator
from reportes_cqrs import MedicamentoQueryService, MedicamentoCommandService
import pusher

app = Flask(__name__)
app.config.from_object(Config)

# Inicialización de la base de datos
db_instance = Database.get_instance()
db_instance.db.init_app(app)
migrate = Migrate(app, db_instance.db)

event_manager = EventManager()
botequin = BotiquinFacade()
queries = MedicamentoQueryService()
commands = MedicamentoCommandService()

pusher_client = pusher.Pusher(
    app_id='2077108',
    key='918819e46056d1579079',
    secret='49cada5ca34511e202ff',
    cluster='us2',
    ssl=True
)

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
        event_manager.emit("usuario_creado", {"usuario": nombre})
        flash("Usuario registrado correctamente. Inicia sesión.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

def obtener_usuario_actual():
    if "usuario" not in session:
        return None
    return Usuario.query.filter_by(nombre=session["usuario"]).first()

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
    event_manager.emit("cierre_sesion", {"usuario": session.get("usuario", "Invitado")})
    session.pop("usuario", None)
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

    medicamentos_query = Medicamento.query.filter_by(usuario_id=usuario_actual.id).all()

    alertas_usuario = [
        alerta for alerta in botequin.alertas
        if any(med.nombre in alerta for med in medicamentos_query)
    ]

    medicamentos = []
    for m in medicamentos_query:
        dec = ProyeccionDecorator(m)
        medicamentos.append({
            "id": m.id,
            "nombre": m.nombre,
            "tipo": m.tipo,
            "cantidad_total": m.cantidad_total,
            "consumo_diario": m.consumo_diario,
            "cantidad_restante": m.cantidad_restante,
            "fecha_fin": dec.calcular_fecha_fin()
        })

    return render_template(
        "index.html",
        medicamentos=medicamentos,
        usuario=session["usuario"],
        alertas=alertas_usuario
    )




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


@app.route("/reportes")
@login_requerido
def reportes():
    usuario = Usuario.query.filter_by(nombre=session["usuario"]).first()
    datos = queries.obtener_proyecciones_usuario(usuario.id)
    return render_template("reportes.html", datos=datos)


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

@app.route("/eliminar/<int:medicamento_id>", methods=["POST"])
@login_requerido
def eliminar_medicamento(medicamento_id):
    usuario = obtener_usuario_actual()
    exito = botequin.eliminar_medicamento(medicamento_id, usuario)

    if exito:
        flash("Medicamento eliminado correctamente", "success")
    else:
        flash("No se pudo eliminar el medicamento", "danger")

    return redirect(url_for("index"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
