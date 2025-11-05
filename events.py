import datetime

class EventManager:
    def __init__(self):
        self.suscriptores = {}
        self.log_file = "event_log.log"

    def subscribe(self, evento, callback):
        if evento not in self.suscriptores:
            self.suscriptores[evento] = []
        self.suscriptores[evento].append(callback)

    def emit(self, evento, data):
        # Ejecutar callbacks
        if evento in self.suscriptores:
            for callback in self.suscriptores[evento]:
                callback(data)
        # Registrar evento en log
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now()}] EVENTO: {evento} - DATOS: {data}\n")
