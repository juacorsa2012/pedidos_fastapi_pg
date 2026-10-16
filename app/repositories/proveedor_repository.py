from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.proveedor_model import Proveedor

class ProveedorRepository:
  def __init__(self, db: AsyncSession):
    self.db = db

  async def registrar(self, nombre: str) -> Proveedor:
    proveedor = Proveedor(nombre=nombre)
    self.db.add(proveedor)
    await self.db.flush()    
    return proveedor

  async def obtener_por_nombre(self, nombre: str) -> Proveedor | None:
    resultado = await self.db.execute(select(Proveedor).where(Proveedor.nombre == nombre.strip().upper()))
    return resultado.scalar_one_or_none()
    
  async def obtener_por_id(self, id: int) -> Proveedor | None:
    resultado = await self.db.execute(select(Proveedor).where(Proveedor.id == id))
    return resultado.scalar_one_or_none()

  async def obtener_todos(self, skip: int = 0, limit: int = 100) -> list[Proveedor]:
    resultado = await self.db.execute(
      select(Proveedor)
      .order_by(Proveedor.nombre.asc())
      .offset(skip)
      .limit(limit))
    
    return resultado.scalars().all()

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