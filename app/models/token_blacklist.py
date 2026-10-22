"""Lista negra de tokens JWT invalidados al cerrar sesión."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, SQLModel

from app.core.time import utcnow


class TokenBlacklist(SQLModel, table=True):
    """Un token revocado (logout), identificado por su `jti` (id único del JWT).

    `expires_at` es la fecha en que el token habría vencido de todas formas:
    después de esa fecha la fila ya no sirve, y el job programado la borra.
    """

    __tablename__ = "token_blacklist"

    id: int | None = Field(default=None, primary_key=True)
    jti: str = Field(unique=True, index=True, max_length=36)
    user_id: int = Field(
        sa_column=Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    )
    expires_at: datetime = Field(index=True)
    revoked_at: datetime = Field(default_factory=utcnow)
