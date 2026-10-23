"""Pedido: una compra confirmada."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlmodel import Field, SQLModel

from app.core.time import utcnow
from app.models.enums import OrderStatus
from app.models.sa_enum import str_enum_column


class Order(SQLModel, table=True):
    """Una compra de un usuario.

    Idempotencia: (user_id, idempotency_key) es único. Si el cliente
    reintenta confirmar la misma compra con la misma clave, la base de
    datos rechaza el segundo pedido y el servicio devuelve el que ya
    existe, sin duplicarlo ni reenviar la boleta.

    `user_id` usa ON DELETE RESTRICT: no se puede borrar un usuario que
    tiene compras, porque el historial nunca debe perderse.
    """

    __tablename__ = "orders"
    __table_args__ = (UniqueConstraint("user_id", "idempotency_key"),)

    id: int | None = Field(default=None, primary_key=True)
    order_code: str = Field(unique=True, index=True, max_length=30)
    user_id: int = Field(
        sa_column=Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    )
    status: OrderStatus = Field(
        default=OrderStatus.PAID,
        sa_column=Column(str_enum_column(OrderStatus), nullable=False),
    )
    subtotal: Decimal = Field(max_digits=10, decimal_places=2)
    discount_total: Decimal = Field(max_digits=10, decimal_places=2)
    total: Decimal = Field(max_digits=10, decimal_places=2)
    idempotency_key: str = Field(max_length=100)
    created_at: datetime = Field(default_factory=utcnow)
    paid_at: datetime = Field(default_factory=utcnow)
    receipt_path: str | None = Field(default=None, max_length=500)
    receipt_sent_at: datetime | None = Field(default=None)
