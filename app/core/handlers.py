"""Manejo centralizado de errores.

Cualquier AppError, cualquier rechazo por rate limit (slowapi) y cualquier
error no controlado se convierten en el mismo formato de JSON: la API nunca
muestra un traceback interno ni responde errores con formas distintas.
`request_id` ya forma parte de ese formato (se lee de `request.state`),
aunque todavía nada lo asigna: lo llenará más adelante el middleware de
logging, sin tener que cambiar este archivo.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.core.exceptions import AppError

logger = logging.getLogger(__name__)


def _error_response(
    status_code: int, code: str, message: str, request: Request, details: object = None
) -> JSONResponse:
    # Se usa jsonable_encoder y no un dict directo: los errores de Pydantic
    # pueden traer el objeto de la excepción dentro (ctx.error), y json.dumps
    # no sabe convertirlo. Sin esto, un 422 legítimo terminaría en un 500.
    content = jsonable_encoder(
        {
            "error": {"code": code, "message": message, "details": details},
            "request_id": getattr(request.state, "request_id", None),
        }
    )
    return JSONResponse(status_code=status_code, content=content)


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Errores que lanzamos a propósito (ConflictError, UnauthorizedError, etc.)."""
    return _error_response(exc.status_code, exc.code, exc.message, request, exc.details)


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Errores de forma de la petición que detecta FastAPI/Pydantic, envueltos en
    el mismo formato en vez de su forma por defecto `{"detail": [...]}`.
    """
    return _error_response(
        422, "validation_error", "Datos de entrada invalidos.", request, exc.errors()
    )


async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Demasiadas peticiones (lo detecta slowapi)."""
    return _error_response(
        429, "rate_limited", "Demasiadas solicitudes. Intenta de nuevo mas tarde.", request
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Cualquier error inesperado: se registra completo en el log del servidor,
    pero al cliente solo se le dice que hubo un error interno.
    """
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return _error_response(500, "internal_error", "Ha ocurrido un error interno.", request)


def register_exception_handlers(app: FastAPI) -> None:
    """Conecta cada tipo de error con su manejador. Se llama una vez en main.py."""
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
