class Config:
    SECRET_KEY = "botiquin_inteligente_key"

    # ⚙️ CONFIGURA AQUÍ TUS DATOS DE CONEXIÓN A MYSQL
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://u760464709_21005241_usr:+Pksasy4@185.232.14.52/u760464709_21005241_bd"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuraciones adicionales
    SQLALCHEMY_DATABASE_URI = (
        "mysql+pymysql://u760464709_21005241_usr:+Pksasy4@185.232.14.52/"
        "u760464709_21005241_bd?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,  # Verifica la conexión antes de usarla
        "pool_recycle": 1800,   # Recicla conexiones cada 30 minutos
        "pool_size": 5,         # Tamaño del pool de conexiones
        "max_overflow": 10,     # Permite conexiones adicionales
        "connect_args": {"connect_timeout": 10},  # Tiempo de espera para conexión
    }
