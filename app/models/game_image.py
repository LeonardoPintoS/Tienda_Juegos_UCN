"""Imágenes de un juego, guardadas en Cloudinary (o en disco en desarrollo)."""

from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, SQLModel


class GameImage(SQLModel, table=True):
    """Una imagen de un juego.

    `public_id` es el identificador de la imagen en Cloudinary; se necesita
    para poder borrarla allá. En modo dev-local empieza con "dev:", para
    que se note que el archivo está en el disco y no en Cloudinary.
    """

    __tablename__ = "game_images"

    id: int | None = Field(default=None, primary_key=True)
    game_id: int = Field(
        sa_column=Column(
            Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False, index=True
        )
    )
    url: str = Field(max_length=1000)
    public_id: str = Field(max_length=300)
    is_cover: bool = Field(default=False)
    sort_order: int = Field(default=0)
