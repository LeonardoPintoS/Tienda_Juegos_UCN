"""Entorno de Alembic.

La URL de conexión viene de app.core.config.settings (DATABASE_URL en
.env), nunca de alembic.ini. `render_as_batch` es obligatorio en SQLite:
no tiene un ALTER TABLE real, así que Alembic recrea la tabla por debajo
para aplicar un cambio, y para hacerlo de forma segura todas las
restricciones necesitan tener un nombre predecible (ver la
naming_convention en app.core.database). Por eso hay que importar
`app.models`, y no solo `app.core.database`, antes de leer
`target_metadata` más abajo.
"""

from logging.config import fileConfig

from alembic import context
from sqlmodel import SQLModel

# Registra todas las tablas en SQLModel.metadata (ver app/models/__init__.py)
# y, de paso, aplica la naming_convention al importar app.core.database.
import app.models  # noqa: E402, F401
from app.core.config import settings
from app.core.database import engine

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# El "plano" de las tablas que Alembic compara contra la base de datos real.
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Genera el SQL por pantalla, sin conectarse a la base de datos."""
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Aplica las migraciones conectándose a la base de datos.

    Reutiliza el mismo engine de la app (app.core.database.engine) en vez
    de crear otro a partir de alembic.ini, así las migraciones y la app
    siempre usan la misma configuración de conexión.
    """
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
