import pytest
from httpx import AsyncClient
from fastapi import status

from app.utils.messages import Mensajes
from app.services.cliente_service import ClienteService
from app.core.config import settings

CLIENTES_URL = "/api/v1/clientes/"

@pytest.mark.asyncio
async def test_endpoint_crear_cliente_devuelve_201(client: AsyncClient, cliente_service: ClienteService) -> None:
  response = await client.post(CLIENTES_URL, json={"nombre": "  cliente  "})

  cuerpo = response.json()

  assert response.status_code == status.HTTP_201_CREATED
  assert cuerpo["message"] == Mensajes.CLIENTE_CREADO
  assert cuerpo["success"] is True
  assert cuerpo["data"]["nombre"] == "CLIENTE"
  assert cuerpo["data"]["id"] is not None
  assert await cliente_service.contar_todos() == 1

@pytest.mark.asyncio
async def test_endpoint_crear_cliente_duplicado_devuelve_409(client: AsyncClient, cliente_service: ClienteService) -> None:
  primera_respuesta = await client.post(CLIENTES_URL, json={"nombre": "Cliente"})
  assert primera_respuesta.status_code == status.HTTP_201_CREATED

  response = await client.post(CLIENTES_URL, json={"nombre": "  CLIENTE  "})

  cuerpo = response.json()
  
  assert response.status_code == status.HTTP_409_CONFLICT
  assert cuerpo["message"] == "El cliente 'CLIENTE' ya existe en la base de datos" 
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "CLIENTE_YA_EXISTE"
  assert cuerpo["data"] is None
  assert await cliente_service.contar_todos() == 1

@pytest.mark.asyncio
async def test_endpoint_crear_cliente_nombre_largo_devuelve_422(client: AsyncClient) -> None:
  response = await client.post(CLIENTES_URL, json={"nombre": "A" * 256})

  cuerpo = response.json()

  assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  assert cuerpo["message"] == Mensajes.CLIENTE_NOMBRE_DEMASIADO_LARGO
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "NOMBRE_INVALIDO"
  assert cuerpo["data"] is None

@pytest.mark.asyncio
async def test_endpoint_crear_cliente_nombre_en_blanco_devuelve_400(client: AsyncClient) -> None:
  response = await client.post(CLIENTES_URL, json={"nombre": "   "})

  cuerpo = response.json()

  assert response.status_code == status.HTTP_400_BAD_REQUEST
  assert cuerpo["message"] == Mensajes.CLIENTE_NOMBRE_VACIO
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "NOMBRE_INVALIDO"
  assert cuerpo["data"] is None

@pytest.mark.asyncio
async def test_endpoint_listar_clientes_vacio_devuelve_lista_vacia(client: AsyncClient) -> None:
  response = await client.get(CLIENTES_URL)

  cuerpo = response.json()

  assert response.status_code == status.HTTP_200_OK
  assert cuerpo["success"] is True
  assert cuerpo["data"]["clientes"] == []
  assert cuerpo["data"]["paginacion"]["total"] == 0
  assert cuerpo["data"]["paginacion"]["hay_mas"] is False

@pytest.mark.asyncio
async def test_endpoint_listar_clientes_respeta_paginacion(client: AsyncClient) -> None:
  for nombre in ("Alf", "Beta", "Gamma"):
    await client.post(CLIENTES_URL, json={"nombre": nombre})

  response = await client.get(CLIENTES_URL, params={"skip": 1, "limit": 1})

  cuerpo = response.json()

  assert response.status_code == status.HTTP_200_OK
  assert [p["nombre"] for p in cuerpo["data"]["clientes"]] == ["BETA"]
  assert cuerpo["data"]["paginacion"]["total"] == 3
  assert cuerpo["data"]["paginacion"]["skip"] == 1
  assert cuerpo["data"]["paginacion"]["limit"] == 1
  assert cuerpo["data"]["paginacion"]["hay_mas"] is True

@pytest.mark.asyncio
async def test_endpoint_obtener_cliente_por_id_devuelve_200(client: AsyncClient) -> None:
  resultado = await client.post(CLIENTES_URL, json={"nombre": "Cliente"})
  cliente_id = resultado.json()["data"]["id"]

  response = await client.get(f"{CLIENTES_URL}{cliente_id}")

  cuerpo = response.json()

  assert response.status_code == status.HTTP_200_OK
  assert cuerpo["message"] == Mensajes.EXITO
  assert cuerpo["success"] is True
  assert cuerpo["data"]["id"] == cliente_id
  assert cuerpo["data"]["nombre"] == "CLIENTE"

@pytest.mark.asyncio
async def test_endpoint_obtener_cliente_id_no_numerico_devuelve_422(client: AsyncClient) -> None:
  response = await client.get(f"{CLIENTES_URL}abc")

  cuerpo = response.json()

  assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  assert cuerpo["message"] == "Los datos enviados no son válidos"
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "VALIDACION_ERROR"
  assert cuerpo["data"] is None

@pytest.mark.asyncio
async def test_endpoint_obtener_cliente_inexistente_devuelve_404(client: AsyncClient) -> None:
  response = await client.get(f"{CLIENTES_URL}999999")

  cuerpo = response.json()

  assert response.status_code == status.HTTP_404_NOT_FOUND
  assert cuerpo["message"] == "Cliente con ID 999999 no encontrado"
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "CLIENTE_NO_ENCONTRADO"
  assert cuerpo["data"] is None


@pytest.mark.asyncio
async def test_endpoint_actualizar_cliente_normaliza_nombre(client: AsyncClient) -> None:
  alta = await client.post(CLIENTES_URL, json={"nombre": "Cliente"})
  cliente_id = alta.json()["data"]["id"]

  response = await client.put(f"{CLIENTES_URL}{cliente_id}", json={"nombre": "  nuevo cliente  "})

  cuerpo = response.json()

  assert response.status_code == status.HTTP_200_OK
  assert cuerpo["message"] == Mensajes.CLIENTE_ACTUALIZADO
  assert cuerpo["success"] is True
  assert cuerpo["data"]["id"] == cliente_id
  assert cuerpo["data"]["nombre"] == "NUEVO CLIENTE"

@pytest.mark.asyncio
async def test_endpoint_actualizar_cliente_con_nombre_duplicado_devuelve_409(client: AsyncClient) -> None:
  await client.post(CLIENTES_URL, json={"nombre": "Cliente A"})
  alta_b = await client.post(CLIENTES_URL, json={"nombre": "Cliente B"})
  cliente_b_id = alta_b.json()["data"]["id"]

  response = await client.put(f"{CLIENTES_URL}{cliente_b_id}", json={"nombre": "  cliente a  "})

  cuerpo = response.json()

  assert response.status_code == status.HTTP_409_CONFLICT
  assert cuerpo["message"] == "El cliente 'CLIENTE A' ya existe en la base de datos"
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "CLIENTE_YA_EXISTE"
  assert cuerpo["data"] is None

  cliente_b = await client.get(f"{CLIENTES_URL}{cliente_b_id}")
  assert cliente_b.json()["data"]["nombre"] == "CLIENTE B"

@pytest.mark.asyncio
async def test_endpoint_actualizar_cliente_inexistente_devuelve_404(client: AsyncClient) -> None:
  response = await client.put(f"{CLIENTES_URL}999999", json={"nombre": "Cliente"})

  cuerpo = response.json()

  assert response.status_code == status.HTTP_404_NOT_FOUND
  assert cuerpo["message"] == "Cliente con ID 999999 no encontrado"
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "CLIENTE_NO_ENCONTRADO"
  assert cuerpo["data"] is None

@pytest.mark.asyncio
async def test_endpoint_actualizar_cliente_nombre_vacio_devuelve_400(client: AsyncClient) -> None:
  alta = await client.post(CLIENTES_URL, json={"nombre": "Cliente"})
  cliente_id = alta.json()["data"]["id"]

  response = await client.put(f"{CLIENTES_URL}{cliente_id}", json={"nombre": "   "})

  cuerpo = response.json()

  assert response.status_code == status.HTTP_400_BAD_REQUEST
  assert cuerpo["message"] == "El nombre de un cliente no puede estar vacío"
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "NOMBRE_INVALIDO"
  assert cuerpo["data"] is None

  cliente = await client.get(f"{CLIENTES_URL}{cliente_id}")
  assert cliente.json()["data"]["nombre"] == "CLIENTE"