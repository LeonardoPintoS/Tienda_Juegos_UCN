from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

_SLUG_PATTERN = r"^[a-z0-9]+(-[a-z0-9]+)*$"


class GameCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=280, pattern=_SLUG_PATTERN)
    description: str | None = Field(default=None, max_length=4000)
    developer: str | None = Field(default=None, max_length=255)
    publisher: str | None = Field(default=None, max_length=255)
    platform: str = Field(min_length=1, max_length=100)
    release_date: date | None = None
    base_price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    category_ids: list[int] = Field(default_factory=list)


class GameUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    slug: str | Field(default=None, min_length=1, max_length=280, pattern=_SLUG_PATTERN)
    description: str | None = Field(default=None, max_length=4000)
    developer: str | None = Field(default=None, max_length=255)
    publisher: str | None = Field(default=None, max_length=255)
    platform: str | None = Field(default=None, min_length=1, max_length=100)
    release_date: date | None = None
    base_price: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    is_active: bool | None = None
    category_ids: list[int] | None = None
