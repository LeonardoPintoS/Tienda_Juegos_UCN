"""Biblioteca: los juegos que un usuario ya compró."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlmodel import Field, SQLModel

from app.core.time import utcnow


class LibraryItem(SQLModel, table=True):
    """Registro de que un usuario posee un juego, obtenido en un pedido.

    Se crea al confirmar la compra. Sirve para dos reglas del enunciado:
    solo se puede reseñar un juego que está en la biblioteca, y no se puede
    comprar dos veces el mismo juego ((user_id, game_id) es único).
    Todas las claves foráneas usan RESTRICT: es la prueba de una compra
    real y no debe desaparecer si se borra algo relacionado.
    """

    __tablename__ = "library_items"
    __table_args__ = (
        UniqueConstraint("user_id", "game_id"),
    )  # Declara unicidad entre ambas columnas, para que el usuario no compre un juego que ya compro

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(
        sa_column=Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    )
    game_id: int = Field(
        sa_column=Column(Integer, ForeignKey("games.id", ondelete="RESTRICT"), nullable=False)
    )
    order_id: int = Field(
        sa_column=Column(Integer, ForeignKey("orders.id", ondelete="RESTRICT"), nullable=False)
    )
    acquired_at: datetime = Field(default_factory=utcnow)
