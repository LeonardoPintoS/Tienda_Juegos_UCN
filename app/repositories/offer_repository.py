from __future__ import annotations

from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import and_
from sqlmodel import Session, select

from app.models import Offer


def active_offer_clause(now: datetime):
    """SQL condition: the offer is enabled and `now` is inside its window."""
    return and_(
        Offer.is_active.is_(True),
        Offer.starts_at <= now,
        Offer.ends_at >= now,
    )


def compute_effective_price(base_price: Decimal, offer: Offer | None) -> tuple[Decimal, int]:
    """Returns (final_price, discount_percent) for a game and its active offer."""
    if offer is None:
        return base_price, 0
    factor = (Decimal(100) - Decimal(offer.discount_percent)) / Decimal(100)
    final_price = (base_price * factor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return final_price, offer.discount_percent


def get_active_offer_for_game(session: Session, game_id: int, now: datetime) -> Offer | None:
    """The best active offer of a game (highest discount), or None."""
    statement = (
        select(Offer)
        .where(Offer.game_id == game_id, active_offer_clause(now))
        .order_by(Offer.discount_percent.desc())
    )
    return session.exec(statement).first()
