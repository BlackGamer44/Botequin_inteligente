# decorators.py
from datetime import datetime

class MedicamentoDecorator:
    def __init__(self, medicamento):
        self.medicamento = medicamento

    def __getattr__(self, attr):
        return getattr(self.medicamento, attr)

class AlertaDecorator(MedicamentoDecorator):
    def verificar_stock(self):
        if self.medicamento.cantidad_restante <= 2:
            print(f"⚠️ ALERTA: {self.medicamento.nombre} está por agotarse ({self.medicamento.cantidad_restante})")

class RegistroDecorator(MedicamentoDecorator):
    def registrar_consumo(self):
        with open("registro_medicamentos.log", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] Se consumió {self.medicamento.nombre}\n")
        print(f"📝 Registro guardado: {self.medicamento.nombre}")
