from __future__ import annotations

from sqlmodel import select

from app.models import Category
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    """Read access to catalog categories.

    Soft-deleted categories (`deleted_at` set) are always excluded by the
    methods below, so the public catalog never exposes them.
    """

    model = Category

    def list_active(self) -> list[Category]:
        """All non-deleted categories, ordered alphabetically by name."""
        statement = (
            select(Category).where(Category.deleted_at.is_(None)).order_by(Category.name.asc())
        )
        return list(self.session.exec(statement).all())

    def get_by_slug(self, slug: str) -> Category | None:
        """A single non-deleted category by its slug, or None."""
        statement = select(Category).where(Category.slug == slug, Category.deleted_at.is_(None))
        return self.session.exec(statement).first()
