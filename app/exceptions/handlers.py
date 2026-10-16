import logging
from fastapi import Request, status, HTTPException
from fastapi.responses import JSONResponse
from app.utils.messages import Mensajes
from .custom_errors import BaseAPIError

logger = logging.getLogger(__name__)

def register_exception_handlers(app):
  """Registra todos los handlers de excepciones en la app"""

  # 1. Handler genérico para TODOS los errores de negocio
  # Captura ProveedorYaExisteError, ProveedorNombreInvalidoError, etc.
  @app.exception_handler(BaseAPIError)
  async def base_api_error_handler(request: Request, exc: BaseAPIError):
    logger.warning(f"Error de negocio [{exc.error_code}]: {exc.detail}")
    return JSONResponse(
      status_code=exc.status_code,
      content={
        "message": str(exc),
        "data": None,
        "success": False,
        "error_code": exc.error_code
      }
    )

  # 2. Handler para HTTPException estándar (404, 409 manuales, etc.)
  @app.exception_handler(HTTPException)
  async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
      status_code=exc.status_code,
      content={
        "message": exc.detail if isinstance(exc.detail, str) else "Error en la solicitud",
        "data": None,
        "success": False
      }
    )

  # 3. Handler catch-all para errores no esperados
  @app.exception_handler(Exception)
  async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error no manejado en {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      content={
        "message": Mensajes.INTERNAL_SERVER_ERROR,
        "data": None,
        "success": False
      }
    )