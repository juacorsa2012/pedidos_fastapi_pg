import pytest
from httpx import AsyncClient
from fastapi import status

from app.utils.messages import Mensajes
from app.services.proveedor_service import ProveedorService
from app.core.config import settings

PROVEEDORES_URL = "/api/v1/proveedores/"

@pytest.mark.asyncio
async def test_endpoint_crear_proveedor_devuelve_201(client: AsyncClient, proveedor_service: ProveedorService) -> None:
  response = await client.post(PROVEEDORES_URL, json={"nombre": "  proveedor  "})

  cuerpo = response.json()

  assert response.status_code == status.HTTP_201_CREATED
  assert cuerpo["message"] == Mensajes.PROVEEDOR_CREADO
  assert cuerpo["success"] is True
  assert cuerpo["data"]["nombre"] == "PROVEEDOR"
  assert cuerpo["data"]["id"] is not None
  assert await proveedor_service.contar_todos() == 1

@pytest.mark.asyncio
async def test_endpoint_crear_proveedor_duplicado_devuelve_409(client: AsyncClient, proveedor_service: ProveedorService) -> None:
  primera_respuesta = await client.post(
    PROVEEDORES_URL,
    json={"nombre": "Proveedor"},
  )
  assert primera_respuesta.status_code == status.HTTP_201_CREATED

  response = await client.post(
    PROVEEDORES_URL,
    json={"nombre": "  PROVEEDOR  "},
  )

  cuerpo = response.json()
  
  assert response.status_code == status.HTTP_409_CONFLICT
  assert cuerpo["message"] == "El proveedor 'PROVEEDOR' ya existe en la base de datos" 
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "PROVEEDOR_YA_EXISTE"
  assert cuerpo["data"] is None
  assert await proveedor_service.contar_todos() == 1

@pytest.mark.asyncio
async def test_endpoint_crear_proveedor_nombre_largo_devuelve_422(client: AsyncClient) -> None:
  response = await client.post(PROVEEDORES_URL, json={"nombre": "A" * 256})

  cuerpo = response.json()

  assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  assert cuerpo["message"] == "El nombre no puede superar los 255 caracteres"
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "NOMBRE_INVALIDO"
  assert cuerpo["data"] is None

@pytest.mark.asyncio
async def test_endpoint_crear_proveedor_nombre_en_blanco_devuelve_400(client: AsyncClient) -> None:
  response = await client.post(PROVEEDORES_URL, json={"nombre": "   "})

  cuerpo = response.json()

  assert response.status_code == status.HTTP_400_BAD_REQUEST
  assert cuerpo["message"] == "El nombre no puede estar vacío"
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "NOMBRE_INVALIDO"
  assert cuerpo["data"] is None


@pytest.mark.asyncio
async def test_endpoint_obtener_proveedor_inexistente_devuelve_404(client: AsyncClient) -> None:
  response = await client.get(f"{PROVEEDORES_URL}999999")

  cuerpo = response.json()

  assert response.status_code == status.HTTP_404_NOT_FOUND
  assert cuerpo["message"] == "Proveedor con ID 999999 no encontrado"
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "PROVEEDOR_NO_ENCONTRADO"
  assert cuerpo["data"] is None

@pytest.mark.asyncio
async def test_endpoint_listar_proveedores_vacio_devuelve_lista_vacia(client: AsyncClient) -> None:
  response = await client.get(PROVEEDORES_URL)

  cuerpo = response.json()

  assert response.status_code == status.HTTP_200_OK
  assert cuerpo["success"] is True
  assert cuerpo["data"]["proveedores"] == []
  assert cuerpo["data"]["paginacion"]["total"] == 0
  assert cuerpo["data"]["paginacion"]["hay_mas"] is False

@pytest.mark.asyncio
async def test_endpoint_listar_proveedores_respeta_paginacion(client: AsyncClient) -> None:
  for nombre in ("Alfa", "Beta", "Gamma"):
    await client.post(PROVEEDORES_URL, json={"nombre": nombre})

  response = await client.get(PROVEEDORES_URL, params={"skip": 1, "limit": 1})

  cuerpo = response.json()

  assert response.status_code == status.HTTP_200_OK
  assert [p["nombre"] for p in cuerpo["data"]["proveedores"]] == ["BETA"]
  assert cuerpo["data"]["paginacion"]["total"] == 3
  assert cuerpo["data"]["paginacion"]["skip"] == 1
  assert cuerpo["data"]["paginacion"]["limit"] == 1
  assert cuerpo["data"]["paginacion"]["hay_mas"] is True

@pytest.mark.asyncio
async def test_endpoint_obtener_proveedor_por_id_devuelve_200(client: AsyncClient) -> None:
  resultado = await client.post(PROVEEDORES_URL, json={"nombre": "Proveedor"})
  proveedor_id = resultado.json()["data"]["id"]

  response = await client.get(f"{PROVEEDORES_URL}{proveedor_id}")

  cuerpo = response.json()

  assert response.status_code == status.HTTP_200_OK
  assert cuerpo["success"] is True
  assert cuerpo["data"]["id"] == proveedor_id
  assert cuerpo["data"]["nombre"] == "PROVEEDOR"

@pytest.mark.asyncio
async def test_endpoint_actualizar_proveedor_normaliza_nombre(client: AsyncClient) -> None:
  alta = await client.post(PROVEEDORES_URL, json={"nombre": "Proveedor"})
  proveedor_id = alta.json()["data"]["id"]

  response = await client.put(f"{PROVEEDORES_URL}{proveedor_id}", json={"nombre": "  nuevo proveedor  "})

  cuerpo = response.json()

  assert response.status_code == status.HTTP_200_OK
  assert cuerpo["message"] == Mensajes.PROVEEDOR_ACTUALIZADO
  assert cuerpo["success"] is True
  assert cuerpo["data"]["id"] == proveedor_id
  assert cuerpo["data"]["nombre"] == "NUEVO PROVEEDOR"

@pytest.mark.asyncio
async def test_endpoint_actualizar_proveedor_con_nombre_duplicado_devuelve_409(client: AsyncClient) -> None:
    await client.post(PROVEEDORES_URL, json={"nombre": "Proveedor A"})
    alta_b = await client.post(PROVEEDORES_URL, json={"nombre": "Proveedor B"})
    proveedor_b_id = alta_b.json()["data"]["id"]

    response = await client.put(f"{PROVEEDORES_URL}{proveedor_b_id}", json={"nombre": "  proveedor a  "})

    cuerpo = response.json()

    assert response.status_code == status.HTTP_409_CONFLICT
    assert cuerpo["message"] == "El proveedor 'PROVEEDOR A' ya existe en la base de datos"    
    assert cuerpo["success"] is False
    assert cuerpo["error_code"] == "PROVEEDOR_YA_EXISTE"
    assert cuerpo["data"] is None

    proveedor_b = await client.get(f"{PROVEEDORES_URL}{proveedor_b_id}")
    assert proveedor_b.json()["data"]["nombre"] == "PROVEEDOR B"

@pytest.mark.asyncio
async def test_endpoint_actualizar_proveedor_inexistente_devuelve_404(client: AsyncClient) -> None:
  response = await client.put(f"{PROVEEDORES_URL}999999", json={"nombre": "Proveedor"})

  cuerpo = response.json()

  assert response.status_code == status.HTTP_404_NOT_FOUND
  assert cuerpo["message"] == "Proveedor con ID 999999 no encontrado"
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "PROVEEDOR_NO_ENCONTRADO"
  assert cuerpo["data"] is None

@pytest.mark.asyncio
async def test_endpoint_actualizar_proveedor_nombre_vacio_devuelve_400(client: AsyncClient) -> None:
  alta = await client.post(PROVEEDORES_URL, json={"nombre": "Proveedor"})
  proveedor_id = alta.json()["data"]["id"]

  response = await client.put(f"{PROVEEDORES_URL}{proveedor_id}", json={"nombre": "   "})

  cuerpo = response.json()

  assert response.status_code == status.HTTP_400_BAD_REQUEST
  assert cuerpo["message"] == "El nombre no puede estar vacío"
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "NOMBRE_INVALIDO"
  assert cuerpo["data"] is None

  proveedor = await client.get(f"{PROVEEDORES_URL}{proveedor_id}")
  assert proveedor.json()["data"]["nombre"] == "PROVEEDOR"

@pytest.mark.asyncio
async def test_endpoint_obtener_proveedor_id_no_numerico_devuelve_422(client: AsyncClient) -> None:
  response = await client.get(f"{PROVEEDORES_URL}abc")

  cuerpo = response.json()

  assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  assert cuerpo["message"] == "Los datos enviados no son válidos"
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "VALIDACION_ERROR"
  assert cuerpo["data"] is None

@pytest.mark.asyncio
async def test_endpoint_crear_proveedor_sin_nombre_devuelve_422(client: AsyncClient) -> None:
  response = await client.post(PROVEEDORES_URL, json={})

  cuerpo = response.json()

  assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  assert cuerpo["message"] == "Los datos enviados no son válidos"
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "VALIDACION_ERROR"
  assert cuerpo["data"] is None

@pytest.mark.asyncio
async def test_endpoint_crear_proveedor_nombre_no_es_texto_devuelve_422(client: AsyncClient) -> None:
  response = await client.post(PROVEEDORES_URL, json={"nombre": 123})

  cuerpo = response.json()

  assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  assert cuerpo["message"] == "Los datos enviados no son válidos"
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "VALIDACION_ERROR"
  assert cuerpo["data"] is None

@pytest.mark.asyncio
async def test_endpoint_listar_proveedores_limit_cero_devuelve_422(client: AsyncClient) -> None:
  response = await client.get(PROVEEDORES_URL, params={"limit": 0})

  cuerpo = response.json()

  assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  assert cuerpo["message"] == "Los datos enviados no son válidos"
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "VALIDACION_ERROR"
  assert cuerpo["data"] is None

@pytest.mark.asyncio
async def test_endpoint_listar_proveedores_skip_negativo_devuelve_422(client: AsyncClient) -> None:
  response = await client.get(PROVEEDORES_URL, params={"skip": -1})

  cuerpo = response.json()

  assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  assert cuerpo["message"] == "Los datos enviados no son válidos"
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "VALIDACION_ERROR"
  assert cuerpo["data"] is None

@pytest.mark.asyncio
async def test_endpoint_actualizar_proveedor_con_mismo_nombre_no_duplica(client: AsyncClient) -> None:
  alta = await client.post(PROVEEDORES_URL, json={"nombre": "Proveedor"})
  proveedor_id = alta.json()["data"]["id"]

  response = await client.put(f"{PROVEEDORES_URL}{proveedor_id}", json={"nombre": "  pROVEEDOR  "})

  resultado = await client.get(PROVEEDORES_URL)
  cuerpo = response.json()

  assert response.status_code == status.HTTP_200_OK
  assert cuerpo["data"]["id"] == proveedor_id
  assert cuerpo["data"]["nombre"] == "PROVEEDOR"
  assert resultado.json()["data"]["paginacion"]["total"] == 1

@pytest.mark.asyncio
async def test_endpoint_actualizar_proveedor_nombre_largo_devuelve_422(client: AsyncClient) -> None:
  alta = await client.post(PROVEEDORES_URL, json={"nombre": "Proveedor"})
  proveedor_id = alta.json()["data"]["id"]

  response = await client.put(f"{PROVEEDORES_URL}{proveedor_id}", json={"nombre": "A" * 256})
  cuerpo = response.json()

  assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  assert cuerpo["message"] == "El nombre no puede superar los 255 caracteres"
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "NOMBRE_INVALIDO"
  assert cuerpo["data"] is None

  consulta = await client.get(f"{PROVEEDORES_URL}{proveedor_id}")
  assert consulta.json()["data"]["nombre"] == "PROVEEDOR"

@pytest.mark.asyncio
async def test_endpoint_listar_proveedores_skip_supera_total_devuelve_vacio(client: AsyncClient) -> None:
  await client.post(PROVEEDORES_URL, json={"nombre": "Proveedor A"})
  await client.post(PROVEEDORES_URL, json={"nombre": "Proveedor B"})

  response = await client.get(PROVEEDORES_URL, params={"skip": 10, "limit": 5})
  cuerpo = response.json()

  assert response.status_code == status.HTTP_200_OK
  assert cuerpo["data"]["proveedores"] == []
  assert cuerpo["data"]["paginacion"]["total"] == 2
  assert cuerpo["data"]["paginacion"]["skip"] == 10
  assert cuerpo["data"]["paginacion"]["hay_mas"] is False


@pytest.mark.asyncio
async def test_endpoint_obtener_proveedor_id_negativo_devuelve_404(client: AsyncClient) -> None:
  response = await client.get(f"{PROVEEDORES_URL}-1")
  
  cuerpo = response.json()

  assert response.status_code == status.HTTP_404_NOT_FOUND
  assert cuerpo["message"] == "Proveedor con ID -1 no encontrado"
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "PROVEEDOR_NO_ENCONTRADO"
  assert cuerpo["data"] is None


@pytest.mark.asyncio
async def test_endpoint_listar_proveedores_devuelve_orden_alfabetico(client: AsyncClient) -> None:
  for nombre in ("Gamma", "Alfa", "Beta"):
    await client.post(PROVEEDORES_URL, json={"nombre": nombre})

  response = await client.get(PROVEEDORES_URL)
  
  cuerpo = response.json()

  assert response.status_code == status.HTTP_200_OK
  assert [
    proveedor["nombre"]
    for proveedor in cuerpo["data"]["proveedores"]
  ] == ["ALFA", "BETA", "GAMMA"]
  assert cuerpo["data"]["paginacion"]["total"] == 3

@pytest.mark.asyncio
async def test_endpoint_crear_proveedor_acepta_nombre_de_255_caracteres(client: AsyncClient) -> None:
  nombre = "A" * 255

  response = await client.post(PROVEEDORES_URL, json={"nombre": nombre})
  cuerpo = response.json()

  assert response.status_code == status.HTTP_201_CREATED
  assert cuerpo["success"] is True
  assert cuerpo["data"]["nombre"] == nombre
  assert len(cuerpo["data"]["nombre"]) == 255


@pytest.mark.asyncio
async def test_endpoint_listar_proveedores_rechaza_limit_superior_al_maximo(client: AsyncClient) -> None:
  response = await client.get(
    PROVEEDORES_URL,
    params={"limit": settings.PAGINACION_LIMITE_MAXIMO + 1},
  )
  cuerpo = response.json()

  assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  assert cuerpo["message"] == "Los datos enviados no son válidos"
  assert cuerpo["success"] is False
  assert cuerpo["error_code"] == "VALIDACION_ERROR"
  assert cuerpo["data"] is None


@pytest.mark.asyncio
async def test_endpoint_listar_proveedores_ultima_pagina_no_tiene_mas(client: AsyncClient) -> None:
  for nombre in ("Alfa", "Beta", "Gamma"):
    await client.post(PROVEEDORES_URL, json={"nombre": nombre})

  response = await client.get(PROVEEDORES_URL, params={"skip": 2, "limit": 1})
  cuerpo = response.json()

  assert response.status_code == status.HTTP_200_OK
  assert [p["nombre"] for p in cuerpo["data"]["proveedores"]] == ["GAMMA"]
  assert cuerpo["data"]["paginacion"]["total"] == 3
  assert cuerpo["data"]["paginacion"]["hay_mas"] is False
