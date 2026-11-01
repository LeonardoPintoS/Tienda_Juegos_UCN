from __future__ import annotations

from decimal import Decimal

from sqlmodel import Session

from app.core.exceptions import NotFoundError
from app.core.time import utcnow
from app.models import Category
from app.repositories.category_repository import CategoryRepository
from app.repositories.game_repository import GameDetailRow, GameRepository, GameSummaryRow
from app.schemas.game import GameSort


def list_games(
    session: Session,
    *,
    q: str | None,
    categories: list[str] | None,
    platform: str | None,
    price_min: Decimal | None,
    price_max: Decimal | None,
    on_offer: bool | None,
    min_rating: float | None,
    sort: GameSort,
    page: int,
    size: int,
) -> tuple[list[GameSummaryRow], int, int]:
    """Returns (items, total, pages)"""
    games = GameRepository(session)
    offset = (page - 1) * size
    items, total = games.search(
        now=utcnow(),
        q=q,
        categories=categories,
        platform=platform,
        price_min=price_min,
        price_max=price_max,
        on_offer=on_offer,
        min_rating=min_rating,
        sort=sort,
        offset=offset,
        limit=size,
    )
    pages = (total + size - 1) // size if total else 0
    return items, total, pages


def get_game_detail(session: Session, *, slug: str) -> GameDetailRow:
    games = GameRepository(session)
    detail = games.get_detail_by_slug(slug=slug, now=utcnow())
    if detail is None:
        raise NotFoundError("Juego no encontrado")
    return detail


def list_categories(session: Session) -> list[Category]:
    """All active categories, ordered by name."""
    return CategoryRepository(session).list_active()


def get_category(session: Session, *, slug: str) -> Category:
    category = CategoryRepository(session).get_by_slug(slug)
    if category is None:
        raise NotFoundError("Categoria no encontrada")
    return category
