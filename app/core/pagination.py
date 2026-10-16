from dataclasses import dataclass
from fastapi import Query
from app.core.config import settings

@dataclass
class Paginacion:
  skip: int = Query(0, ge=0)
  limit: int = Query(
    settings.PAGINACION_LIMITE_POR_DEFECTO,
    ge=1,
    le=settings.PAGINACION_LIMITE_MAXIMO,
  )