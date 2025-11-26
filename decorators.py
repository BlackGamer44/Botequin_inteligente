from datetime import datetime, timedelta

class MedicamentoDecorator:
    def __init__(self, medicamento):
        self.medicamento = medicamento

    def __getattr__(self, attr):
        return getattr(self.medicamento, attr)


class AlertaDecorator(MedicamentoDecorator):
    def verificar_stock(self):
        if self.medicamento.cantidad_restante <= 2:
            return f"⚠️ ALERTA: {self.medicamento.nombre} está por agotarse ({self.medicamento.cantidad_restante})"
        return None


class RegistroDecorator(MedicamentoDecorator):
    def registrar_consumo(self):
        with open("registro_medicamentos.log", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] Se consumió {self.medicamento.nombre}\n")


# ⭐ NUEVO DECORADOR
class ProyeccionDecorator(MedicamentoDecorator):
    def calcular_fecha_fin(self):
        if self.medicamento.consumo_diario == 0:
            return "Consumo diario = 0"
        
        dias = self.medicamento.cantidad_restante / self.medicamento.consumo_diario
        fecha_fin = datetime.now() + timedelta(days=dias)
        return fecha_fin.strftime("%d/%m/%Y")
