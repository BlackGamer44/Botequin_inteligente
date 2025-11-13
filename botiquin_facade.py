# botiquin_facade.py
from models import Medicamento, db
from factory import MedicamentoFactory
from events import EventManager

class BotiquinFacade:
    def __init__(self):
        self.event_manager = EventManager()
        self.factory = MedicamentoFactory()
        self.alertas = []  # ← aquí guardaremos los mensajes

        self.event_manager.subscribe("medicamento_agregado", self.alerta_stock_bajo)
        self.event_manager.subscribe("medicamento_actualizado", self.alerta_stock_bajo)

    def alerta_stock_bajo(self, medicamento):
        if medicamento.cantidad_restante <= 2:
            mensaje = f"⚠️ El medicamento '{medicamento.nombre}' está por agotarse ({medicamento.cantidad_restante} unidades restantes)."
            print(mensaje)
            self.alertas.append(mensaje)  # ← guardar alerta

    def agregar_medicamento(self, usuario, nombre, cantidad_total, consumo_diario, tipo):
        nuevo = self.factory.crear_medicamento(nombre, cantidad_total, consumo_diario, tipo)
        nuevo.usuario_id = usuario.id
        db.session.add(nuevo)
        db.session.commit()
        self.event_manager.emit("medicamento_agregado", nuevo)
        return nuevo

    def consumir_medicamento(self, medicamento_id):
        medicamento = Medicamento.query.get(medicamento_id)
        if medicamento:
            medicamento.cantidad_restante -= medicamento.consumo_diario
            if medicamento.cantidad_restante < 0:
                medicamento.cantidad_restante = 0
            db.session.commit()
            self.event_manager.emit("medicamento_actualizado", medicamento)
        return medicamento

    def obtener_medicamentos_usuario(self, usuario):
        return Medicamento.query.filter_by(usuario_id=usuario.id).all()
