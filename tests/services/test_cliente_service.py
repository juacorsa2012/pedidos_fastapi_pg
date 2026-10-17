import pytest
from unittest.mock import AsyncMock
from sqlalchemy.exc import IntegrityError
from fastapi import status
from pydantic import ValidationError

from app.exceptions.custom_errors import (
  ClienteNombreInvalidoError,
  ClienteNoEncontradoError,
  ClienteYaExisteError,
)
from app.schemas.cliente_schema import ClienteCreate
from app.utils.messages import Mensajes


@pytest.mark.asyncio
async def test_registrar_cliente_guarda_nombre_normalizado(cliente_service):
  cliente = await cliente_service.registrar_cliente(ClienteCreate(nombre="   cliente 1  "))

  assert cliente.id is not None
  assert cliente.nombre == "CLIENTE 1"
  assert await cliente_service.contar_todos() == 1


@pytest.mark.asyncio
async def test_registrar_cliente_rechaza_nombre_vacio(cliente_service):
  with pytest.raises(ClienteNombreInvalidoError) as exc:
    await cliente_service.registrar_cliente(ClienteCreate(nombre="   "))

  assert await cliente_service.contar_todos() == 0
  assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
  assert exc.value.error_code == "NOMBRE_INVALIDO"
  assert exc.value.detail == Mensajes.CLIENTE_NOMBRE_VACIO


def test_cliente_create_rechaza_nombre_mayor_de_255_caracteres():
  with pytest.raises(ValidationError) as exc:
    ClienteCreate(nombre="A" * 256)

  error = exc.value.errors()[0]
  assert error["loc"] == ("nombre",)
  assert error["type"] == "string_too_long"


@pytest.mark.asyncio
async def test_registrar_cliente_acepta_nombre_de_255_caracteres(cliente_service):
  nombre = "A" * 255

  cliente = await cliente_service.registrar_cliente(ClienteCreate(nombre=nombre))

  assert cliente.id is not None
  assert cliente.nombre == nombre
  assert len(cliente.nombre) == 255
  assert await cliente_service.contar_todos() == 1


@pytest.mark.asyncio
async def test_registrar_cliente_rechaza_nombre_vacio_string_vacio(cliente_service):
  with pytest.raises(ClienteNombreInvalidoError) as exc:
    await cliente_service.registrar_cliente(ClienteCreate(nombre=""))

  assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
  assert exc.value.error_code == "NOMBRE_INVALIDO"
  assert exc.value.detail == Mensajes.CLIENTE_NOMBRE_VACIO
  assert await cliente_service.contar_todos() == 0


@pytest.mark.asyncio
async def test_registrar_cliente_rechaza_nombre_duplicado(cliente_service):
  await cliente_service.registrar_cliente(ClienteCreate(nombre="Cliente"))

  with pytest.raises(ClienteYaExisteError) as exc:
    await cliente_service.registrar_cliente(ClienteCreate(nombre="  CLIENTE  "))

  assert exc.value.status_code == status.HTTP_409_CONFLICT
  assert exc.value.error_code == "CLIENTE_YA_EXISTE"
  assert await cliente_service.contar_todos() == 1


@pytest.mark.asyncio
async def test_registrar_cliente_convierte_integrity_error_en_duplicado(cliente_service):
  cliente_service.db.flush = AsyncMock(
    side_effect=IntegrityError(
      "INSERT",
      {},
      Exception("UNIQUE constraint failed"),
    )
  )
  cliente_service.db.rollback = AsyncMock()

  with pytest.raises(ClienteYaExisteError) as exc:
    await cliente_service.registrar_cliente(ClienteCreate(nombre="Cliente"))

  assert exc.value.error_code == "CLIENTE_YA_EXISTE"
  cliente_service.db.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_obtener_por_id_devuelve_cliente_existente(cliente_service):
  cliente_creado = await cliente_service.registrar_cliente(ClienteCreate(nombre="Cliente"))

  cliente = await cliente_service.obtener_por_id(cliente_creado.id)

  assert cliente.id == cliente_creado.id
  assert cliente.nombre == "CLIENTE"


@pytest.mark.asyncio
async def test_obtener_por_id_inexistente_lanza_error(cliente_service):
  with pytest.raises(ClienteNoEncontradoError) as exc:
    await cliente_service.obtener_por_id(999)

  assert exc.value.status_code == status.HTTP_404_NOT_FOUND
  assert exc.value.error_code == "CLIENTE_NO_ENCONTRADO"


@pytest.mark.asyncio
async def test_obtener_por_nombre_normaliza_minusculas_y_espacios(cliente_service):
  cliente_creado = await cliente_service.registrar_cliente(ClienteCreate(nombre="Cliente"))

  cliente = await cliente_service.obtener_por_nombre("  cliente  ")

  assert cliente is not None
  assert cliente.id == cliente_creado.id
  assert cliente.nombre == "CLIENTE"


@pytest.mark.asyncio
async def test_obtener_todos_ordena_y_respeta_skip_y_limit(cliente_service):
  for nombre in ("Zeta", "Beta", "Alfa"):
    await cliente_service.registrar_cliente(ClienteCreate(nombre=nombre))

  clientes = await cliente_service.obtener_todos(skip=1, limit=1)

  assert [cliente.nombre for cliente in clientes] == ["BETA"]


@pytest.mark.asyncio
async def test_actualizar_cliente_cambia_y_normaliza_nombre(cliente_service):
  cliente = await cliente_service.registrar_cliente(ClienteCreate(nombre="Cliente"))

  actualizado = await cliente_service.actualizar_cliente(
    cliente.id,
    ClienteCreate(nombre="  nueva empresa  "),
  )

  assert actualizado.id == cliente.id
  assert actualizado.nombre == "NUEVA EMPRESA"


@pytest.mark.asyncio
async def test_actualizar_cliente_ignora_mismo_nombre_con_otra_capitalizacion(cliente_service):
  cliente = await cliente_service.registrar_cliente(ClienteCreate(nombre="Cliente"))

  actualizado = await cliente_service.actualizar_cliente(
    cliente.id,
    ClienteCreate(nombre="  clIente  "),
  )

  assert actualizado.id == cliente.id
  assert actualizado.nombre == "CLIENTE"
  assert await cliente_service.contar_todos() == 1


@pytest.mark.asyncio
async def test_actualizar_cliente_rechaza_nombre_de_otro_cliente(cliente_service):
  await cliente_service.registrar_cliente(ClienteCreate(nombre="Cliente"))
  segundo = await cliente_service.registrar_cliente(ClienteCreate(nombre="Beta"))

  with pytest.raises(ClienteYaExisteError) as exc:
    await cliente_service.actualizar_cliente(
      segundo.id,
      ClienteCreate(nombre="  cliente  "),
    )

  assert exc.value.status_code == status.HTTP_409_CONFLICT
  assert exc.value.error_code == "CLIENTE_YA_EXISTE"
  assert await cliente_service.obtener_por_id(segundo.id) == segundo
  assert await cliente_service.contar_todos() == 2
