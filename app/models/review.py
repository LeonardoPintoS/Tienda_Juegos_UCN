"""Reseña: valoración y comentario de un usuario sobre un juego."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, UniqueConstraint
from sqlmodel import Field, SQLModel

from app.core.time import utcnow


class Review(SQLModel, table=True):
    """Valoración de 1 a 5 y un comentario opcional.

    (user_id, game_id) es único: máximo una reseña por juego. La regla de
    que el usuario debe tener el juego en su biblioteca la valida el
    servicio, porque SQLite no puede expresar "debe existir una fila en
    otra tabla" como restricción.
    """

    __tablename__ = "reviews"
    __table_args__ = (
        UniqueConstraint("user_id", "game_id"),
        CheckConstraint("rating >= 1 AND rating <= 5", name="rating_range"),
    )

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(
        sa_column=Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    )
    game_id: int = Field(
        sa_column=Column(
            Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False, index=True
        )
    )
    rating: int
    comment: str | None = Field(default=None, max_length=2000)
    deleted_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
