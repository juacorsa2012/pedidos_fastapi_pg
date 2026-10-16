from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ClienteBase(BaseModel):
  nombre: str

class ClienteCreate(ClienteBase):
  pass

class ClienteRead(ClienteBase):
  id: int
  created_at: datetime
  updated_at: datetime
  model_config = ConfigDict(from_attributes=True)
