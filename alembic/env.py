import asyncio
import os
import sys
from logging.config import fileConfig
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import pool

# Importamos o criador de engine assíncrona:
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# ----------------------------------------------------------------------
# 1. Carrega as variáveis do .envs/.env
# ----------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".envs" / ".env")

# ----------------------------------------------------------------------
# 2. Adiciona a raiz ao PATH do Python
# ----------------------------------------------------------------------
sys.path.insert(0, str(BASE_DIR))

# ----------------------------------------------------------------------
# 3. Importa a Base e os modelos
# ----------------------------------------------------------------------
from src.core.database import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ----------------------------------------------------------------------
# 4. Sobrescreve a URL com a variável do .env
# ----------------------------------------------------------------------
database_url = os.getenv("ALEMBIC_DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)

target_metadata = Base.metadata


# ----------------------------------------------------------------------
# Execução das migrações (Modo Assíncrono)
# ----------------------------------------------------------------------
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Cria a conexão assíncrona necessária para o asyncpg."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        # Roda a migração de forma segura dentro do loop assíncrono
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Executa o loop asyncio para rodar as migrações."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
