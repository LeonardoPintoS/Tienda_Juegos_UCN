"""User model — identity, role, verification and suspension state."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column
from sqlmodel import Field, SQLModel

from app.core.time import utcnow
from app.models.enums import UserRole
from app.models.sa_enum import str_enum_column


class User(SQLModel, table=True):
    """Una cuenta registrada: ya sea un comprador o un administrador.

    "verification_attempts" y "verification_blocked_until" residen aquí, no
    en VerificationCode — si el contador residiera en el código, solicitar uno
    nuevo lo restablecería y el límite de intentos máximos sería trivial de
    eludir (ver app/models/verification_code.py).

    La suspensión no revoca directamente los JWT ya emitidos (TokenBlacklist
    solo rastrea cierres de sesión explícitos, ver token_blacklist.py). En su
    lugar, `is_suspended` se vuelve a comprobar contra esta fila en cada
    solicitud autenticada (app/core/dependencies.py), que es lo que realmente
    hace que una suspensión surta efecto en los tokens emitidos antes de ella.
    """

    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(
        index=True, unique=True, max_length=255
    )  # unique:facilita la busque por email unico en la base de datos
    password_hash: str  # guarda contraseña que luego hasharemos
    full_name: str = Field(max_length=255)
    role: UserRole = Field(  # deriva de la clase enums.py predeterminadamente "user"
        default=UserRole.USER,
        sa_column=Column(str_enum_column(UserRole), nullable=False),
    )

    # Seguridad
    is_verified: bool = Field(default=False)
    is_suspended: bool = Field(default=False)
    suspended_at: datetime | None = Field(default=None)
    suspension_reason: str | None = Field(default=None, max_length=500)

    verification_attempts: int = Field(default=0)
    verification_blocked_until: datetime | None = Field(default=None)

    # Auditoria
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    # No eliminamos usuarios, porque es importante mantener el registro de compras que mantiene
    # por eso nosotros solamente suspendemos la cuenta en caso de que el usuario deje la cuenta.
