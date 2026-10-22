"""Lista de deseados: juegos que un usuario guardó para después."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlmodel import Field, SQLModel

from app.core.time import utcnow


class WishlistItem(SQLModel, table=True):
    """Un juego en la lista de deseados de un usuario.

    (user_id, game_id) es único: el mismo juego no se repite en la lista.
    `created_at` permite al panel de popularidad contar los juegos más
    deseados dentro de un período.
    """

    __tablename__ = "wishlist_items"
    __table_args__ = (UniqueConstraint("user_id", "game_id"),)

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(
        sa_column=Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    )
    game_id: int = Field(
        sa_column=Column(
            Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False, index=True
        )
    )
    created_at: datetime = Field(default_factory=utcnow)
