from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field, StringConstraints

Nombre = Annotated[
  str,
  StringConstraints(strip_whitespace=True, max_length=255),
]

class ClienteBase(BaseModel):
  nombre: Nombre

class ClienteCreate(ClienteBase):
  pass

class ClienteResponse(ClienteBase):
  id: int
  created_at: datetime
  updated_at: datetime

  model_config = ConfigDict(from_attributes=True)
