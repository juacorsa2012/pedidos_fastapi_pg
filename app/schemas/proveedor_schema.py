from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ProveedorBase(BaseModel):
  nombre: str

class ProveedorCreate(ProveedorBase):
  pass

class ProveedorResponse(ProveedorBase):
  id: int
  created_at: datetime
  updated_at: datetime
  model_config = ConfigDict(from_attributes=True)
