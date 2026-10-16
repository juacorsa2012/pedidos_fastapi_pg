from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.pedido_model import EstadoPedido

class PedidoBase(BaseModel):
  producto: str
  unidades: int
  oferta: str = "SIN OFERTA"
  solicitado_por: str | None = None
  observaciones: str | None = None

class PedidoCreate(PedidoBase):
  cliente_id: int
  proveedor_id: int

class PedidoRead(PedidoBase):
  id: int
  estado: EstadoPedido
  proveedor_id: int
  cliente_id: int
  created_at: datetime
  updated_at: datetime

  model_config = ConfigDict(from_attributes=True)