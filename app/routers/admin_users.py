"""Admin endpoints for user management (/admin/users). Admin role required."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.core.database import get_session
from app.core.dependencies import AdminUser
from app.schemas.admin_user import AdminUserRead, SuspendUserRequest, UserPage
from app.services import admin_user_service

router = APIRouter(prefix="/admin/users", tags=["admin-users"])

SessionDep = Annotated[Session, Depends(get_session)]


@router.get("", response_model=UserPage)
def list_users(
    session: SessionDep,
    _admin: AdminUser,
    q: Annotated[str | None, Query(max_length=255, description="Busca en correo y nombre")] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> UserPage:
    users, total, pages = admin_user_service.list_users(session, q=q, page=page, size=size)
    return UserPage(
        items=[AdminUserRead.model_validate(u) for u in users],
        page=page,
        size=size,
        total=total,
        pages=pages,
    )


@router.get("/{user_id}", response_model=AdminUserRead)
def get_user(user_id: int, session: SessionDep, _admin: AdminUser) -> AdminUserRead:
    user = admin_user_service.get_user(session, user_id=user_id)
    return AdminUserRead.model_validate(user)


@router.patch("/{user_id}/suspend", response_model=AdminUserRead)
def suspend_user(
    user_id: int, payload: SuspendUserRequest, session: SessionDep, admin: AdminUser
) -> AdminUserRead:
    user = admin_user_service.suspend_user(
        session, admin_id=admin.id, user_id=user_id, reason=payload.reason
    )
    return AdminUserRead.model_validate(user)


@router.patch("/{user_id}/reactivate", response_model=AdminUserRead)
def reactivate_user(user_id: int, session: SessionDep, _admin: AdminUser) -> AdminUserRead:
    user = admin_user_service.reactivate_user(session, user_id=user_id)
    return AdminUserRead.model_validate(user)
