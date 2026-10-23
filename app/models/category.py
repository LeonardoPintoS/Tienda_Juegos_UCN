"""Categoría (género) para clasificar los juegos del catálogo."""

from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, SQLModel


class Category(SQLModel, table=True):
    """Género o clasificación de un juego, por ejemplo "Acción" o "RPG".

    Se elimina de forma lógica (soft delete) con `deleted_at`: la fila
    nunca se borra, así los juegos que la usaban no pierden la relación.
    El catálogo público solo muestra las que tienen `deleted_at` en NULL.
    """

    __tablename__ = "categories"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, max_length=100)
    slug: str = Field(unique=True, max_length=120, index=True)
    description: str | None = Field(default=None, max_length=500)
    deleted_at: datetime | None = Field(default=None)
