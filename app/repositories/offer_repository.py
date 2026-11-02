"""The single canonical definition of "is this offer live right now".

Every place in the app that needs an effective price (catalog, cart and
checkout, the seeder) must call these helpers, never re-derive the
condition inline. A copy that forgets `is_active` would apply discounts an
admin explicitly turned off.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import update
from sqlalchemy.sql.elements import ColumnElement
from sqlmodel import Session, select

from app.models.game import Game
from app.models.offer import Offer
from app.repositories.base import BaseRepository


def active_offer_clause(now: datetime) -> ColumnElement[bool]:
    """SQLAlchemy boolean clause: is an Offer row live at `now`?

    Vigency requires all three: the admin's manual switch is on, and `now`
    falls inside [starts_at, ends_at].
    """
    return Offer.is_active.is_(True) & (Offer.starts_at <= now) & (Offer.ends_at >= now)


def get_active_offer_for_game(session: Session, game_id: int, now: datetime) -> Offer | None:
    """The live offer for a game, if any.

    Offer creation (admin_offer_service) is responsible for not letting two
    offers on the same game overlap in time; this just returns whichever
    one the query finds, since at most one should ever match.
    """
    statement = select(Offer).where(Offer.game_id == game_id, active_offer_clause(now))
    return session.exec(statement).first()


def compute_effective_price(base_price: Decimal, offer: Offer | None) -> tuple[Decimal, int]:
    """The (final_price, discount_percent) for a game given its possibly-None
    active offer, rounded to 2 decimals like any other currency amount.
    """
    if offer is None:
        return base_price, 0
    discount = (base_price * offer.discount_percent) / Decimal(100)
    final_price = (base_price - discount).quantize(Decimal("0.01"))
    return final_price, offer.discount_percent


class OfferRepository(BaseRepository[Offer]):
    model = Offer

    def list_all(self, *, game_id: int | None = None) -> list[Offer]:
        statement = select(Offer).order_by(Offer.starts_at.desc())
        if game_id is not None:
            statement = statement.where(Offer.game_id == game_id)
        return list(self.session.exec(statement).all())

    def lock_game_offers(self, game_id: int) -> None:
        """Serialize admin writes on one game's offers.

        "No two active offers may overlap" spans several rows, so no DB
        constraint can enforce it: the service's check-then-insert is the
        only defence, and two concurrent requests would both pass the check
        before either commits. A no-op UPDATE on the game row takes the
        write lock; the second request waits here until the first commits,
        so its overlap check then sees the first one's offer.
        """
        self.session.execute(
            update(Game).where(Game.id == game_id).values(id=Game.id),
            execution_options={"synchronize_session": False},
        )

    def list_overlapping_active(
        self,
        *,
        game_id: int,
        starts_at: datetime,
        ends_at: datetime,
        exclude_offer_id: int | None = None,
    ) -> list[Offer]:
        statement = select(Offer).where(
            Offer.game_id == game_id,
            Offer.is_active.is_(True),
            Offer.starts_at <= ends_at,
            Offer.ends_at >= starts_at,
        )
        if exclude_offer_id is not None:
            statement = statement.where(Offer.id != exclude_offer_id)
        return list(self.session.exec(statement).all())
