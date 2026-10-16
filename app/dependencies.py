from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from database import get_db_session
from app.services.proveedor_service import ProveedorService

def get_proveedor_service(db: AsyncSession = Depends(get_db_session)) -> ProveedorService:
  return ProveedorService(db)
