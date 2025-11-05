from database import Database
from werkzeug.security import generate_password_hash, check_password_hash

db_instance = Database.get_instance()
db = db_instance.db

class Usuario(db.Model):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    contraseña_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, contraseña):
        self.contraseña_hash = generate_password_hash(contraseña)

    def check_password(self, contraseña):
        return check_password_hash(self.contraseña_hash, contraseña)


class Medicamento(db.Model):
    __tablename__ = "medicamentos"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    cantidad_total = db.Column(db.Integer, nullable=False)
    consumo_diario = db.Column(db.Integer, nullable=False)
    cantidad_restante = db.Column(db.Integer, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)  # ← relación con usuario

    usuario = db.relationship("Usuario", backref=db.backref("medicamentos", lazy=True))

    def __repr__(self):
        return f"<Medicamento {self.nombre}>"


