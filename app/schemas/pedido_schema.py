from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from app.models.pedido_model import EstadoPedido


Producto = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=255),
]


class ClientePedidoResponse(BaseModel):
    id: int
    nombre: str

    model_config = ConfigDict(from_attributes=True)


class ProveedorPedidoResponse(BaseModel):
    id: int
    nombre: str

    model_config = ConfigDict(from_attributes=True)


class PedidoBase(BaseModel):
    producto: Producto
    unidades: int = Field(gt=0)
    oferta: str = Field(default="SIN OFERTA", max_length=25)
    solicitado_por: str | None = None
    observaciones: str | None = Field(default=None, max_length=1000)


class PedidoCreate(PedidoBase):
    cliente_id: int
    proveedor_id: int


class PedidoResponse(PedidoBase):
    id: int
    estado: EstadoPedido
    cliente_id: int
    proveedor_id: int
    cliente: ClientePedidoResponse
    proveedor: ProveedorPedidoResponse
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)