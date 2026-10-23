"""Códigos de verificación de correo enviados al registrarse."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, SQLModel

from app.core.time import utcnow


class VerificationCode(SQLModel, table=True):
    """Código de un solo uso enviado por correo para verificar la cuenta.

    El código nunca se guarda en texto plano, solo su hash (`code_hash`).
    Al pedir un código nuevo, el servicio marca los anteriores con
    `invalidated_at`, así solo hay uno válido por usuario. El contador de
    intentos fallidos vive en User, no aquí: si estuviera en el código,
    pedir uno nuevo lo reiniciaría y el límite de intentos no serviría.
    """

    __tablename__ = "verification_codes"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(
        sa_column=Column(
            Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
        )
    )
    code_hash: str = Field(max_length=255)
    expires_at: datetime
    consumed_at: datetime | None = Field(default=None)
    invalidated_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=utcnow)
