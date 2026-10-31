"""Errores propios de la aplicación.

Todos heredan de AppError. handlers.py los convierte en una respuesta JSON
con el mismo formato, sin importar dónde se lanzaron.
"""

from __future__ import annotations


class AppError(Exception):
    """Base de todos los errores de negocio y de autenticación que lanzamos a propósito.

    Cada subclase fija su `status_code` y su `code`; en cada lugar donde se
    lanza solo cambia el `message` legible (y opcionalmente `details`).
    """

    status_code: int = 400
    code: str = "app_error"

    def __init__(self, message: str, *, details: dict | None = None) -> None:
        self.message = message
        self.details = details
        super().__init__(message)


class ValidationError(AppError):
    """La petición rompe una regla de negocio que Pydantic no puede expresar solo
    (los 422 propios de Pydantic los maneja FastAPI por separado).
    """

    status_code = 422
    code = "validation_error"


class UnauthorizedError(AppError):
    """Credenciales ausentes, inválidas, vencidas o revocadas."""

    status_code = 401
    code = "unauthorized"


class ForbiddenError(AppError):
    """El usuario está autenticado, pero no tiene permiso para esta acción."""

    status_code = 403
    code = "forbidden"


class NotFoundError(AppError):
    """El recurso no existe, o no existe *para quien lo pide*.

    Cuando se revisa si algo pertenece al usuario, devolver 404 (y no 403) es
    a propósito: así no se confirma que existe un recurso de otra persona.
    """

    status_code = 404
    code = "not_found"


class ConflictError(AppError):
    """La petición está bien formada, pero choca con el estado actual
    (correo duplicado, una reseña que ya existe, etc.).
    """

    status_code = 409
    code = "conflict"


class RateLimitError(AppError):
    """Demasiadas peticiones. Normalmente lo lanza slowapi, no nuestro código;
    está aquí para que su respuesta tenga el mismo formato que los demás errores.
    """

    status_code = 429
    code = "rate_limited"
