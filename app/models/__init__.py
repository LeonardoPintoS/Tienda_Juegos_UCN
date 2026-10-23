"""Importa todos los modelos para registrarlos en SQLModel.metadata.

SQLModel solo conoce una tabla si su clase fue importada al menos una vez.
create_all() y Alembic (autogenerate) leen SQLModel.metadata, así que
basta con importar `app.models` para que vean todas las tablas.
"""

# Debe ir primero: al importarse, database.py define la naming_convention
# de las restricciones, antes de que se cree cualquier tabla.
import app.core.database  # noqa: F401  # isort: skip
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.category import Category
from app.models.enums import OrderStatus, UserRole
from app.models.game import Game
from app.models.game_category_link import GameCategoryLink
from app.models.game_image import GameImage
from app.models.library_item import LibraryItem
from app.models.offer import Offer
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.review import Review
from app.models.token_blacklist import TokenBlacklist
from app.models.user import User
from app.models.verification_code import VerificationCode
from app.models.wishlist_item import WishlistItem

__all__ = [
    "Cart",
    "CartItem",
    "Category",
    "Game",
    "GameCategoryLink",
    "GameImage",
    "LibraryItem",
    "Offer",
    "Order",
    "OrderItem",
    "OrderStatus",
    "Review",
    "TokenBlacklist",
    "User",
    "UserRole",
    "VerificationCode",
    "WishlistItem",
]
