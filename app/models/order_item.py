"""Detalle congelado de un pedido: qué se compró y a qué precio."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, SQLModel


class OrderItem(SQLModel, table=True):
    """Un juego comprado, copiado tal como estaba al momento de la compra.

    Los campos `*_snapshot` y los precios son una copia: si después el juego
    cambia de nombre o de precio, el historial sigue mostrando lo que el
    usuario realmente pagó. `game_id` puede quedar en NULL (ON DELETE SET
    NULL) si el juego se borrara físicamente; el detalle no se pierde.
    """

    __tablename__ = "order_items"

    id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(
        sa_column=Column(
            Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True
        )
    )
    game_id: int | None = Field(
        default=None,
        sa_column=Column(Integer, ForeignKey("games.id", ondelete="SET NULL"), nullable=True),
    )
    title_snapshot: str = Field(max_length=255)
    slug_snapshot: str = Field(max_length=280)
    unit_price: Decimal = Field(max_digits=10, decimal_places=2)
    discount_percent: int = Field(default=0)
    final_price: Decimal = Field(max_digits=10, decimal_places=2)
