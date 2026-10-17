import pytest
from unittest.mock import AsyncMock
from sqlalchemy.exc import IntegrityError
from fastapi import status
from pydantic import ValidationError
from app.exceptions.custom_errors import ProveedorNombreInvalidoError, ProveedorYaExisteError, ProveedorNoEncontradoError
from app.schemas.proveedor_schema import ProveedorCreate
from app.utils.messages import Mensajes

# Clear-Host; pytest

@pytest.mark.asyncio
async def test_registrar_proveedor_guarda_nombre_normalizado(proveedor_service):  
  proveedor = await proveedor_service.registrar_proveedor(ProveedorCreate(nombre="   proveedor 1  "))

  assert proveedor.id is not None
  assert proveedor.nombre == "PROVEEDOR 1"
  assert await proveedor_service.contar_todos() == 1


@pytest.mark.asyncio
async def test_registrar_proveedor_rechaza_nombre_vacio(proveedor_service):  
  with pytest.raises(ProveedorNombreInvalidoError) as exc:
    await proveedor_service.registrar_proveedor(ProveedorCreate(nombre="   "))

  assert await proveedor_service.contar_todos() == 0
  assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
  assert exc.value.error_code == "NOMBRE_INVALIDO"
  assert exc.value.detail == Mensajes.PROVEEDOR_NOMBRE_VACIO


def test_proveedor_create_rechaza_nombre_mayor_de_255_caracteres():
  with pytest.raises(ValidationError) as exc:
    ProveedorCreate(nombre="A" * 256)

  error = exc.value.errors()[0]
  assert error["loc"] == ("nombre",)
  assert error["type"] == "string_too_long"

@pytest.mark.asyncio
async def test_registrar_proveedor_acepta_nombre_de_255_caracteres(proveedor_service):
  nombre = "A" * 255

  proveedor = await proveedor_service.registrar_proveedor(ProveedorCreate(nombre=nombre))

  assert proveedor.id is not None
  assert proveedor.nombre == nombre
  assert len(proveedor.nombre) == 255
  assert await proveedor_service.contar_todos() == 1

@pytest.mark.asyncio
async def test_registrar_proveedor_rechaza_nombre_vacio(proveedor_service):
  with pytest.raises(ProveedorNombreInvalidoError) as exc:
    await proveedor_service.registrar_proveedor(ProveedorCreate(nombre=""))

  assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
  assert exc.value.error_code == "NOMBRE_INVALIDO"
  assert exc.value.detail == Mensajes.PROVEEDOR_NOMBRE_VACIO
  assert await proveedor_service.contar_todos() == 0


@pytest.mark.asyncio
async def test_registrar_proveedor_rechaza_nombre_duplicado(proveedor_service):
  await proveedor_service.registrar_proveedor(ProveedorCreate(nombre="Proveedor"))

  with pytest.raises(ProveedorYaExisteError) as exc:
    await proveedor_service.registrar_proveedor(ProveedorCreate(nombre="  PROVEEDOR  "))

  assert exc.value.status_code == status.HTTP_409_CONFLICT
  assert exc.value.error_code == "PROVEEDOR_YA_EXISTE"
  assert await proveedor_service.contar_todos() == 1


@pytest.mark.asyncio
async def test_registrar_proveedor_convierte_integrity_error_en_duplicado(proveedor_service):
  proveedor_service.db.flush = AsyncMock(
    side_effect=IntegrityError(
      "INSERT",
      {},
      Exception("UNIQUE constraint failed"),
      )
  )
  proveedor_service.db.rollback = AsyncMock()

  with pytest.raises(ProveedorYaExisteError) as exc:
    await proveedor_service.registrar_proveedor(ProveedorCreate(nombre="Proveedor"))

  assert exc.value.error_code == "PROVEEDOR_YA_EXISTE"
  proveedor_service.db.rollback.assert_awaited_once()

@pytest.mark.asyncio
async def test_obtener_por_id_devuelve_proveedor_existente(proveedor_service):
  proveedor_creado = await proveedor_service.registrar_proveedor(ProveedorCreate(nombre="Proveedor"))

  proveedor = await proveedor_service.obtener_por_id(proveedor_creado.id)

  assert proveedor.id == proveedor_creado.id
  assert proveedor.nombre == "PROVEEDOR"

@pytest.mark.asyncio
async def test_obtener_por_id_inexistente_lanza_error(proveedor_service):
  with pytest.raises(ProveedorNoEncontradoError) as exc:
    await proveedor_service.obtener_por_id(999)

  assert exc.value.status_code == status.HTTP_404_NOT_FOUND
  assert exc.value.error_code == "PROVEEDOR_NO_ENCONTRADO"

@pytest.mark.asyncio
async def test_obtener_por_nombre_normaliza_minusculas_y_espacios(proveedor_service):
  proveedor_creado = await proveedor_service.registrar_proveedor(ProveedorCreate(nombre="Proveedor"))

  proveedor = await proveedor_service.obtener_por_nombre("  proveedor  ")

  assert proveedor is not None
  assert proveedor.id == proveedor_creado.id
  assert proveedor.nombre == "PROVEEDOR"

@pytest.mark.asyncio
async def test_obtener_todos_ordena_y_respeta_skip_y_limit(proveedor_service):
  for nombre in ("Zeta", "Beta", "Alfa"):
    await proveedor_service.registrar_proveedor(ProveedorCreate(nombre=nombre))

  proveedores = await proveedor_service.obtener_todos(skip=1, limit=1)

  assert [proveedor.nombre for proveedor in proveedores] == ["BETA"]

@pytest.mark.asyncio
async def test_actualizar_proveedor_cambia_y_normaliza_nombre(proveedor_service):
  proveedor = await proveedor_service.registrar_proveedor(ProveedorCreate(nombre="Proveedor"))

  actualizado = await proveedor_service.actualizar_proveedor(
    proveedor.id,
    ProveedorCreate(nombre="  nueva empresa  "),
  )

  assert actualizado.id == proveedor.id
  assert actualizado.nombre == "NUEVA EMPRESA"

@pytest.mark.asyncio
async def test_actualizar_proveedor_ignora_mismo_nombre_con_otra_capitalizacion(proveedor_service):
  proveedor = await proveedor_service.registrar_proveedor(ProveedorCreate(nombre="Proveedor"))

  actualizado = await proveedor_service.actualizar_proveedor(
    proveedor.id,
    ProveedorCreate(nombre="  proVeeDor  "),
  )

  assert actualizado.id == proveedor.id
  assert actualizado.nombre == "PROVEEDOR"
  assert await proveedor_service.contar_todos() == 1

@pytest.mark.asyncio
async def test_actualizar_proveedor_rechaza_nombre_de_otro_proveedor(proveedor_service):
  primero = await proveedor_service.registrar_proveedor(ProveedorCreate(nombre="Proveedor"))
  segundo = await proveedor_service.registrar_proveedor(ProveedorCreate(nombre="Beta"))

  with pytest.raises(ProveedorYaExisteError) as exc:
    await proveedor_service.actualizar_proveedor(
      segundo.id,
      ProveedorCreate(nombre="  proveedor  "),
    )

  assert exc.value.status_code == status.HTTP_409_CONFLICT
  assert exc.value.error_code == "PROVEEDOR_YA_EXISTE"
  assert await proveedor_service.obtener_por_id(segundo.id) == segundo
  assert await proveedor_service.contar_todos() == 2