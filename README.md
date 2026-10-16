# Pedidos FastAPI

API asíncrona para gestionar pedidos, proveedores y clientes. Actualmente están disponibles los endpoints CRUD de proveedores; los modelos de clientes y pedidos ya están definidos, pero sus rutas todavía no forman parte de la API.

## Requisitos

- Python 3.11 o superior.
- [`uv`](https://docs.astral.sh/uv/) para gestionar el entorno y las dependencias.
- PostgreSQL para ejecutar la aplicación y las migraciones.

## Puesta en marcha

Desde la raíz del proyecto:

```powershell
uv sync --dev
Copy-Item .env.example .env
```

Edita `.env` con la configuración local. Por ejemplo:

```dotenv
DATABASE_URL=postgresql+asyncpg://usuario:contrasena@localhost:5432/pedidos
API_DESCRIPCION=API de gestión de pedidos
API_VERSION=1.0.0
PORT=8000
PAGINACION_LIMITE_POR_DEFECTO=100
PAGINACION_LIMITE_MAXIMO=500
```

La base de datos `pedidos` debe existir en PostgreSQL antes de aplicar las migraciones.

## Base de datos

El acceso a la base de datos usa SQLAlchemy asíncrono y `asyncpg`. Alembic aplica las migraciones con una conexión síncrona derivada de `DATABASE_URL`.

Aplicar las migraciones pendientes:

```powershell
uv run alembic upgrade head
```

Crear una migración nueva a partir de los modelos:

```powershell
uv run alembic revision --autogenerate -m "descripcion del cambio"
```

Revisa la migración generada antes de aplicarla. Para volver una migración atrás:

```powershell
uv run alembic downgrade -1
```

## Ejecutar la API

```powershell
uv run python main.py
```

El servidor usa el puerto definido en `PORT`. Con el ejemplo anterior, la documentación interactiva está en:

- Swagger UI: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>
- Estado del servicio: <http://127.0.0.1:8000/health>

## Endpoints disponibles

| Método | Ruta | Descripción | Respuesta normal |
| --- | --- | --- | --- |
| `POST` | `/api/v1/proveedores/` | Registrar proveedor | `201 Created` |
| `GET` | `/api/v1/proveedores/` | Listar proveedores con paginación | `200 OK` |
| `GET` | `/api/v1/proveedores/{proveedor_id}` | Consultar proveedor por ID | `200 OK` |
| `PUT` | `/api/v1/proveedores/{proveedor_id}` | Actualizar proveedor | `200 OK` |

### Ejemplo: registrar proveedor

```http
POST /api/v1/proveedores/
Content-Type: application/json
```

```json
{
  "nombre": "Proveedor Ejemplo"
}
```

El nombre se normaliza eliminando espacios externos y convirtiéndolo a mayúsculas. La respuesta de éxito tiene esta forma:

```json
{
  "message": "Proveedor registrado correctamente",
  "data": {
    "id": 1,
    "nombre": "PROVEEDOR EJEMPLO",
    "created_at": "2026-01-01T12:00:00",
    "updated_at": "2026-01-01T12:00:00"
  },
  "success": true
}
```

La paginación del listado usa los parámetros `skip` y `limit`. `skip` debe ser mayor o igual que cero; `limit`, entre 1 y el máximo configurado.

```text
GET /api/v1/proveedores/?skip=0&limit=100
```

Las respuestas de error usan un formato uniforme, por ejemplo:

```json
{
  "message": "El proveedor 'PROVEEDOR EJEMPLO' ya existe en la base de datos",
  "data": null,
  "success": false,
  "error_code": "PROVEEDOR_YA_EXISTE"
}
```

## Pruebas

Las pruebas usan `pytest`, `pytest-asyncio`, `httpx` y una base SQLite en memoria configurada en `tests/conftest.py`. No necesitan conectarse a PostgreSQL.

Ejecutar todas las pruebas:

```powershell
uv run pytest
```

Ejecutar solo los tests del servicio o de la API:

```powershell
uv run pytest tests/services/test_proveedor_service.py
uv run pytest tests/routers/test_proveedor_router.py
```

## Estructura del proyecto

```text
app/
├── core/          # Configuración y paginación
├── exceptions/    # Errores y manejadores HTTP
├── models/        # Modelos SQLAlchemy
├── routers/       # Rutas FastAPI
├── schemas/       # Esquemas Pydantic y respuestas
├── services/      # Lógica de negocio
└── utils/         # Mensajes compartidos
alembic/           # Configuración y versiones de migración
tests/             # Pruebas de servicios y endpoints
main.py            # Aplicación FastAPI y punto de entrada
database.py        # Base SQLAlchemy y sesiones asíncronas
```

