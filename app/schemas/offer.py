"""Schemas for the admin offers CRUD (/admin/offers)."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def _as_utc(value: datetime | None) -> datetime | None:
    """Treat a datetime sent without timezone as UTC.

    SQLModel 0.0.48 refuses to store naive datetimes, and Swagger lets the
    client send "2026-11-01T00:00:00" with no offset. Normalizing here also
    keeps the ends_at > starts_at comparison safe (naive vs aware raises).
    """
    if value is not None and value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value


class OfferCreate(BaseModel):
    game_id: int
    discount_percent: int = Field(ge=1, le=90)
    starts_at: datetime
    ends_at: datetime
    is_active: bool = True

    _utc_dates = field_validator("starts_at", "ends_at")(_as_utc)

    @model_validator(mode="after")
    def _window_is_ordered(self) -> OfferCreate:
        if self.ends_at <= self.starts_at:
            raise ValueError("ends_at debe ser posterior a starts_at.")
        return self


class OfferUpdate(BaseModel):
    discount_percent: int | None = Field(default=None, ge=1, le=90)
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    is_active: bool | None = None

    _utc_dates = field_validator("starts_at", "ends_at")(_as_utc)


class OfferRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    game_id: int
    discount_percent: int
    starts_at: datetime
    ends_at: datetime
    is_active: bool
