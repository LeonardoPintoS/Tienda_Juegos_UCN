"""GameVault UCN — punto de entrada de la aplicación FastAPI.

Los routers, el manejo centralizado de errores y los jobs se irán
agregando en las siguientes fases. El lifespan de abajo ya ejecuta el
seeder al arrancar; más adelante también iniciará el scheduler.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Se ejecuta una vez al levantar el servidor (antes del yield)."""
    if settings.seed_on_startup:
        # Se importa aquí y no arriba, para que `alembic env.py` (que también
        # importa app.core.config) no cargue el seeder antes de tiempo.
        from app.seeders.run import run_seeders

        run_seeders()
    yield


app = FastAPI(
    title=settings.app_name,
    description="API REST de GameVault UCN - plataforma de distribución de videojuegos",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """liveness check. Extended in later phases with integration satus"""
    return {"status": "ok", "environment": settings.environment}
