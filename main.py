import logging
import uvicorn
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI
from app.exceptions.handlers import register_exception_handlers
from app.core.config import settings
from database import dispose_engine
from app.models import * 
from app.routers.proveedor_router import router as proveedores_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
  yield
  await dispose_engine()


app = FastAPI(
  lifespan=lifespan,
  title="API de Pedidos",
  description=settings.API_DESCRIPCION,
  version=settings.API_VERSION
)

register_exception_handlers(app)

app.include_router(proveedores_router, prefix="/api/v1/proveedores", tags=["Proveedores"])


@app.get("/health")
async def health():
  return {
    "status": "OK",
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "version": settings.API_VERSION,
    "service": settings.API_DESCRIPCION
  }

if __name__ == "__main__":
  uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True, log_level="info")