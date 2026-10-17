import pytest
from httpx import AsyncClient
from fastapi import status
from app.utils.messages import Mensajes
from app.services.cliente_service import ClienteService
from app.services.pedido_service import PedidoService
from app.services.proveedor_service import ProveedorService
from app.schemas.cliente_schema import ClienteCreate
from app.schemas.proveedor_schema import ProveedorCreate
from app.schemas.pedido_schema import PedidoCreate
from app.models.pedido_model import EstadoPedido
from app.utils.messages import Mensajes

PEDIDOS_URL = "/api/v1/pedidos/"

@pytest.mark.asyncio
async def test_endpoint_crear_pedido_devuelve_201(
  client: AsyncClient, 
  cliente_service: ClienteService, 
  proveedor_service: ProveedorService) -> None:
  cliente = await cliente_service.registrar_cliente(ClienteCreate(nombre="Cliente"))
  proveedor = await proveedor_service.registrar_proveedor(ProveedorCreate(nombre="Proveedor"))

  response = await client.post(
    PEDIDOS_URL,
    json={
      "producto": "Producto de prueba",
      "unidades": 2,
      "oferta": "OFERTA 500",
      "solicitado_por": "solicitado por",
      "observaciones": "observaciones",
      "cliente_id": cliente.id,
      "proveedor_id": proveedor.id,
    },
  )

  cuerpo = response.json()

  assert response.status_code == status.HTTP_201_CREATED
  assert cuerpo["message"] == Mensajes.PEDIDO_CREADO
  assert cuerpo["success"] is True
  assert cuerpo["data"]["id"] is not None
  assert cuerpo["data"]["producto"] == "Producto de prueba"
  assert cuerpo["data"]["oferta"] == "OFERTA 500"
  assert cuerpo["data"]["solicitado_por"] == "solicitado por"
  assert cuerpo["data"]["observaciones"] == "observaciones"
  assert cuerpo["data"]["unidades"] == 2
  assert cuerpo["data"]["cliente_id"] == cliente.id
  assert cuerpo["data"]["proveedor_id"] == proveedor.id


@pytest.mark.asyncio
async def test_endpoint_crear_pedido_sin_producto_devuelve_422(
  client: AsyncClient,
  cliente_service: ClienteService,
  proveedor_service: ProveedorService) -> None:
  cliente = await cliente_service.registrar_cliente(ClienteCreate(nombre="Cliente"))
  proveedor = await proveedor_service.registrar_proveedor(ProveedorCreate(nombre="Proveedor"))

  response = await client.post(
    PEDIDOS_URL,
    json={
      "unidades": 2,
      "cliente_id": cliente.id,
      "proveedor_id": proveedor.id,
    },
  )
  cuerpo = response.json()

  assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  assert cuerpo["success"] is False
  assert cuerpo["data"] is None
  assert cuerpo["message"] == Mensajes.DATOS_ENVIADOS_NO_VALIDOS
  assert cuerpo["error_code"] == "VALIDACION_ERROR"

@pytest.mark.asyncio
async def test_endpoint_crear_pedido_sin_unidades_devuelve_422(
  client: AsyncClient,
  cliente_service: ClienteService,
  proveedor_service: ProveedorService) -> None:
  cliente = await cliente_service.registrar_cliente(ClienteCreate(nombre="Cliente"))
  proveedor = await proveedor_service.registrar_proveedor(ProveedorCreate(nombre="Proveedor"))

  response = await client.post(
    PEDIDOS_URL,
    json={
      "producto": "Producto de prueba",
      "cliente_id": cliente.id,
      "proveedor_id": proveedor.id,
    },
  )

  cuerpo = response.json()

  assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  assert cuerpo["success"] is False
  assert cuerpo["data"] is None
  assert cuerpo["message"] == Mensajes.DATOS_ENVIADOS_NO_VALIDOS
  assert cuerpo["error_code"] == "VALIDACION_ERROR"


@pytest.mark.asyncio
async def test_endpoint_crear_pedido_con_cliente_inexistente_devuelve_404(client: AsyncClient, proveedor_service: ProveedorService) -> None:
  proveedor = await proveedor_service.registrar_proveedor(ProveedorCreate(nombre="Proveedor"))

  response = await client.post(
    PEDIDOS_URL,
    json={
      "producto": "Producto de prueba",
      "unidades": 2,
      "cliente_id": 999999,
      "proveedor_id": proveedor.id,
    },
  )

  cuerpo = response.json()

  assert response.status_code == status.HTTP_404_NOT_FOUND
  assert cuerpo["message"] == "Cliente con ID 999999 no encontrado"
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "CLIENTE_NO_ENCONTRADO"
  assert cuerpo["data"] is None


@pytest.mark.asyncio
async def test_endpoint_crear_pedido_con_proveedor_inexistente_devuelve_404(client: AsyncClient, cliente_service: ClienteService) -> None:
  cliente = await cliente_service.registrar_cliente(ClienteCreate(nombre="Cliente"))

  response = await client.post(
    PEDIDOS_URL,
    json={
      "producto": "Producto de prueba",
      "unidades": 2,
      "cliente_id": cliente.id,
      "proveedor_id": 999999,
    },
  )

  cuerpo = response.json()

  assert response.status_code == status.HTTP_404_NOT_FOUND
  assert cuerpo["message"] == "Proveedor con ID 999999 no encontrado"
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "PROVEEDOR_NO_ENCONTRADO"
  assert cuerpo["data"] is None


@pytest.mark.asyncio
async def test_endpoint_crear_pedido_con_unidades_negativas_devuelve_422(
  client: AsyncClient,
  cliente_service: ClienteService,
  proveedor_service: ProveedorService,
) -> None:
  cliente = await cliente_service.registrar_cliente(ClienteCreate(nombre="Cliente"))
  proveedor = await proveedor_service.registrar_proveedor(ProveedorCreate(nombre="Proveedor"))

  response = await client.post(
    PEDIDOS_URL,
    json={
      "producto": "Producto de prueba",
      "unidades": -1,
      "cliente_id": cliente.id,
      "proveedor_id": proveedor.id,
    },
  )

  cuerpo = response.json()

  assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  assert cuerpo["success"] is False
  assert cuerpo["data"] is None
  assert cuerpo["message"] == Mensajes.DATOS_ENVIADOS_NO_VALIDOS
  assert cuerpo["error_code"] == "VALIDACION_ERROR"


@pytest.mark.asyncio
async def test_endpoint_crear_pedido_con_producto_vacio_devuelve_422(
  client: AsyncClient,
  cliente_service: ClienteService,
  proveedor_service: ProveedorService,
) -> None:
  cliente = await cliente_service.registrar_cliente(ClienteCreate(nombre="Cliente"))
  proveedor = await proveedor_service.registrar_proveedor(ProveedorCreate(nombre="Proveedor"))

  response = await client.post(
    PEDIDOS_URL,
    json={
      "producto": "   ",
      "unidades": 1,
      "cliente_id": cliente.id,
      "proveedor_id": proveedor.id,
    },
  )

  cuerpo = response.json()

  assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  assert cuerpo["success"] is False
  assert cuerpo["data"] is None
  assert cuerpo["message"] == Mensajes.DATOS_ENVIADOS_NO_VALIDOS
  assert cuerpo["error_code"] == "VALIDACION_ERROR"


@pytest.mark.asyncio
async def test_endpoint_crear_pedido_con_producto_muy_largo_devuelve_422(
  client: AsyncClient,
  cliente_service: ClienteService,
  proveedor_service: ProveedorService,
) -> None:
  cliente = await cliente_service.registrar_cliente(ClienteCreate(nombre="Cliente"))
  proveedor = await proveedor_service.registrar_proveedor(ProveedorCreate(nombre="Proveedor"))

  response = await client.post(
    PEDIDOS_URL,
    json={
      "producto": "P" * 256,
      "unidades": 1,
      "cliente_id": cliente.id,
      "proveedor_id": proveedor.id,
    },
  )

  cuerpo = response.json()

  assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  assert cuerpo["success"] is False
  assert cuerpo["data"] is None
  assert cuerpo["message"] == Mensajes.DATOS_ENVIADOS_NO_VALIDOS
  assert cuerpo["error_code"] == "VALIDACION_ERROR"


@pytest.mark.asyncio
async def test_endpoint_crear_pedido_con_unidades_cero_devuelve_422(
  client: AsyncClient,
  cliente_service: ClienteService,
  proveedor_service: ProveedorService,
) -> None:
  cliente = await cliente_service.registrar_cliente(ClienteCreate(nombre="Cliente"))
  proveedor = await proveedor_service.registrar_proveedor(ProveedorCreate(nombre="Proveedor"))

  response = await client.post(
    PEDIDOS_URL,
    json={
      "producto": "Producto de prueba",
      "unidades": 0,
      "cliente_id": cliente.id,
      "proveedor_id": proveedor.id,
    },
  )

  cuerpo = response.json()

  assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  assert cuerpo["success"] is False
  assert cuerpo["data"] is None
  assert cuerpo["message"] == Mensajes.DATOS_ENVIADOS_NO_VALIDOS
  assert cuerpo["error_code"] == "VALIDACION_ERROR"


@pytest.mark.parametrize(
  "campos_opcionales",
  [
    {},
    {"solicitado_por": None, "observaciones": None},
  ],
  ids=["omitidos", "nulos"],
)
@pytest.mark.asyncio
async def test_endpoint_crear_pedido_acepta_campos_opcionales_omitidos_o_nulos(
  client: AsyncClient,
  cliente_service: ClienteService,
  proveedor_service: ProveedorService,
  campos_opcionales: dict[str, None],
) -> None:
  cliente = await cliente_service.registrar_cliente(ClienteCreate(nombre="Cliente"))
  proveedor = await proveedor_service.registrar_proveedor(ProveedorCreate(nombre="Proveedor"))
  datos_pedido = {
    "producto": "Producto de prueba",
    "unidades": 1,
    "cliente_id": cliente.id,
    "proveedor_id": proveedor.id,
    **campos_opcionales,
  }

  response = await client.post(PEDIDOS_URL, json=datos_pedido)
  cuerpo = response.json()

  assert response.status_code == status.HTTP_201_CREATED
  assert cuerpo["data"]["solicitado_por"] is None
  assert cuerpo["data"]["observaciones"] is None


@pytest.mark.parametrize(
  ("campo", "valor"),
  [
    ("oferta", "O" * 26),
    ("observaciones", "O" * 1001),
  ],
  ids=["oferta-supera-25", "observaciones-supera-1000"],
)
@pytest.mark.asyncio
async def test_endpoint_crear_pedido_rechaza_campos_que_superan_longitud_maxima(
  client: AsyncClient,
  cliente_service: ClienteService,
  proveedor_service: ProveedorService,
  campo: str,
  valor: str,
) -> None:
  cliente = await cliente_service.registrar_cliente(ClienteCreate(nombre="Cliente"))
  proveedor = await proveedor_service.registrar_proveedor(ProveedorCreate(nombre="Proveedor"))
  datos_pedido = {
    "producto": "Producto de prueba",
    "unidades": 1,
    "cliente_id": cliente.id,
    "proveedor_id": proveedor.id,
    campo: valor,
  }

  response = await client.post(PEDIDOS_URL, json=datos_pedido)
  cuerpo = response.json()

  assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  assert cuerpo["success"] is False
  assert cuerpo["data"] is None
  assert cuerpo["message"] == Mensajes.DATOS_ENVIADOS_NO_VALIDOS
  assert cuerpo["error_code"] == "VALIDACION_ERROR"


@pytest.mark.asyncio
async def test_endpoint_crear_pedido_acepta_producto_de_255_caracteres(
  client: AsyncClient,
  cliente_service: ClienteService,
  proveedor_service: ProveedorService,
) -> None:
  cliente = await cliente_service.registrar_cliente(ClienteCreate(nombre="Cliente"))
  proveedor = await proveedor_service.registrar_proveedor(ProveedorCreate(nombre="Proveedor"))
  producto = "P" * 255

  response = await client.post(
    PEDIDOS_URL,
    json={
      "producto": producto,
      "unidades": 1,
      "cliente_id": cliente.id,
      "proveedor_id": proveedor.id,
    },
  )
  cuerpo = response.json()

  assert response.status_code == status.HTTP_201_CREATED
  assert cuerpo["data"]["producto"] == producto
  assert len(cuerpo["data"]["producto"]) == 255


@pytest.mark.parametrize("unidades", ["dos", 1.5], ids=["texto", "decimal-fraccionario"])
@pytest.mark.asyncio
async def test_endpoint_crear_pedido_rechaza_unidades_con_tipo_invalido(
  client: AsyncClient,
  cliente_service: ClienteService,
  proveedor_service: ProveedorService,
  unidades: str | float,
) -> None:
  cliente = await cliente_service.registrar_cliente(ClienteCreate(nombre="Cliente"))
  proveedor = await proveedor_service.registrar_proveedor(ProveedorCreate(nombre="Proveedor"))

  response = await client.post(
    PEDIDOS_URL,
    json={
      "producto": "Producto de prueba",
      "unidades": unidades,
      "cliente_id": cliente.id,
      "proveedor_id": proveedor.id,
    },
  )
  cuerpo = response.json()

  assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  assert cuerpo["success"] is False
  assert cuerpo["data"] is None
  assert cuerpo["message"] == Mensajes.DATOS_ENVIADOS_NO_VALIDOS
  assert cuerpo["error_code"] == "VALIDACION_ERROR"


@pytest.mark.asyncio
async def test_endpoint_crear_pedido_acepta_campos_en_longitud_maxima(
  client: AsyncClient,
  cliente_service: ClienteService,
  proveedor_service: ProveedorService,
) -> None:
  cliente = await cliente_service.registrar_cliente(ClienteCreate(nombre="Cliente"))
  proveedor = await proveedor_service.registrar_proveedor(ProveedorCreate(nombre="Proveedor"))
  oferta = "O" * 25
  observaciones = "X" * 1000

  response = await client.post(
    PEDIDOS_URL,
    json={
      "producto": "Producto de prueba",
      "unidades": 1,
      "oferta": oferta,
      "observaciones": observaciones,
      "cliente_id": cliente.id,
      "proveedor_id": proveedor.id,
    },
  )
  cuerpo = response.json()

  assert response.status_code == status.HTTP_201_CREATED
  assert cuerpo["data"]["oferta"] == oferta
  assert len(cuerpo["data"]["oferta"]) == 25
  assert cuerpo["data"]["observaciones"] == observaciones
  assert len(cuerpo["data"]["observaciones"]) == 1000


@pytest.mark.parametrize(
  "campo_id",
  ["cliente_id", "proveedor_id"],
  ids=["cliente-id-no-entero", "proveedor-id-no-entero"],
)
@pytest.mark.asyncio
async def test_endpoint_crear_pedido_rechaza_ids_no_enteros(
  client: AsyncClient,
  cliente_service: ClienteService,
  proveedor_service: ProveedorService,
  campo_id: str,
) -> None:
  cliente = await cliente_service.registrar_cliente(ClienteCreate(nombre="Cliente"))
  proveedor = await proveedor_service.registrar_proveedor(ProveedorCreate(nombre="Proveedor"))
  datos_pedido = {
    "producto": "Producto de prueba",
    "unidades": 1,
    "cliente_id": cliente.id,
    "proveedor_id": proveedor.id,
  }
  datos_pedido[campo_id] = "no-es-entero"

  response = await client.post(PEDIDOS_URL, json=datos_pedido)
  cuerpo = response.json()

  assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  assert cuerpo["success"] is False
  assert cuerpo["data"] is None
  assert cuerpo["message"] == Mensajes.DATOS_ENVIADOS_NO_VALIDOS
  assert cuerpo["error_code"] == "VALIDACION_ERROR"


@pytest.mark.asyncio
async def test_endpoint_crear_pedido_usa_valores_predeterminados(
  client: AsyncClient,
  cliente_service: ClienteService,
  proveedor_service: ProveedorService,
) -> None:
  cliente = await cliente_service.registrar_cliente(ClienteCreate(nombre="Cliente"))
  proveedor = await proveedor_service.registrar_proveedor(ProveedorCreate(nombre="Proveedor"))

  response = await client.post(
    PEDIDOS_URL,
    json={
      "producto": "Producto de prueba",
      "unidades": 1,
      "cliente_id": cliente.id,
      "proveedor_id": proveedor.id,
    },
  )
  cuerpo = response.json()

  assert response.status_code == status.HTTP_201_CREATED
  assert cuerpo["data"]["oferta"] == "SIN OFERTA"
  assert cuerpo["data"]["estado"] == EstadoPedido.PEDIDO.value


@pytest.mark.asyncio
async def test_endpoint_obtener_pedido_por_id_devuelve_pedido_con_cliente_y_proveedor(
  client: AsyncClient,
  pedido_service: PedidoService,
  cliente_service: ClienteService,
  proveedor_service: ProveedorService,
) -> None:
  cliente = await cliente_service.registrar_cliente(ClienteCreate(nombre="Cliente"))
  proveedor = await proveedor_service.registrar_proveedor(ProveedorCreate(nombre="Proveedor"))
  pedido_creado = await pedido_service.registrar_pedido(
    PedidoCreate(
      producto="Producto de prueba",
      unidades=2,
      cliente_id=cliente.id,
      proveedor_id=proveedor.id,
    ),
  )

  response = await client.get(f"{PEDIDOS_URL}{pedido_creado.id}")
  cuerpo = response.json()

  assert response.status_code == status.HTTP_200_OK
  assert cuerpo["message"] == Mensajes.EXITO
  assert cuerpo["success"] is True
  assert cuerpo["data"]["id"] == pedido_creado.id
  assert cuerpo["data"]["cliente"]["id"] == cliente.id
  assert cuerpo["data"]["cliente"]["nombre"] == "CLIENTE"
  assert cuerpo["data"]["proveedor"]["id"] == proveedor.id
  assert cuerpo["data"]["proveedor"]["nombre"] == "PROVEEDOR"


@pytest.mark.asyncio
async def test_endpoint_obtener_pedido_inexistente_devuelve_404(client: AsyncClient) -> None:
  response = await client.get(f"{PEDIDOS_URL}999999")
  cuerpo = response.json()

  assert response.status_code == status.HTTP_404_NOT_FOUND
  assert cuerpo["message"] == "Pedido con ID 999999 no encontrado"
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "PEDIDO_NO_ENCONTRADO"
  assert cuerpo["data"] is None  


@pytest.mark.asyncio
async def test_endpoint_obtener_pedido_con_id_no_entero_devuelve_422(client: AsyncClient) -> None:
  response = await client.get(f"{PEDIDOS_URL}no-es-entero")
  cuerpo = response.json()

  assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "VALIDACION_ERROR"
  assert cuerpo["data"] is None


@pytest.mark.asyncio
async def test_endpoint_actualizar_pedido_con_unidades_negativas_devuelve_422(
  client: AsyncClient,
  pedido_service: PedidoService,
  cliente_service: ClienteService,
  proveedor_service: ProveedorService,
) -> None:
  cliente = await cliente_service.registrar_cliente(ClienteCreate(nombre="Cliente"))
  proveedor = await proveedor_service.registrar_proveedor(ProveedorCreate(nombre="Proveedor"))
  pedido = await pedido_service.registrar_pedido(
    PedidoCreate(
      producto="Producto original",
      unidades=1,
      cliente_id=cliente.id,
      proveedor_id=proveedor.id,
    ),
  )

  response = await client.put(
    f"{PEDIDOS_URL}{pedido.id}",
    json={
      "producto": "Producto actualizado",
      "unidades": -1,
      "cliente_id": cliente.id,
      "proveedor_id": proveedor.id,
    },
  )
  cuerpo = response.json()

  assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "VALIDACION_ERROR"
  assert cuerpo["data"] is None


@pytest.mark.asyncio
async def test_endpoint_obtener_pedido_con_id_negativo_devuelve_422(client: AsyncClient) -> None:
  response = await client.get(f"{PEDIDOS_URL}-1")
  cuerpo = response.json()

  assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "VALIDACION_ERROR"
  assert cuerpo["data"] is None


@pytest.mark.asyncio
async def test_endpoint_obtener_pedido_con_id_cero_devuelve_422(client: AsyncClient) -> None:
  response = await client.get(f"{PEDIDOS_URL}0")
  cuerpo = response.json()

  assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "VALIDACION_ERROR"
  assert cuerpo["data"] is None


@pytest.mark.asyncio
async def test_endpoint_eliminar_pedido_existente_devuelve_200(
  client: AsyncClient,
  pedido_service: PedidoService,
  cliente_service: ClienteService,
  proveedor_service: ProveedorService,
) -> None:
  cliente = await cliente_service.registrar_cliente(ClienteCreate(nombre="Cliente"))
  proveedor = await proveedor_service.registrar_proveedor(ProveedorCreate(nombre="Proveedor"))
  pedido = await pedido_service.registrar_pedido(
    PedidoCreate(
      producto="Producto de prueba",
      unidades=1,
      cliente_id=cliente.id,
      proveedor_id=proveedor.id,
    ),
  )

  response = await client.delete(f"{PEDIDOS_URL}{pedido.id}")
  cuerpo = response.json()

  assert response.status_code == status.HTTP_200_OK
  assert cuerpo["message"] == Mensajes.PEDIDO_BORRADO
  assert cuerpo["success"] is True
  assert cuerpo["data"] is None

  consulta = await client.get(f"{PEDIDOS_URL}{pedido.id}")
  assert consulta.status_code == status.HTTP_404_NOT_FOUND

  segundo_borrado = await client.delete(f"{PEDIDOS_URL}{pedido.id}")
  cuerpo_segundo_borrado = segundo_borrado.json()
  assert segundo_borrado.status_code == status.HTTP_404_NOT_FOUND
  assert cuerpo_segundo_borrado["error_code"] == "PEDIDO_NO_ENCONTRADO"


@pytest.mark.asyncio
async def test_endpoint_eliminar_pedido_inexistente_devuelve_404(client: AsyncClient) -> None:
  response = await client.delete(f"{PEDIDOS_URL}999999")
  cuerpo = response.json()

  assert response.status_code == status.HTTP_404_NOT_FOUND
  assert cuerpo["message"] == "Pedido con ID 999999 no encontrado"
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "PEDIDO_NO_ENCONTRADO"
  assert cuerpo["data"] is None


@pytest.mark.asyncio
async def test_endpoint_eliminar_pedido_con_id_cero_devuelve_422(client: AsyncClient) -> None:
  response = await client.delete(f"{PEDIDOS_URL}0")
  cuerpo = response.json()

  assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "VALIDACION_ERROR"
  assert cuerpo["data"] is None


@pytest.mark.asyncio
async def test_endpoint_eliminar_pedido_con_id_negativo_devuelve_422(client: AsyncClient) -> None:
  response = await client.delete(f"{PEDIDOS_URL}-1")
  cuerpo = response.json()

  assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "VALIDACION_ERROR"
  assert cuerpo["data"] is None


@pytest.mark.asyncio
async def test_endpoint_eliminar_pedido_con_id_no_entero_devuelve_422(client: AsyncClient) -> None:
  response = await client.delete(f"{PEDIDOS_URL}no-es-entero")
  cuerpo = response.json()

  assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "VALIDACION_ERROR"
  assert cuerpo["data"] is None


@pytest.mark.asyncio
async def test_endpoint_obtener_pedidos_por_estado_devuelve_pedidos_con_estado(
  client: AsyncClient,
  pedido_service: PedidoService,
  cliente_service: ClienteService,
  proveedor_service: ProveedorService,
) -> None:
  cliente = await cliente_service.registrar_cliente(ClienteCreate(nombre="Cliente"))
  proveedor = await proveedor_service.registrar_proveedor(ProveedorCreate(nombre="Proveedor"))
  pedido = await pedido_service.registrar_pedido(
    PedidoCreate(
      producto="Producto de prueba",
      unidades=1,
      cliente_id=cliente.id,
      proveedor_id=proveedor.id,
    ),
  )

  response = await client.get(f"{PEDIDOS_URL}estado/{EstadoPedido.PEDIDO.value}")
  cuerpo = response.json()

  assert response.status_code == status.HTTP_200_OK
  assert cuerpo["message"] == Mensajes.EXITO
  assert cuerpo["success"] is True
  assert len(cuerpo["data"]) == 1
  assert cuerpo["data"][0]["id"] == pedido.id
  assert cuerpo["data"][0]["estado"] == EstadoPedido.PEDIDO.value
  assert cuerpo["data"][0]["cliente"]["id"] == cliente.id
  assert cuerpo["data"][0]["proveedor"]["id"] == proveedor.id


@pytest.mark.asyncio
async def test_endpoint_obtener_pedidos_por_estado_inexistente_devuelve_422(client: AsyncClient) -> None:
  response = await client.get(f"{PEDIDOS_URL}estado/no-existe")
  cuerpo = response.json()

  assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "VALIDACION_ERROR"
  assert cuerpo["data"] is None


@pytest.mark.asyncio
async def test_endpoint_obtener_pedidos_por_estado_sin_resultados_devuelve_lista_vacia(client: AsyncClient) -> None:
  response = await client.get(f"{PEDIDOS_URL}estado/{EstadoPedido.FACTURADO.value}")
  cuerpo = response.json()

  assert response.status_code == status.HTTP_200_OK
  assert cuerpo["message"] == Mensajes.EXITO
  assert cuerpo["success"] is True
  assert cuerpo["data"] == []


@pytest.mark.asyncio
async def test_endpoint_actualizar_pedido_devuelve_pedido_actualizado(
  client: AsyncClient,
  pedido_service: PedidoService,
  cliente_service: ClienteService,
  proveedor_service: ProveedorService,
) -> None:
  cliente = await cliente_service.registrar_cliente(ClienteCreate(nombre="Cliente"))
  proveedor = await proveedor_service.registrar_proveedor(ProveedorCreate(nombre="Proveedor"))
  pedido = await pedido_service.registrar_pedido(
    PedidoCreate(
      producto="Producto original",
      unidades=1,
      cliente_id=cliente.id,
      proveedor_id=proveedor.id,
    ),
  )

  response = await client.put(
    f"{PEDIDOS_URL}{pedido.id}",
    json={
      "producto": "Producto actualizado",
      "unidades": 3,
      "oferta": "OFERTA NUEVA",
      "solicitado_por": "Cliente",
      "observaciones": "Pedido actualizado",
      "cliente_id": cliente.id,
      "proveedor_id": proveedor.id,
    },
  )
  cuerpo = response.json()

  assert response.status_code == status.HTTP_200_OK
  assert cuerpo["message"] == Mensajes.PEDIDO_ACTUALIZADO
  assert cuerpo["success"] is True
  assert cuerpo["data"]["id"] == pedido.id
  assert cuerpo["data"]["producto"] == "Producto actualizado"
  assert cuerpo["data"]["unidades"] == 3
  assert cuerpo["data"]["oferta"] == "OFERTA NUEVA"
  assert cuerpo["data"]["cliente"]["id"] == cliente.id
  assert cuerpo["data"]["proveedor"]["id"] == proveedor.id


@pytest.mark.asyncio
async def test_endpoint_actualizar_pedido_inexistente_devuelve_404(client: AsyncClient) -> None:
  response = await client.put(
    f"{PEDIDOS_URL}999999",
    json={
      "producto": "Producto de prueba",
      "unidades": 1,
      "cliente_id": 1,
      "proveedor_id": 1,
    },
  )
  cuerpo = response.json()

  assert response.status_code == status.HTTP_404_NOT_FOUND
  assert cuerpo["message"] == "Pedido con ID 999999 no encontrado"
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "PEDIDO_NO_ENCONTRADO"
  assert cuerpo["data"] is None


@pytest.mark.asyncio
async def test_endpoint_actualizar_pedido_con_producto_vacio_devuelve_422(
  client: AsyncClient,
  pedido_service: PedidoService,
  cliente_service: ClienteService,
  proveedor_service: ProveedorService,
) -> None:
  cliente = await cliente_service.registrar_cliente(ClienteCreate(nombre="Cliente"))
  proveedor = await proveedor_service.registrar_proveedor(ProveedorCreate(nombre="Proveedor"))
  pedido = await pedido_service.registrar_pedido(
    PedidoCreate(
      producto="Producto original",
      unidades=1,
      cliente_id=cliente.id,
      proveedor_id=proveedor.id,
    ),
  )

  response = await client.put(
    f"{PEDIDOS_URL}{pedido.id}",
    json={
      "producto": "   ",
      "unidades": 1,
      "cliente_id": cliente.id,
      "proveedor_id": proveedor.id,
    },
  )
  cuerpo = response.json()

  assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "VALIDACION_ERROR"
  assert cuerpo["data"] is None


@pytest.mark.asyncio
async def test_endpoint_actualizar_pedido_con_unidades_cero_devuelve_422(
  client: AsyncClient,
  pedido_service: PedidoService,
  cliente_service: ClienteService,
  proveedor_service: ProveedorService,
) -> None:
  cliente = await cliente_service.registrar_cliente(ClienteCreate(nombre="Cliente"))
  proveedor = await proveedor_service.registrar_proveedor(ProveedorCreate(nombre="Proveedor"))
  pedido = await pedido_service.registrar_pedido(
    PedidoCreate(
      producto="Producto original",
      unidades=1,
      cliente_id=cliente.id,
      proveedor_id=proveedor.id,
    ),
  )

  response = await client.put(
    f"{PEDIDOS_URL}{pedido.id}",
    json={
      "producto": "Producto actualizado",
      "unidades": 0,
      "cliente_id": cliente.id,
      "proveedor_id": proveedor.id,
    },
  )
  cuerpo = response.json()

  assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "VALIDACION_ERROR"
  assert cuerpo["data"] is None


@pytest.mark.asyncio
async def test_endpoint_actualizar_pedido_con_cliente_inexistente_devuelve_404(
  client: AsyncClient,
  pedido_service: PedidoService,
  cliente_service: ClienteService,
  proveedor_service: ProveedorService,
) -> None:
  cliente = await cliente_service.registrar_cliente(ClienteCreate(nombre="Cliente"))
  proveedor = await proveedor_service.registrar_proveedor(ProveedorCreate(nombre="Proveedor"))
  pedido = await pedido_service.registrar_pedido(
    PedidoCreate(
      producto="Producto original",
      unidades=1,
      cliente_id=cliente.id,
      proveedor_id=proveedor.id,
    ),
  )

  response = await client.put(
    f"{PEDIDOS_URL}{pedido.id}",
    json={
      "producto": "Producto actualizado",
      "unidades": 2,
      "cliente_id": 999999,
      "proveedor_id": proveedor.id,
    },
  )
  cuerpo = response.json()

  assert response.status_code == status.HTTP_404_NOT_FOUND
  assert cuerpo["message"] == "Cliente con ID 999999 no encontrado"
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "CLIENTE_NO_ENCONTRADO"
  assert cuerpo["data"] is None


@pytest.mark.asyncio
async def test_endpoint_actualizar_pedido_con_proveedor_inexistente_devuelve_404(
  client: AsyncClient,
  pedido_service: PedidoService,
  cliente_service: ClienteService,
  proveedor_service: ProveedorService,
) -> None:
  cliente = await cliente_service.registrar_cliente(ClienteCreate(nombre="Cliente"))
  proveedor = await proveedor_service.registrar_proveedor(ProveedorCreate(nombre="Proveedor"))
  pedido = await pedido_service.registrar_pedido(
    PedidoCreate(
      producto="Producto original",
      unidades=1,
      cliente_id=cliente.id,
      proveedor_id=proveedor.id,
    ),
  )

  response = await client.put(
    f"{PEDIDOS_URL}{pedido.id}",
    json={
      "producto": "Producto actualizado",
      "unidades": 2,
      "cliente_id": cliente.id,
      "proveedor_id": 999999,
    },
  )
  cuerpo = response.json()

  assert response.status_code == status.HTTP_404_NOT_FOUND
  assert cuerpo["message"] == "Proveedor con ID 999999 no encontrado"
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "PROVEEDOR_NO_ENCONTRADO"
  assert cuerpo["data"] is None


@pytest.mark.parametrize("pedido_id", ["0", "-1", "no-es-entero"])
@pytest.mark.asyncio
async def test_endpoint_actualizar_pedido_con_id_invalido_devuelve_422(client: AsyncClient,  pedido_id: str) -> None:
  response = await client.put(
    f"{PEDIDOS_URL}{pedido_id}",
    json={
      "producto": "Producto de prueba",
      "unidades": 1,
      "cliente_id": 1,
      "proveedor_id": 1,
    },
  )
  cuerpo = response.json()

  assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "VALIDACION_ERROR"
  assert cuerpo["data"] is None


@pytest.mark.parametrize(
  ("campo", "valor"),
  [("oferta", "O" * 26), ("observaciones", "O" * 1001)],
  ids=["oferta-supera-25", "observaciones-supera-1000"],
)
@pytest.mark.asyncio
async def test_endpoint_actualizar_pedido_rechaza_campos_que_superan_longitud_maxima(
  client: AsyncClient,
  pedido_service: PedidoService,
  cliente_service: ClienteService,
  proveedor_service: ProveedorService,
  campo: str,
  valor: str,
) -> None:
  cliente = await cliente_service.registrar_cliente(ClienteCreate(nombre="Cliente"))
  proveedor = await proveedor_service.registrar_proveedor(ProveedorCreate(nombre="Proveedor"))
  pedido = await pedido_service.registrar_pedido(
    PedidoCreate(
      producto="Producto original",
      unidades=1,
      cliente_id=cliente.id,
      proveedor_id=proveedor.id,
    ),
  )

  response = await client.put(
    f"{PEDIDOS_URL}{pedido.id}",
    json={
      "producto": "Producto actualizado",
      "unidades": 2,
      "cliente_id": cliente.id,
      "proveedor_id": proveedor.id,
      campo: valor,
    },
  )
  cuerpo = response.json()

  assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "VALIDACION_ERROR"
  assert cuerpo["data"] is None


@pytest.mark.asyncio
async def test_endpoint_actualizar_pedido_acepta_longitudes_maximas_de_oferta_y_observaciones(
  client: AsyncClient,
  pedido_service: PedidoService,
  cliente_service: ClienteService,
  proveedor_service: ProveedorService,
) -> None:
  cliente = await cliente_service.registrar_cliente(ClienteCreate(nombre="Cliente"))
  proveedor = await proveedor_service.registrar_proveedor(ProveedorCreate(nombre="Proveedor"))
  pedido = await pedido_service.registrar_pedido(
    PedidoCreate(
      producto="Producto original",
      unidades=1,
      cliente_id=cliente.id,
      proveedor_id=proveedor.id,
    ),
  )
  oferta = "O" * 25
  observaciones = "X" * 1000

  response = await client.put(
    f"{PEDIDOS_URL}{pedido.id}",
    json={
      "producto": "Producto actualizado",
      "unidades": 2,
      "oferta": oferta,
      "observaciones": observaciones,
      "cliente_id": cliente.id,
      "proveedor_id": proveedor.id,
    },
  )
  cuerpo = response.json()

  assert response.status_code == status.HTTP_200_OK
  assert cuerpo["data"]["oferta"] == oferta
  assert cuerpo["data"]["observaciones"] == observaciones


@pytest.mark.parametrize("unidades", ["dos", 1.5], ids=["texto", "decimal-fraccionario"])
@pytest.mark.asyncio
async def test_endpoint_actualizar_pedido_rechaza_unidades_con_tipo_invalido(
  client: AsyncClient,
  pedido_service: PedidoService,
  cliente_service: ClienteService,
  proveedor_service: ProveedorService,
  unidades: str | float,
) -> None:
  cliente = await cliente_service.registrar_cliente(ClienteCreate(nombre="Cliente"))
  proveedor = await proveedor_service.registrar_proveedor(ProveedorCreate(nombre="Proveedor"))
  pedido = await pedido_service.registrar_pedido(
    PedidoCreate(
      producto="Producto original",
      unidades=1,
      cliente_id=cliente.id,
      proveedor_id=proveedor.id,
    ),
  )

  response = await client.put(
    f"{PEDIDOS_URL}{pedido.id}",
    json={
      "producto": "Producto actualizado",
      "unidades": unidades,
      "cliente_id": cliente.id,
      "proveedor_id": proveedor.id,
    },
  )
  cuerpo = response.json()

  assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "VALIDACION_ERROR"
  assert cuerpo["data"] is None


@pytest.mark.parametrize("campo_id", ["cliente_id", "proveedor_id"])
@pytest.mark.asyncio
async def test_endpoint_actualizar_pedido_con_referencia_inexistente_no_modifica_pedido(
  client: AsyncClient,
  pedido_service: PedidoService,
  cliente_service: ClienteService,
  proveedor_service: ProveedorService,
  campo_id: str,
) -> None:
  cliente = await cliente_service.registrar_cliente(ClienteCreate(nombre="Cliente"))
  proveedor = await proveedor_service.registrar_proveedor(ProveedorCreate(nombre="Proveedor"))
  pedido = await pedido_service.registrar_pedido(
    PedidoCreate(
      producto="Producto original",
      unidades=1,
      cliente_id=cliente.id,
      proveedor_id=proveedor.id,
    ),
  )
  datos_actualizacion = {
    "producto": "Producto actualizado",
    "unidades": 2,
    "cliente_id": cliente.id,
    "proveedor_id": proveedor.id,
  }
  datos_actualizacion[campo_id] = 999999

  response = await client.put(f"{PEDIDOS_URL}{pedido.id}", json=datos_actualizacion)
  consulta = await client.get(f"{PEDIDOS_URL}{pedido.id}")
  cuerpo = consulta.json()

  assert response.status_code == status.HTTP_404_NOT_FOUND
  assert consulta.status_code == status.HTTP_200_OK
  assert cuerpo["data"]["producto"] == "Producto original"
  assert cuerpo["data"]["unidades"] == 1
  assert cuerpo["data"]["cliente_id"] == cliente.id
  assert cuerpo["data"]["proveedor_id"] == proveedor.id


