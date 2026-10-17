from fastapi import status
from app.utils.messages import Mensajes


class BaseAPIError(Exception):
  def __init__(self, status_code: int, detail: str, error_code: str):
    self.status_code = status_code
    self.detail = detail
    self.error_code = error_code
    super().__init__(detail)

class ProveedorYaExisteError(BaseAPIError):
  def __init__(self, nombre: str):
    super().__init__(
      status_code=status.HTTP_409_CONFLICT,
      detail=f"El proveedor '{nombre}' ya existe en la base de datos",
      error_code="PROVEEDOR_YA_EXISTE"
    )
    self.nombre = nombre

class ProveedorNombreInvalidoError(BaseAPIError):
  def __init__(self, mensaje: str = Mensajes.PROVEEDOR_NOMBRE_VACIO):
    super().__init__(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail=mensaje,
      error_code="NOMBRE_INVALIDO"
    )

class ProveedorNoEncontradoError(BaseAPIError):
  def __init__(self, id: int):
    super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f"Proveedor con ID {id} no encontrado", error_code="PROVEEDOR_NO_ENCONTRADO")
    self.id = id
    
    
class ClienteNombreInvalidoError(BaseAPIError):
  def __init__(self, mensaje: str = Mensajes.CLIENTE_NOMBRE_VACIO):
    super().__init__(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail=mensaje,
      error_code="NOMBRE_INVALIDO"
    )

class ClienteYaExisteError(BaseAPIError):
  def __init__(self, nombre: str):
    super().__init__(
      status_code=status.HTTP_409_CONFLICT,
      detail=f"El cliente '{nombre}' ya existe en la base de datos",
      error_code="CLIENTE_YA_EXISTE"
    )
    self.nombre = nombre

class ClienteNoEncontradoError(BaseAPIError):
  def __init__(self, id: int):
    super().__init__(
      status_code=status.HTTP_404_NOT_FOUND, 
      detail=f"Cliente con ID {id} no encontrado", 
      error_code="CLIENTE_NO_ENCONTRADO"
    )
    self.id = id
    
class PedidoNoEncontradoError(BaseAPIError):
  def __init__(self, pedido_id: int):
    super().__init__(
      status_code=status.HTTP_404_NOT_FOUND, 
      detail=f"Pedido con ID {pedido_id} no encontrado", 
      error_code="PEDIDO_NO_ENCONTRADO"
    )
    self.id = pedido_id