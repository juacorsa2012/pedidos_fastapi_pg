from fastapi import status

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
  def __init__(self, mensaje: str = "El nombre no puede estar vacío"):
    super().__init__(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail=mensaje,
      error_code="NOMBRE_INVALIDO"
    )

class ProveedorNoEncontradoError(BaseAPIError):
  def __init__(self, id: int):
    super().__init__(
      status_code=status.HTTP_404_NOT_FOUND,
      detail=f"Proveedor con ID {id} no encontrado",
      error_code="PROVEEDOR_NO_ENCONTRADO"
    )
    self.id = id
