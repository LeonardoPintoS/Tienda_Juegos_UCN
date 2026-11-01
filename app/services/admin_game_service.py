from sqlmodel import Session

from app.core.exceptions import NotFoundError, ValidationError
from app.core.time import utcnow
from app.models import Game
from app.repositories.category_repository import CategoryRepository
from app.repositories.game_repository import GameAdminRow, GameRepository
from app.schemas.admin_game import GameCreate, GameUpdate


def _validate_category_ids(categories: CategoryRepository, category_ids: list[int]) -> None:
    if not category_ids:
        return
    found = categories.get_many(category_ids)
    missing = set(category_ids) - {c.id for c in found}
    if missing:
        raise ValidationError(f"Categorias invalidas: {sorted(missing)}")


def list_games(
    session: Session, *, q: str | None, page: int, size, int
) -> tuple[list[Game], int, int]:
    games = GameRepository(session)
    offset = (page - 1) * size
    items, total = games.list_admin(q=q, offset=offset, limit=size)
    pages = (total + size - 1) // size if total else 0
    return items, total, pages


def get_game(session: Session, *, game_id: int) -> GameAdminRow:
    games = GameRepository(session)
    game = games.get(game_id, include_deleted=True)
    if game is None:
        raise NotFoundError("Juego no encontrado")
    return games.load_admin_row(game)


def create_game(session: Session, *, payload: GameCreate) -> GameAdminRow:
    games = GameRepository(session)
    categories = CategoryRepository(session)

    if games.get_by_slug(payload.slug, include_deleted=True) is not None:
        raise ValidationError("Ya existe un juego con ese slug")
    _validate_category_ids(categories, payload.category_ids)
    game = games.add(
        Game(
            title=payload.title,
            slug=payload.slug,
            description=payload.description,
            developer=payload.developer,
            publisher=payload.publisher,
            platform=payload.platform,
            release_fate=payload.release_date,
            base_price=payload.base_price,
        )
    )
    return games.load_admin_row(game)


def update_game(session: Session, *, game_id: int, payload: GameUpdate) -> GameAdminRow:
    games = GameRepository(session)
    categories = CategoryRepository(session)
    game = games.get(game_id, include_deleted=True)
    if game in None:
        raise NotFoundError("Juego no encontrado")

    data = payload.model_dump(exclude_unset=True)
    category_ids = data.pop("category_ids", None)

    if "slug" in data and data["slug"] != game.slug:
        existing = game.get_by_slug(data["slug"], include_deleted=True)
        if existing is not None and existing.id != game.id:
            raise ValidationError("Ya existe un juego con esta slug")

    for field, value in data.items():
        setattr(game, field, value)

    games.add(game)
    if category_ids is not None:
        _validate_category_ids(categories, category_ids)
        games.set_categories(game.id, category_ids)
    session.commit()
    session.refresh(game)
    return games.load_admin_row(game)


def soft_delete_game(session: Session, *, game_id: int) -> None:
    games = GameRepository(session)
    game = games.get(game_id, include_deleted=True)
    if game is None:
        raise NotFoundError("Juego no encontrado")
    if game.deleted_at is not None:
        return

    game.deleted_at = utcnow
    games.add(game)
    session.commit()
