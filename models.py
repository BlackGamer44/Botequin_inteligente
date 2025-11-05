class BotiquinDB:
    __instance = None

    def __init__(self):
        if BotiquinDB.__instance is not None:
            raise Exception("Esta clase es un Singleton. Usa get_instance().")
        else:
            self.medicamentos = []
            BotiquinDB.__instance = self

    @staticmethod
    def get_instance():
        if BotiquinDB.__instance is None:
            BotiquinDB()
        return BotiquinDB.__instance

    def agregar_medicamento(self, medicamento):
        self.medicamentos.append(medicamento)

    def obtener_todos(self):
        return self.medicamentos

    def obtener_por_nombre(self, nombre):
        for m in self.medicamentos:
            if m["nombre"] == nombre:
                return m
        return None
