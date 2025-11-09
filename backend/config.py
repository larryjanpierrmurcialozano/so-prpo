import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-cambiar-en-produccion")

    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_PORT = os.environ.get("MYSQL_PORT", "3306")
    MYSQL_DB = os.environ.get("MYSQL_DB", "inventario_davincin")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4",
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,           # Número de conexiones permanentes
        'max_overflow': 20,        # Conexiones adicionales temporales
        'pool_timeout': 30,        # Timeout para obtener conexión del pool
        'pool_recycle': 3600,      # Reciclar conexiones cada hora
        'pool_pre_ping': True      # Verificar conexión antes de usar
    }

    MAX_CONTENT_LENGTH = 8 * 1024 * 1024

    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'static', 'uploads')

    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = False  # True en producción con HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
