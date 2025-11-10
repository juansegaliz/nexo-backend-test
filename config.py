import os

class Settings:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}"
        f"@{os.getenv('MYSQL_HOST','127.0.0.1')}:{os.getenv('MYSQL_PORT','3307')}"
        f"/{os.getenv('MYSQL_DB')}?charset=utf8mb4"
    )

    SQLALCHEMY_ECHO = False

    CORS_ORIGINS = os.getenv("CORS_ORIGINS","*").split(",")

    JWT_SECRET = os.getenv("JWT_SECRET", "dev")
    JWT_EXPIRES_MIN = int(os.getenv("JWT_EXPIRES_MIN", "15"))

    UPLOAD_ROOT = os.getenv("UPLOAD_ROOT", "uploads")

    MAX_AVATAR_MB = int(os.getenv("MAX_AVATAR_MB", "2"))
