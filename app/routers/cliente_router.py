from fastapi import APIRouter, Depends, status
from app.schemas.cliente_schema import ClienteCreate, ClienteResponse
from app.schemas.response_schema import ApiResponse
from app.utils.messages import Mensajes
from app.dependencies import get_cliente_service
from app.services.cliente_service import ClienteService
from app.core.pagination import Paginacion

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ApiResponse)
async def crear_cliente(datos: ClienteCreate, service: ClienteService = Depends(get_cliente_service)):
  cliente = await service.registrar_cliente(datos)
  return ApiResponse(message=Mensajes.CLIENTE_CREADO, data=ClienteResponse.model_validate(cliente))

@router.get("/", status_code=status.HTTP_200_OK, response_model=ApiResponse)
async def obtener_clientes(paginacion: Paginacion = Depends(), service: ClienteService = Depends(get_cliente_service)):  
  clientes = await service.obtener_todos(skip=paginacion.skip, limit=paginacion.limit)
  total = await service.contar_todos()
  clientes_data = [ClienteResponse.model_validate(c) for c in clientes]      
  
  return ApiResponse(
    message=Mensajes.EXITO,
    data={
      "clientes": clientes_data,
      "paginacion": {
        "total": total,
        "skip": paginacion.skip,
        "limit": paginacion.limit,
        "hay_mas": paginacion.skip + len(clientes) < total,
      },
    },
  )

@router.get("/{cliente_id}", status_code=status.HTTP_200_OK, response_model=ApiResponse)
async def obtener_cliente_por_id(cliente_id: int, service: ClienteService = Depends(get_cliente_service)):
  cliente = await service.obtener_por_id(cliente_id)
  return ApiResponse(message=Mensajes.EXITO, data=ClienteResponse.model_validate(cliente))

@router.put("/{cliente_id}", status_code=status.HTTP_200_OK, response_model=ApiResponse)
async def actualizar_cliente(cliente_id: int, datos: ClienteCreate, service: ClienteService = Depends(get_cliente_service)):
  cliente_actualizado = await service.actualizar_cliente(cliente_id, datos)    
  return ApiResponse(message=Mensajes.CLIENTE_ACTUALIZADO, data=ClienteResponse.model_validate(cliente_actualizado))    
