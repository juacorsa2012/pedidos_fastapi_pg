import os
import sys
from collections.abc import AsyncIterator
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

# Configurar el entorno antes de importar módulos que cargan Settings.
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ.setdefault("API_DESCRIPCION", "Entorno de pruebas")
os.environ.setdefault("API_VERSION", "test")
os.environ.setdefault("PORT", "8000")

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.dependencies import get_proveedor_service, get_cliente_service, get_pedido_service
from app.models import Cliente, Pedido, Proveedor  # noqa: F401
from app.services.proveedor_service import ProveedorService
from app.services.cliente_service import ClienteService
from app.services.pedido_service import PedidoService
from database import Base
from main import app


@pytest_asyncio.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
  engine = create_async_engine("sqlite+aiosqlite:///:memory:")

  async with engine.begin() as connection:
    await connection.run_sync(Base.metadata.create_all)

  session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)

  try:
    async with session_factory() as session:
      yield session
  finally:
    await engine.dispose()


@pytest.fixture
def proveedor_service(db_session: AsyncSession) -> ProveedorService:
  return ProveedorService(db_session)

@pytest.fixture
def cliente_service(db_session: AsyncSession) -> ClienteService:
  return ClienteService(db_session)

@pytest.fixture
def pedido_service(db_session: AsyncSession) -> PedidoService:
  return PedidoService(db_session)


@pytest_asyncio.fixture
async def client(proveedor_service: ProveedorService, cliente_service: ClienteService, pedido_service: PedidoService)-> AsyncIterator[AsyncClient]:
  app.dependency_overrides[get_proveedor_service] = lambda: proveedor_service
  app.dependency_overrides[get_cliente_service] = lambda: cliente_service
  app.dependency_overrides[get_pedido_service] = lambda: pedido_service

  try:
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as test_client:
      yield test_client
  finally:
    app.dependency_overrides.pop(get_proveedor_service, None)
