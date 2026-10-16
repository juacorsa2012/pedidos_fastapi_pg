import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from app.exceptions.custom_errors import (
  ProveedorYaExisteError,
  ProveedorNoEncontradoError,
  ProveedorNombreInvalidoError,
)
from app.models.proveedor_model import Proveedor
from app.schemas.proveedor_schema import ProveedorCreate

logger = logging.getLogger(__name__)

class ProveedorService:
  def __init__(self, db: AsyncSession):
    self.db = db

  def _normalizar_nombre(self, nombre: str) -> str:
    nombre_normalizado = nombre.strip().upper()
    if not nombre_normalizado:
      raise ProveedorNombreInvalidoError()
    return nombre_normalizado

  async def registrar_proveedor(self, datos: ProveedorCreate) -> Proveedor:
    nombre = self._normalizar_nombre(datos.nombre)

    resultado = await self.db.execute(select(Proveedor).where(Proveedor.nombre == nombre))
    if resultado.scalar_one_or_none():
      raise ProveedorYaExisteError(nombre)

    proveedor = Proveedor(nombre=nombre)
    self.db.add(proveedor)

    try:
      await self.db.flush()
      await self.db.commit()
    except IntegrityError as e:
      await self.db.rollback()
      raise ProveedorYaExisteError(nombre) from e

    logger.info("Proveedor registrado. ID: %s", proveedor.id)
    return proveedor      
  
  async def obtener_todos(self, skip: int = 0, limit: int = 100) -> list[Proveedor]:    
    proveedores = await self.db.execute(
      select(Proveedor)
      .order_by(Proveedor.nombre)
      .offset(skip)
      .limit(limit))
    
    return list(proveedores.scalars().all()) 
  
  async def obtener_por_nombre(self, nombre: str) -> Proveedor | None:
    proveedor = await self.db.execute(select(Proveedor).where(Proveedor.nombre == nombre.strip().upper()))
    return proveedor.scalar_one_or_none()   
  
  async def obtener_por_id(self, proveedor_id: int) -> Proveedor:   
    proveedor = await self.db.get(Proveedor, proveedor_id)

    if proveedor is None:
      raise ProveedorNoEncontradoError(proveedor_id)

    return proveedor 
  
  async def actualizar_proveedor(self, proveedor_id: int, datos: ProveedorCreate) -> Proveedor:
    proveedor = await self.obtener_por_id(proveedor_id)
    nombre = self._normalizar_nombre(datos.nombre)

    if proveedor.nombre.strip().upper() == nombre:
      return proveedor

    resultado = await self.db.execute(select(Proveedor).where(Proveedor.nombre == nombre))
    existente = resultado.scalar_one_or_none()
    if existente is not None and existente.id != proveedor.id:
      raise ProveedorYaExisteError(nombre)

    proveedor.nombre = nombre

    try:
      await self.db.flush()
      await self.db.refresh(proveedor)
      await self.db.commit()
    except IntegrityError as e:
      await self.db.rollback()
      raise ProveedorYaExisteError(nombre) from e

    logger.info("Proveedor %s actualizado. Nuevo nombre: %s", proveedor_id, proveedor.nombre)

    return proveedor 
  
  async def contar_todos(self) -> int:
    resultado = await self.db.execute(select(func.count()).select_from(Proveedor))
    return resultado.scalar_one()    