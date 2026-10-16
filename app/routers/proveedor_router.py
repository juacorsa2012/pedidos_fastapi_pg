from fastapi import APIRouter, Depends, status
from app.services.proveedor_service import ProveedorService
from app.schemas.proveedor_schema import ProveedorCreate, ProveedorResponse
from app.schemas.response_schema import ApiResponse
from app.utils.messages import Mensajes
from app.dependencies import get_proveedor_service
from app.core.pagination import Paginacion

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ApiResponse)
async def crear_proveedor(datos: ProveedorCreate, service: ProveedorService = Depends(get_proveedor_service)):
  proveedor = await service.registrar_proveedor(datos)     
  return ApiResponse(message=Mensajes.PROVEEDOR_CREADO, data=ProveedorResponse.model_validate(proveedor))

@router.get("/", status_code=status.HTTP_200_OK, response_model=ApiResponse)
async def obtener_proveedores(
  paginacion: Paginacion = Depends(),
  service: ProveedorService = Depends(get_proveedor_service)):  
  proveedores = await service.obtener_todos(skip=paginacion.skip, limit=paginacion.limit)
  total = await service.contar_todos()
  proveedores_data = [ProveedorResponse.model_validate(p) for p in proveedores]      
  
  return ApiResponse(
    message=Mensajes.EXITO,
    data={
      "proveedores": proveedores_data,
      "paginacion": {
        "total": total,
        "skip": paginacion.skip,
        "limit": paginacion.limit,
        "hay_mas": paginacion.skip + len(proveedores) < total,
      },
    },
  )
  
@router.get("/{proveedor_id}", status_code=status.HTTP_200_OK, response_model=ApiResponse)
async def obtener_proveedor_por_id(proveedor_id: int, service: ProveedorService = Depends(get_proveedor_service)):
  proveedor = await service.obtener_por_id(proveedor_id)   
  return ApiResponse(message=Mensajes.EXITO, data=ProveedorResponse.model_validate(proveedor))

@router.put("/{proveedor_id}", status_code=status.HTTP_200_OK, response_model=ApiResponse)
async def actualizar_proveedor(proveedor_id: int, datos: ProveedorCreate, service: ProveedorService = Depends(get_proveedor_service)):
  proveedor_actualizado = await service.actualizar_proveedor(proveedor_id, datos)    
  return ApiResponse(message=Mensajes.PROVEEDOR_ACTUALIZADO, data=ProveedorResponse.model_validate(proveedor_actualizado))    
  