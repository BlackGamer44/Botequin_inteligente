# botiquin_facade.py
from dao import MedicamentoDAO
from factory import MedicamentoFactory
from events import EventManager
from models import Medicamento, db   # ← IMPORTANTE
from decorators import AlertaDecorator
import pusher

pusher_client = pusher.Pusher(
    app_id='2077108',
    key='918819e46056d1579079',
    secret='49cada5ca34511e202ff',
    cluster='us2',
    ssl=True
)

class BotiquinFacade:
    def __init__(self):
        self.event_manager = EventManager()
        self.factory = MedicamentoFactory()
        self.alertas = []

        # Suscribir eventos
        self.event_manager.subscribe("medicamento_agregado", self.alerta_stock_bajo)
        self.event_manager.subscribe("medicamento_actualizado", self.alerta_stock_bajo)
        self.event_manager.subscribe("medicamento_eliminado", self.alerta_eliminado)

    # ---------------- ALERTAS ----------------
    def alerta_stock_bajo(self, medicamento):
        if medicamento.cantidad_restante <= 2:
            mensaje = f" El medicamento '{medicamento.nombre}' está por agotarse ({medicamento.cantidad_restante} unidades restantes)."
            print(mensaje)
            self.alertas.append(mensaje)  
            pusher_client.trigger('botiquin', 'alerta-stock-bajo', {'mensaje': mensaje})

    def alerta_eliminado(self, medicamento):
        mensaje = f" Medicamento '{medicamento.nombre}' eliminado."
        print(mensaje)
        self.alertas.append(mensaje)
        pusher_client.trigger('botiquin', 'medicamento-eliminado', {
            'id': medicamento.id,
            'mensaje': mensaje
        })

    # ---------------- CRUD PRINCIPAL ----------------
    def agregar_medicamento(self, usuario, nombre, cantidad_total, consumo_diario, tipo):

        nuevo = self.factory.crear_medicamento(nombre, cantidad_total, consumo_diario, tipo)
        nuevo.usuario_id = usuario.id

        MedicamentoDAO.guardar(nuevo)

        decorado = AlertaDecorator(nuevo)
        alerta = decorado.verificar_stock()

        if alerta:
          self.alertas.append(alerta)


        self.event_manager.emit("medicamento_agregado", nuevo)

        # --- EVENTO PUSHER PARA TABLA  ---
        pusher_client.trigger('botiquin', 'medicamento-agregado', {
            'id': nuevo.id,
            'nombre': nuevo.nombre,
            'cantidad_total': nuevo.cantidad_total,
            'consumo_diario': nuevo.consumo_diario,
            'cantidad_restante': nuevo.cantidad_restante,
            'tipo': nuevo.tipo
        })

        return nuevo

    def consumir_medicamento(self, medicamento_id):
        medicamento = MedicamentoDAO.obtener_por_id(medicamento_id)

        if medicamento:
            medicamento.cantidad_restante -= medicamento.consumo_diario

            if medicamento.cantidad_restante < 0:
                medicamento.cantidad_restante = 0

            MedicamentoDAO.actualizar(medicamento)

            # aplicar decorador de alerta
            decorado = AlertaDecorator(medicamento)
            alerta = decorado.verificar_stock()

            if alerta:
                self.alertas.append(alerta)

            self.event_manager.emit("medicamento_actualizado", medicamento)

            # --- PUSHER: Actualizar fila de la tabla ---
            pusher_client.trigger('botiquin', 'medicamento-actualizado', {
                'id': medicamento.id,
                'cantidad_restante': medicamento.cantidad_restante
            })

            # Alerta visual
            pusher_client.trigger('botiquin', 'consumo', {
                'mensaje': f" Se consumió {medicamento.consumo_diario} unidades de {medicamento.nombre}. Restan {medicamento.cantidad_restante}."
            })

        return medicamento

    def obtener_medicamentos_usuario(self, usuario):
        return MedicamentoDAO.obtener_por_usuario(usuario.id)

    def eliminar_medicamento(self, medicamento_id, usuario):

        medicamento = MedicamentoDAO.obtener_por_id(medicamento_id)

        if not medicamento or medicamento.usuario_id != usuario.id:
            return False

        MedicamentoDAO.eliminar(medicamento)

        self.event_manager.emit("medicamento_eliminado", medicamento)

        # --- PUSHER: Eliminar fila de la tabla ---
        pusher_client.trigger('botiquin', 'medicamento-eliminado', {
            'id': medicamento.id
        })

        return True
