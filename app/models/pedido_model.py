from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, func, ForeignKey
from database import Base
from enum import Enum
from sqlalchemy import Enum as SQLEnum


class EstadoPedido(str, Enum):
  PEDIDO = "pedido"
  PREPARADO = "preparado"
  ENTREGADO = "entregado"
  CANCELADO = "cancelado"
  FACTURADO = "facturado"
  DEVUELTO  = "devuelto"


class Pedido(Base):
  __tablename__ = "pedidos"

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  producto: Mapped[str] = mapped_column(String(255), nullable=False)
  unidades: Mapped[int] = mapped_column(Integer, nullable=False)
  oferta: Mapped[str] = mapped_column(String(25), nullable=False, default="SIN OFERTA")
  solicitado_por: Mapped[str | None] = mapped_column(String(255), nullable=True)
  observaciones: Mapped[str | None] = mapped_column(String(1000), nullable=True)
  estado: Mapped[EstadoPedido] = mapped_column(SQLEnum(EstadoPedido), nullable=False, default=EstadoPedido.PEDIDO)
  proveedor_id: Mapped[int] = mapped_column(ForeignKey("proveedores.id"), nullable=False)
  proveedor: Mapped["Proveedor"] = relationship(back_populates="pedidos")
  cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=False)
  cliente: Mapped["Cliente"] = relationship(back_populates="pedidos")
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
  updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(),nullable=False)

