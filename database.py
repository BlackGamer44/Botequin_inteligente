from flask_sqlalchemy import SQLAlchemy

class Database:
    __instance = None
    db = SQLAlchemy()

    def __init__(self):
        if Database.__instance is not None:
            raise Exception("Esta clase es un Singleton. Usa get_instance().")
        Database.__instance = self

    @staticmethod
    def get_instance():
        if Database.__instance is None:
            Database()
        return Database.__instance
