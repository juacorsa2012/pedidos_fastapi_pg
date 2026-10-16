import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.custom_errors import ProveedorYaExisteError, ProveedorNombreInvalidoError, ProveedorNoEncontradoError
from app.models.proveedor_model import Proveedor
from app.schemas.proveedor_schema import ProveedorCreate
from app.repositories.proveedor_repository import ProveedorRepository
from app.utils.messages import Mensajes

logger = logging.getLogger(__name__)

class ProveedorService:
  def __init__(self, db: AsyncSession):
    self.db = db
    self.repo = ProveedorRepository(db)

  async def registrar_proveedor(self, datos: ProveedorCreate) -> Proveedor:
    if await self.repo.obtener_por_nombre(datos.nombre):
      raise ProveedorYaExisteError(datos.nombre)

    proveedor = await self.repo.registrar(datos.nombre)
    await self.db.commit()
    logger.info("Proveedor registrado. ID: %s", proveedor.id)
    return proveedor    

  async def obtener_todos(self, skip: int = 0, limit: int = 100) -> list[Proveedor]:    
    return await self.repo.obtener_todos(skip=skip, limit=limit)

  async def obtener_por_nombre(self, nombre: str) -> Proveedor | None:
    return await self.repo.obtener_por_nombre(nombre)  

  async def obtener_por_id(self, id: int) -> Proveedor | None:    
    proveedor = await self.repo.obtener_por_id(id)   

    if proveedor is None:
      raise ProveedorNoEncontradoError(id)

    return proveedor 

  async def actualizar_proveedor(self, id: int, nuevo_nombre: str) -> Proveedor:
    nombre_limpio = nuevo_nombre.strip().upper()
    
    if len(nombre_limpio) == 0:
      logger.warning("Intento de actualización fallida: El nombre proporcionado estaba vacío.")      
      raise ProveedorNombreInvalidoError(Mensajes.PROVEEDOR_NOMBRE_VACIO)    

    # Verificamos si el proveedor existe
    proveedor_actual = await self.repo.obtener_por_id(id)
    if not proveedor_actual:
      logger.warning("Intento de actualización fallida: El proveedor no existe en la base de datos.")
      raise ProveedorNoEncontradoError(id)      

    #  VALIDACIÓN DE UNICIDAD: Solo si el nombre ha cambiado
    if nombre_limpio != proveedor_actual.nombre:
      existe_otro_proveedor = await self.repo.obtener_por_nombre(nombre_limpio)
      if existe_otro_proveedor:
        logger.warning("Intento de actualización fallida: Se ha intentado actualizar un proveedor con el nombre de otro ya existente.")
        raise ProveedorYaExisteError(nombre_limpio)

    # Si pasa las validaciones, llamamos al repo para que actualice y haga commit
    nuevo_proveedor = await self.repo.actualizar(id, nombre_limpio)
    logger.info(f"Proveedor actualizado con éxito. Nuevo nombre asignado: {nuevo_proveedor.nombre}")

    return nuevo_proveedor