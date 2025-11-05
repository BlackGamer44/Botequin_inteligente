class EventManager:
    def __init__(self):
        self.suscriptores = {}

    def subscribe(self, evento, callback):
        if evento not in self.suscriptores:
            self.suscriptores[evento] = []
        self.suscriptores[evento].append(callback)

    def emit(self, evento, data):
        if evento in self.suscriptores:
            for callback in self.suscriptores[evento]:
                callback(data)
