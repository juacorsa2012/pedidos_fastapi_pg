from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class ProveedorBase(BaseModel):
  pass

class ProveedorCreate(ProveedorBase):
  nombre: str = Field(max_length=255)

class ProveedorResponse(ProveedorBase):
  nombre: str
  id: int
  created_at: datetime
  updated_at: datetime
  model_config = ConfigDict(from_attributes=True)
