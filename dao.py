from models import db, Medicamento

class MedicamentoDAO:

    @staticmethod
    def guardar(medicamento):
        db.session.add(medicamento)
        db.session.commit()

    @staticmethod
    def actualizar(medicamento):
        db.session.commit()

    @staticmethod
    def obtener_por_id(id):
        return Medicamento.query.get(id)

    @staticmethod
    def obtener_por_usuario(usuario_id):
        return Medicamento.query.filter_by(usuario_id=usuario_id).all()

    @staticmethod
    def eliminar(medicamento):
        db.session.delete(medicamento)
        db.session.commit()
