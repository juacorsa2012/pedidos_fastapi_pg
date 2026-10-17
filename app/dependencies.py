from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from database import get_db_session
from app.services.proveedor_service import ProveedorService
from app.services.cliente_service import ClienteService
from app.services.pedido_service import PedidoService

def get_proveedor_service(db: AsyncSession = Depends(get_db_session)) -> ProveedorService:
  return ProveedorService(db)

def get_cliente_service(db: AsyncSession = Depends(get_db_session)) -> ClienteService:
  return ClienteService(db)

def get_pedido_service(db: AsyncSession = Depends(get_db_session)) -> PedidoService:
  return PedidoService(db)
