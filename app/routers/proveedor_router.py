from fastapi import APIRouter, Depends, status
from app.services.proveedor_service import ProveedorService
from app.schemas.proveedor_schema import ProveedorCreate, ProveedorResponse
from app.schemas.response_schema import ApiResponse
from app.utils.messages import Mensajes
from app.dependencies import get_proveedor_service
from app.exceptions.custom_errors import ProveedorNoEncontradoError

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ApiResponse)
async def crear_proveedor(proveedor: ProveedorCreate, service: ProveedorService = Depends(get_proveedor_service)):
  nuevo_proveedor = await service.registrar_proveedor(proveedor)
     
  return ApiResponse(
    message=Mensajes.PROVEEDOR_CREADO,
    data=ProveedorResponse.model_validate(nuevo_proveedor),
    success=True
  )

@router.get("/", status_code=status.HTTP_200_OK, response_model=ApiResponse)
async def obtener_proveedores(service: ProveedorService = Depends(get_proveedor_service)):  
  proveedores = await service.obtener_todos()
  proveedores_data = [ProveedorResponse.model_validate(p) for p in proveedores]
      
  return ApiResponse(
    message=Mensajes.EXITO,
    data=proveedores_data,
    success=True
  )
  
@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=ApiResponse)
async def obtener_proveedor_por_id(id: int, service: ProveedorService = Depends(get_proveedor_service)):
  proveedor = await service.obtener_por_id(id)

  if not proveedor:
    raise ProveedorNoEncontradoError(id)    
   
  return ApiResponse(
    message=Mensajes.EXITO,
    data=ProveedorResponse.model_validate(proveedor),
    success=True
  )

@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=ApiResponse)
async def actualizar_proveedor(id: int, datos: ProveedorCreate, service: ProveedorService = Depends(get_proveedor_service)):
  proveedor_actualizado = await service.actualizar_proveedor(id, datos.nombre)  
  
  return ApiResponse(
    message=Mensajes.PROVEEDOR_ACTUALIZADO,
    data=ProveedorResponse.model_validate(proveedor_actualizado),
    success=True
  )    
  