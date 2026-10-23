"""Shopping cart — works for both guests and authenticated users."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer
from sqlmodel import Field, SQLModel

from app.core.time import utcnow


class Cart(SQLModel, table=True):
    """Un carrito por usuario (aplicado mediante el "user_id" único) o uno por
    sesión de invitado (identificado por "session_token").

    Exactamente uno de "user_id" / "session_token" debe estar establecido —
    aplicado mediante una CheckConstraint, no solo en la capa de servicio,
    para que ningún carrito pueda quedar nunca inaccesible ni por la sesión
    ni por la cuenta. En SQLite, los valores NULL nunca colisionan con una
    restricción única, por lo que cualquier cantidad de carritos de invitados
    (con user_id NULL) coexisten sin problemas junto a la restricción de uno
    por usuario.
    """

    __tablename__ = "carts"
    __table_args__ = (
        CheckConstraint(
            "user_id IS NOT NULL OR session_token IS NOT NULL",
            name="owner_present",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(
        default=None,
        sa_column=Column(
            Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=True
        ),
    )
    session_token: str | None = Field(default=None, unique=True, max_length=64, index=True)
    # Auditoria
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
