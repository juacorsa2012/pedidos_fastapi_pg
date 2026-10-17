import logging
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.custom_errors import ClienteNoEncontradoError, ProveedorNoEncontradoError, PedidoNoEncontradoError
from app.models.cliente_model import Cliente
from app.models.pedido_model import EstadoPedido, Pedido
from app.models.proveedor_model import Proveedor
from app.schemas.pedido_schema import PedidoCreate

logger = logging.getLogger(__name__)

class PedidoService:
  def __init__(self, db: AsyncSession):
    self.db = db
  
  async def registrar_pedido(self, datos: PedidoCreate) -> Pedido:
    cliente = await self.db.get(Cliente, datos.cliente_id)
    if cliente is None:
      raise ClienteNoEncontradoError(datos.cliente_id)

    proveedor = await self.db.get(Proveedor, datos.proveedor_id)
    if proveedor is None:
      raise ProveedorNoEncontradoError(datos.proveedor_id)

    pedido = Pedido(**datos.model_dump())
    self.db.add(pedido)

    try:
      await self.db.commit()
      await self.db.refresh(pedido)
    except SQLAlchemyError:
      await self.db.rollback()
      raise

    logger.info("Pedido registrado. ID: %s", pedido.id)
    return pedido

  
  
  async def obtener_por_id(self, pedido_id: int) -> Pedido:
    resultado = await self.db.execute(
      select(Pedido)
      .options(
        selectinload(Pedido.cliente),
        selectinload(Pedido.proveedor),
      )
      .where(Pedido.id == pedido_id)
    )
    pedido = resultado.scalar_one_or_none()

    if pedido is None:
      raise PedidoNoEncontradoError(pedido_id)

    return pedido
  
  
  async def actualizar_pedido(self, pedido_id: int, datos: PedidoCreate) -> Pedido:
    pedido = await self.db.get(Pedido, pedido_id)
    if pedido is None:
      raise PedidoNoEncontradoError(pedido_id)

    cliente = await self.db.get(Cliente, datos.cliente_id)
    if cliente is None:
      raise ClienteNoEncontradoError(datos.cliente_id)

    proveedor = await self.db.get(Proveedor, datos.proveedor_id)
    if proveedor is None:
      raise ProveedorNoEncontradoError(datos.proveedor_id)

    for campo, valor in datos.model_dump().items():
      setattr(pedido, campo, valor)

    try:
      await self.db.flush()
      await self.db.commit()
    except SQLAlchemyError:
      await self.db.rollback()
      raise

    logger.info("Pedido %s actualizado", pedido_id)
    return await self.obtener_por_id(pedido_id)

  async def obtener_por_estado(self, estado: EstadoPedido, skip: int = 0, limit: int = 100) -> list[Pedido]:
    resultado = await self.db.execute(
      select(Pedido)
      .options(
        selectinload(Pedido.cliente),
        selectinload(Pedido.proveedor),
      )
      .where(Pedido.estado == estado)
      .order_by(Pedido.id)
      .offset(skip)
      .limit(limit)
    )
    return list(resultado.scalars().all())

  async def obtener_por_cliente(self, cliente_id: int, skip: int = 0, limit: int = 100) -> list[Pedido]:
    resultado = await self.db.execute(
      select(Pedido)
      .options(
        selectinload(Pedido.cliente),
        selectinload(Pedido.proveedor),
      )
      .where(Pedido.cliente_id == cliente_id)
      .order_by(Pedido.id)
      .offset(skip)
      .limit(limit)
    )
    return list(resultado.scalars().all())

  async def obtener_por_proveedor(self, proveedor_id: int, skip: int = 0, limit: int = 100) -> list[Pedido]:
    resultado = await self.db.execute(
      select(Pedido)
      .options(
        selectinload(Pedido.cliente),
        selectinload(Pedido.proveedor),
      )
      .where(Pedido.proveedor_id == proveedor_id)
      .order_by(Pedido.id)
      .offset(skip)
      .limit(limit)
    )
    return list(resultado.scalars().all())

  async def obtener_por_proveedor_y_cliente(self, proveedor_id: int, cliente_id: int, skip: int = 0, limit: int = 100) -> list[Pedido]:
    resultado = await self.db.execute(
      select(Pedido)
      .options(
        selectinload(Pedido.cliente),
        selectinload(Pedido.proveedor),
      )
      .where(
        Pedido.proveedor_id == proveedor_id,
        Pedido.cliente_id == cliente_id,
      )
      .order_by(Pedido.id)
      .offset(skip)
      .limit(limit)
    )
    return list(resultado.scalars().all())

  async def obtener_por_estado_y_cliente(
    self,
    estado: EstadoPedido,
    cliente_id: int,
    skip: int = 0,
    limit: int = 100,
  ) -> list[Pedido]:
    resultado = await self.db.execute(
      select(Pedido)
      .options(
        selectinload(Pedido.cliente),
        selectinload(Pedido.proveedor),
      )
      .where(
        Pedido.estado == estado,
        Pedido.cliente_id == cliente_id,
      )
      .order_by(Pedido.id)
      .offset(skip)
      .limit(limit)
    )
    return list(resultado.scalars().all())

  
  async def eliminar_pedido(self, pedido_id: int) -> None:
    pedido = await self.db.get(Pedido, pedido_id)
    if pedido is None:
      raise PedidoNoEncontradoError(pedido_id)

    try:
      await self.db.delete(pedido)
      await self.db.commit()
    except SQLAlchemyError:
      await self.db.rollback()
      raise

    logger.info("Pedido eliminado. ID: %s", pedido_id)


  
