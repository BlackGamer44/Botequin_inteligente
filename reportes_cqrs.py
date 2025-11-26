# reportes_cqrs.py
from dao import MedicamentoDAO
from datetime import datetime, timedelta
from models import Medicamento

class MedicamentoQueryService:
 
    def obtener_medicamentos_usuario(self, usuario_id):
        return MedicamentoDAO.obtener_por_usuario(usuario_id)

    def obtener_medicamentos_bajo_stock(self, usuario_id, limite=2):
        medicamentos = MedicamentoDAO.obtener_por_usuario(usuario_id)
        return [m for m in medicamentos if m.cantidad_restante <= limite]

    def calcular_fecha_agotamiento(self, medicamento: Medicamento):
        if medicamento.consumo_diario == 0:
            return None
        dias_restantes = medicamento.cantidad_restante / medicamento.consumo_diario
        fecha_fin = datetime.now() + timedelta(days=dias_restantes)
        return fecha_fin.date()

    def obtener_proyecciones_usuario(self, usuario_id):
        medicamentos = MedicamentoDAO.obtener_por_usuario(usuario_id)
        reporte = []

        for m in medicamentos:
            fecha_fin = self.calcular_fecha_agotamiento(m)
            reporte.append({
                "nombre": m.nombre,
                "tipo": m.tipo,
                "restante": m.cantidad_restante,
                "consumo_diario": m.consumo_diario,
                "fecha_agotamiento": fecha_fin
            })

        return reporte


    def consumo_total_semanal(self, usuario_id):
        medicamentos = MedicamentoDAO.obtener_por_usuario(usuario_id)
        return sum(m.consumo_diario * 7 for m in medicamentos)

    def consumo_total_mensual(self, usuario_id):
        medicamentos = MedicamentoDAO.obtener_por_usuario(usuario_id)
        return sum(m.consumo_diario * 30 for m in medicamentos)

class MedicamentoCommandService:

    def registrar_consumo(self, medicamento_id):
        med = MedicamentoDAO.obtener_por_id(medicamento_id)
        if med:
            med.cantidad_restante -= med.consumo_diario
            if med.cantidad_restante < 0:
                med.cantidad_restante = 0
            MedicamentoDAO.actualizar()
        return med

    def editar_medicamento(self, medicamento_id, **datos):
        med = MedicamentoDAO.obtener_por_id(medicamento_id)

        if not med:
            return None

        # Solo actualiza campos recibidos
        for atributo, valor in datos.items():
            setattr(med, atributo, valor)

        MedicamentoDAO.actualizar()
        return med