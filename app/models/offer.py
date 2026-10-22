"""Oferta: descuento porcentual de un juego durante un período."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer
from sqlmodel import Field, SQLModel


class Offer(SQLModel, table=True):
    """Descuento de un juego entre `starts_at` y `ends_at`.

    Una oferta está vigente si `is_active` es True y la fecha actual está
    entre `starts_at` y `ends_at`. Las restricciones CHECK impiden guardar
    un descuento fuera de rango o un período al revés, aunque el servicio
    se equivoque.
    """

    __tablename__ = "offers"
    __table_args__ = (
        CheckConstraint(
            "discount_percent >= 1 AND discount_percent <= 90",
            name="discount_range",
        ),
        CheckConstraint("ends_at > starts_at", name="valid_period"),
    )

    id: int | None = Field(default=None, primary_key=True)
    game_id: int = Field(
        sa_column=Column(
            Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False, index=True
        )
    )
    discount_percent: int
    starts_at: datetime
    ends_at: datetime
    is_active: bool = Field(default=True)
