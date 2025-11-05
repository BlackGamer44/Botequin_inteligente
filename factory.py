class MedicamentoFactory:
    def crear_medicamento(self, nombre, cantidad_total, consumo_diario):
        return {
            "nombre": nombre,
            "cantidad_total": cantidad_total,
            "consumo_diario": consumo_diario,
            "cantidad_restante": cantidad_total
        }
