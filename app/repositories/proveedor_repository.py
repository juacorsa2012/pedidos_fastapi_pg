from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

from app.models.proveedor_model import Proveedor
from app.exceptions.custom_errors import ProveedorYaExisteError

class ProveedorRepository:
  def __init__(self, db: AsyncSession):
    self.db = db

  async def registrar(self, nombre: str) -> Proveedor:
    proveedor = Proveedor(nombre=nombre.upper())
    self.db.add(proveedor)
    try:
      await self.db.flush()
    except IntegrityError as e:  
      raise ProveedorYaExisteError(nombre) from e
    return proveedor

  async def obtener_por_nombre(self, nombre: str) -> Proveedor | None:
    resultado = await self.db.execute(select(Proveedor).where(Proveedor.nombre == nombre.strip().upper()))
    return resultado.scalar_one_or_none()
    
  async def obtener_por_id(self, proveedor_id: int) -> Proveedor | None:
    return await self.db.get(Proveedor, proveedor_id)

  async def obtener_todos(self, skip: int = 0, limit: int = 100) -> list[Proveedor]:
    resultado = await self.db.execute(
      select(Proveedor)
      .order_by(Proveedor.nombre)
      .offset(skip)
      .limit(limit))
    
    return list(resultado.scalars().all())

  async def contar_registros(self) -> int:
    resultado = await self.db.execute(select(func.count()).select_from(Proveedor))
    return resultado.scalar_one()

  async def actualizar(self, id: int, nombre: str) -> Proveedor | None:
    resultado = await self.db.execute(select(Proveedor).where(Proveedor.id == id))
    proveedor = resultado.scalar_one_or_none()
    
    if proveedor:
      proveedor.nombre = nombre.strip().upper()
      await self.db.flush()
      await self.db.commit()
      await self.db.refresh(proveedor)
      
    return proveedor