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

    def get_by_slug(self, slug: str, *, include_deleted: bool = False) -> Category | None:

        statement = select(Category).where(Category.slug == slug)
        if not include_deleted:
            statement = statement.where(Category.deleted_at.is_(None))
        return self.session.exec(statement).first()

    def list_all(self) -> list[Category]:
        statement = select(Category).where(Category.deleted_at.is_(None)).order_by(Category.name)
        return list(self.session.exec(statement).all())

    def list_all_admin(self) -> list[Category]:
        statement = select(Category).order_by(Category.name)
        return list(self.session.exec(statement).all())

    def get_by_name(self, name: str, *, include_deleted: bool = False) -> Category | None:

        statement = select(Category).where(Category.name == name)
        if not include_deleted:
            statement = statement.where(Category.deleted_at.is_(None))
        return self.session.exec(statement).first()

    def get_many(self, category_ids: list[int]) -> list[Category]:
        if not category_ids:
            return []
        statement = select(Category).where(
            Category.id.in_(category_ids),
            Category.deleted_at.is_(None),
        )
        return list(self.session.exec(statement).all())
