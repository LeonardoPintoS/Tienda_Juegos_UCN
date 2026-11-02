"""Business logic for the admin users endpoints: list users, suspend and
reactivate accounts.

Suspension takes effect immediately, even on tokens issued before it:
`get_current_user` re-reads `is_suspended` from the database on every
request, and `login` refuses suspended accounts.
"""

from __future__ import annotations

import math

from sqlmodel import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.core.time import utcnow
from app.models import User
from app.repositories.user_repository import UserRepository


def list_users(
    session: Session, *, q: str | None, page: int, size: int
) -> tuple[list[User], int, int]:
    """Return (users, total, pages) for the requested page."""
    users, total = UserRepository(session).list_page(q=q, offset=(page - 1) * size, limit=size)
    pages = math.ceil(total / size) if total else 0
    return users, total, pages


def get_user(session: Session, *, user_id: int) -> User:
    user = UserRepository(session).get(user_id)
    if user is None:
        raise NotFoundError("Usuario no encontrado.")
    return user


def suspend_user(session: Session, *, admin_id: int, user_id: int, reason: str) -> User:
    if admin_id == user_id:
        raise ConflictError("No puedes suspender tu propia cuenta.")

    users = UserRepository(session)
    user = users.get(user_id)
    if user is None:
        raise NotFoundError("Usuario no encontrado.")

    user.is_suspended = True
    user.suspended_at = utcnow()
    user.suspension_reason = reason
    user.updated_at = utcnow()
    users.add(user)
    session.commit()
    session.refresh(user)
    return user


def reactivate_user(session: Session, *, user_id: int) -> User:
    """Lift a suspension. Idempotent: reactivating an active user is a no-op."""
    users = UserRepository(session)
    user = users.get(user_id)
    if user is None:
        raise NotFoundError("Usuario no encontrado.")

    user.is_suspended = False
    user.suspended_at = None
    user.suspension_reason = None
    user.updated_at = utcnow()
    users.add(user)
    session.commit()
    session.refresh(user)
    return user
