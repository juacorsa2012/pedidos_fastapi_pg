from fastapi import APIRouter, Depends, Path, status
from app.schemas.pedido_schema import PedidoCreate, PedidoResponse
from app.models.pedido_model import EstadoPedido
from app.schemas.response_schema import ApiResponse
from app.utils.messages import Mensajes
from app.dependencies import get_pedido_service
from app.services.pedido_service import PedidoService
from app.core.pagination import Paginacion

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ApiResponse)
async def crear_pedido(datos: PedidoCreate, service: PedidoService = Depends(get_pedido_service)):
  pedido = await service.registrar_pedido(datos)
  return ApiResponse(message=Mensajes.PEDIDO_CREADO, data=PedidoResponse.model_validate(pedido))

@router.get("/estado/{estado}", status_code=status.HTTP_200_OK, response_model=ApiResponse)
async def obtener_pedidos_por_estado(
  estado: EstadoPedido,
  paginacion: Paginacion = Depends(),
  service: PedidoService = Depends(get_pedido_service),
):
  pedidos = await service.obtener_por_estado(estado=estado, skip=paginacion.skip, limit=paginacion.limit)
  pedidos_data = [PedidoResponse.model_validate(pedido) for pedido in pedidos]
  return ApiResponse(message=Mensajes.EXITO, data=pedidos_data)

@router.get("/cliente/{cliente_id}/estado/{estado}", status_code=status.HTTP_200_OK, response_model=ApiResponse)
async def obtener_pedidos_por_estado_y_cliente(
  estado: EstadoPedido,
  cliente_id: int = Path(gt=0),
  paginacion: Paginacion = Depends(),
  service: PedidoService = Depends(get_pedido_service),
):
  pedidos = await service.obtener_por_estado_y_cliente(
    estado=estado,
    cliente_id=cliente_id,
    skip=paginacion.skip,
    limit=paginacion.limit,
  )
  pedidos_data = [PedidoResponse.model_validate(pedido) for pedido in pedidos]
  return ApiResponse(message=Mensajes.EXITO, data=pedidos_data)

@router.get("/cliente/{cliente_id}", status_code=status.HTTP_200_OK, response_model=ApiResponse)
async def obtener_pedidos_por_cliente(
  cliente_id: int = Path(gt=0),
  paginacion: Paginacion = Depends(),
  service: PedidoService = Depends(get_pedido_service),
):
  pedidos = await service.obtener_por_cliente(
    cliente_id=cliente_id,
    skip=paginacion.skip,
    limit=paginacion.limit,
  )
  pedidos_data = [PedidoResponse.model_validate(pedido) for pedido in pedidos]
  return ApiResponse(message=Mensajes.EXITO, data=pedidos_data)


@router.get("/proveedor/{proveedor_id}", status_code=status.HTTP_200_OK, response_model=ApiResponse)
async def obtener_pedidos_por_proveedor(
  proveedor_id: int = Path(gt=0),
  paginacion: Paginacion = Depends(),
  service: PedidoService = Depends(get_pedido_service),
):
  pedidos = await service.obtener_por_proveedor(
    proveedor_id=proveedor_id,
    skip=paginacion.skip,
    limit=paginacion.limit,
  )
  pedidos_data = [PedidoResponse.model_validate(pedido) for pedido in pedidos]
  return ApiResponse(message=Mensajes.EXITO, data=pedidos_data)


@router.get("/proveedor/{proveedor_id}/cliente/{cliente_id}", status_code=status.HTTP_200_OK, response_model=ApiResponse)
async def obtener_pedidos_por_proveedor_y_cliente(
  proveedor_id: int = Path(gt=0),
  cliente_id: int = Path(gt=0),
  paginacion: Paginacion = Depends(),
  service: PedidoService = Depends(get_pedido_service),
):
  pedidos = await service.obtener_por_proveedor_y_cliente(
    proveedor_id=proveedor_id,
    cliente_id=cliente_id,
    skip=paginacion.skip,
    limit=paginacion.limit,
  )
  pedidos_data = [PedidoResponse.model_validate(pedido) for pedido in pedidos]
  return ApiResponse(message=Mensajes.EXITO, data=pedidos_data)

@router.get("/{pedido_id}", status_code=status.HTTP_200_OK, response_model=ApiResponse)
async def obtener_pedido_por_id(pedido_id: int = Path(gt=0), service: PedidoService = Depends(get_pedido_service)):
  pedido = await service.obtener_por_id(pedido_id)
  return ApiResponse(message=Mensajes.EXITO, data=PedidoResponse.model_validate(pedido))

@router.put("/{pedido_id}", status_code=status.HTTP_200_OK, response_model=ApiResponse)
async def actualizar_pedido(datos: PedidoCreate, pedido_id: int = Path(gt=0), service: PedidoService = Depends(get_pedido_service)):
  pedido = await service.actualizar_pedido(pedido_id, datos)
  return ApiResponse(message=Mensajes.PEDIDO_ACTUALIZADO, data=PedidoResponse.model_validate(pedido))

@router.delete("/{pedido_id}", status_code=status.HTTP_200_OK, response_model=ApiResponse)
async def eliminar_pedido(pedido_id: int = Path(gt=0), service: PedidoService = Depends(get_pedido_service)):
  await service.eliminar_pedido(pedido_id)
  return ApiResponse(message=Mensajes.PEDIDO_BORRADO, data=None)


