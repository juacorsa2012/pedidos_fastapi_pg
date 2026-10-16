from pydantic import BaseModel
from typing import Any, Optional

class ApiResponse(BaseModel):
  """
  Schema estándar para todas las respuestas de la API.
  Permite mantener una estructura consistente: { message, data, success }
  """
  message: str
  data: Optional[Any] = None
  success: bool = True