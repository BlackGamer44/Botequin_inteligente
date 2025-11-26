from models import Medicamento

class MedicamentoFactory:
    def crear_medicamento(self, nombre, cantidad_total, consumo_diario, tipo):
        if tipo == "pastilla":
            return Pastilla(nombre, cantidad_total, consumo_diario)
        elif tipo == "inyeccion":
            return Inyeccion(nombre, cantidad_total, consumo_diario)
        elif tipo == "jarabe":
            return Jarabe(nombre, cantidad_total, consumo_diario)
        elif tipo == "tableta":
            return Tableta(nombre, cantidad_total, consumo_diario)
        elif tipo == "capsula":
            return Capsula(nombre, cantidad_total, consumo_diario)
        else:
            raise ValueError("Tipo de medicamento no válido")

class Pastilla(Medicamento):
    def __init__(self, nombre, cantidad_total, consumo_diario):
        self.nombre = nombre
        self.cantidad_total = cantidad_total
        self.consumo_diario = consumo_diario
        self.cantidad_restante = cantidad_total
        self.tipo = "pastilla"

class Inyeccion(Medicamento):
    def __init__(self, nombre, cantidad_total, consumo_diario):
        self.nombre = nombre
        self.cantidad_total = cantidad_total
        self.consumo_diario = consumo_diario
        self.cantidad_restante = cantidad_total
        self.tipo = "inyeccion"

class Jarabe(Medicamento):
    def __init__(self, nombre, cantidad_total, consumo_diario):
        self.nombre = nombre
        self.cantidad_total = cantidad_total
        self.consumo_diario = consumo_diario
        self.cantidad_restante = cantidad_total
        self.tipo = "jarabe"

class Tableta(Medicamento):
    def __init__(self, nombre, cantidad_total, consumo_diario):
        self.nombre = nombre
        self.cantidad_total = cantidad_total
        self.consumo_diario = consumo_diario
        self.cantidad_restante = cantidad_total
        self.tipo = "tableta"

class Capsula(Medicamento):
    def __init__(self, nombre, cantidad_total, consumo_diario):
        self.nombre = nombre
        self.cantidad_total = cantidad_total
        self.consumo_diario = consumo_diario
        self.cantidad_restante = cantidad_total
        self.tipo = "capsula"