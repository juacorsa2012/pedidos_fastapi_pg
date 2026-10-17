import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from app.exceptions.custom_errors import ClienteNombreInvalidoError, ClienteYaExisteError, ClienteNoEncontradoError
from app.models.cliente_model import Cliente
from app.schemas.cliente_schema import ClienteCreate

logger = logging.getLogger(__name__)

class ClienteService:
  def __init__(self, db: AsyncSession):
    self.db = db

  def _normalizar_nombre(self, nombre: str) -> str:
    nombre_normalizado = nombre.strip().upper()
    if not nombre_normalizado:
      raise ClienteNombreInvalidoError()
    return nombre_normalizado
    
  async def registrar_cliente(self, datos: ClienteCreate) -> Cliente:
    nombre = self._normalizar_nombre(datos.nombre)

    existe = await self.db.scalar(select(Cliente.id).where(Cliente.nombre == nombre))

    if existe is not None:
      raise ClienteYaExisteError(nombre)

    cliente = Cliente(nombre=nombre)
    self.db.add(cliente)

    try:
      await self.db.flush()
      await self.db.commit()
    except IntegrityError as e:
      await self.db.rollback()
      raise ClienteYaExisteError(nombre) from e
    
    await self.db.refresh(cliente)
    logger.info("Cliente registrado. ID: %s", cliente.id)
    return cliente

  
  async def obtener_todos(self, skip: int = 0, limit: int = 100) -> list[Cliente]:    
    clientes = await self.db.execute(
      select(Cliente)
      .order_by(Cliente.nombre)
      .offset(skip)
      .limit(limit))
      
    return list(clientes.scalars().all()) 
    
  
  async def obtener_por_nombre(self, nombre: str) -> Cliente | None:
    cliente = await self.db.execute(select(Cliente).where(Cliente.nombre == nombre.strip().upper()))
    return cliente.scalar_one_or_none()   
    
  async def obtener_por_id(self, cliente_id: int) -> Cliente:   
    cliente = await self.db.get(Cliente, cliente_id)
  
    if cliente is None:
      raise ClienteNoEncontradoError(cliente_id)
  
    return cliente
    
  async def actualizar_cliente(self, cliente_id: int, datos: ClienteCreate) -> Cliente:
    cliente = await self.obtener_por_id(cliente_id)
    nombre = self._normalizar_nombre(datos.nombre)
  
    if cliente.nombre.strip().upper() == nombre:
      return cliente
  
    resultado = await self.db.execute(select(Cliente).where(Cliente.nombre == nombre))
    existe = resultado.scalar_one_or_none()
    if existe is not None and existe.id != cliente.id:
      raise ClienteYaExisteError(nombre)
  
    cliente.nombre = nombre
  
    try:
        await self.db.flush()
        await self.db.refresh(cliente)
        await self.db.commit()
    except IntegrityError as e:
      await self.db.rollback()
      raise ClienteYaExisteError(nombre) from e
  
    logger.info("Cliente %s actualizado. Nuevo nombre: %s", cliente_id, cliente.nombre)
  
    return cliente    
  
  async def contar_todos(self) -> int:
    resultado = await self.db.execute(select(func.count()).select_from(Cliente))
    return resultado.scalar_one()    
