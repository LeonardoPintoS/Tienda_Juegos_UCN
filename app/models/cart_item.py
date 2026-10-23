"""Un juego dentro de un carrito."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlmodel import Field, SQLModel

from app.core.time import utcnow


class CartItem(SQLModel, table=True):
    """Un juego agregado a un carrito.

    No tiene cantidad: un juego digital se compra una sola vez. Por lo
    mismo, (cart_id, game_id) es único: el mismo juego no puede estar dos
    veces en el mismo carrito. El precio NO se guarda aquí; se consulta
    siempre en Game al momento de comprar, como exige el enunciado.
    """

    __tablename__ = "cart_items"
    __table_args__ = (UniqueConstraint("cart_id", "game_id"),)

    id: int | None = Field(default=None, primary_key=True)
    cart_id: int = Field(
        sa_column=Column(Integer, ForeignKey("carts.id", ondelete="CASCADE"), nullable=False)
    )
    game_id: int = Field(
        sa_column=Column(Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False)
    )
    added_at: datetime = Field(default_factory=utcnow)
