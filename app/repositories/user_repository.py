"""Data access for User. No query outside this class touches the users
table directly.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import case, update
from sqlmodel import select

from app.models import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    def get_by_email(self, email: str) -> User | None:
        return self.session.exec(select(User).where(User.email == email)).first()

    def claim_verification_attempt(
        self, user_id: int, *, max_attempts: int, blocked_until: datetime
    ) -> bool:
        """Atomically consume one verification attempt.

        A single UPDATE both checks and increments the counter, so two
        concurrent requests can never both slip under the limit. If this
        attempt is the last one allowed, the same statement also sets
        `verification_blocked_until`. Returns False when no attempt was
        left (the user is already blocked or out of attempts).
        """
        result = self.session.execute(
            update(User)
            .where(
                User.id == user_id,
                User.verification_blocked_until.is_(None),
                User.verification_attempts < max_attempts,
            )
            .values(
                verification_attempts=User.verification_attempts + 1,
                # Block only if this attempt uses up the last one.
                verification_blocked_until=case(
                    (User.verification_attempts + 1 >= max_attempts, blocked_until),
                    else_=None,
                ),
            ),
            execution_options={"synchronize_session": False},
        )
        return result.rowcount == 1

    def reset_expired_verification_block(self, user_id: int, now: datetime) -> bool:
        """Clear a block whose time has passed and reset the attempt counter.

        Without resetting the counter it would stay at the maximum, and the
        first attempt after the block expired would block the user again.
        Returns True if a block was actually cleared.
        """
        result = self.session.execute(
            update(User)
            .where(
                User.id == user_id,
                User.verification_blocked_until.is_not(None),
                User.verification_blocked_until <= now,
            )
            .values(verification_attempts=0, verification_blocked_until=None),
            execution_options={"synchronize_session": False},
        )
        return result.rowcount == 1

    def mark_verified(self, user_id: int) -> None:
        """Mark the account as verified and clear any attempt state."""
        self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(is_verified=True, verification_attempts=0, verification_blocked_until=None),
            execution_options={"synchronize_session": False},
        )
