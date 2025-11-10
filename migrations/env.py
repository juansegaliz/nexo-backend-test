from logging.config import fileConfig
from alembic import context
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from app.extensions import Base
import app.models


load_dotenv()  

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)


user = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASSWORD")
host = os.getenv("MYSQL_HOST", "127.0.0.1")
port = os.getenv("MYSQL_PORT", "3306")
db = os.getenv("MYSQL_DB")

url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}?charset=utf8mb4"

target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    engine = create_engine(url, pool_pre_ping=True, future=True)

    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
