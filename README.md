# Pedidos FastAPI

API asíncrona para gestionar clientes, proveedores y pedidos. Permite crear, consultar y actualizar clientes y proveedores, además de crear, consultar, filtrar, actualizar y eliminar pedidos.

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
| `POST` | `/api/v1/clientes/` | Registrar cliente | `201 Created` |
| `GET` | `/api/v1/clientes/` | Listar clientes con paginación | `200 OK` |
| `GET` | `/api/v1/clientes/{cliente_id}` | Consultar cliente por ID | `200 OK` |
| `PUT` | `/api/v1/clientes/{cliente_id}` | Actualizar cliente | `200 OK` |
| `POST` | `/api/v1/pedidos/` | Crear pedido | `201 Created` |
| `GET` | `/api/v1/pedidos/{pedido_id}` | Consultar pedido por ID | `200 OK` |
| `GET` | `/api/v1/pedidos/estado/{estado}` | Filtrar pedidos por estado | `200 OK` |
| `GET` | `/api/v1/pedidos/cliente/{cliente_id}` | Filtrar pedidos por cliente | `200 OK` |
| `GET` | `/api/v1/pedidos/proveedor/{proveedor_id}` | Filtrar pedidos por proveedor | `200 OK` |
| `GET` | `/api/v1/pedidos/cliente/{cliente_id}/estado/{estado}` | Filtrar por cliente y estado | `200 OK` |
| `GET` | `/api/v1/pedidos/proveedor/{proveedor_id}/cliente/{cliente_id}` | Filtrar por proveedor y cliente | `200 OK` |
| `PUT` | `/api/v1/pedidos/{pedido_id}` | Actualizar pedido | `200 OK` |
| `DELETE` | `/api/v1/pedidos/{pedido_id}` | Eliminar pedido | `200 OK` |

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

Los endpoints de listado de clientes y filtros de pedidos aceptan los mismos parámetros de paginación. Por ejemplo:

```text
GET /api/v1/pedidos/estado/pedido?skip=0&limit=50
GET /api/v1/pedidos/cliente/1?skip=0&limit=50
```

## Pedidos

Para crear un pedido, envía `producto`, `unidades`, `cliente_id` y `proveedor_id`. `oferta` es opcional y su valor predeterminado es `SIN OFERTA`; `solicitado_por` y `observaciones` también son opcionales. El estado inicial es `pedido`.

```http
POST /api/v1/pedidos/
Content-Type: application/json
```

```json
{
  "producto": "Producto de ejemplo",
  "unidades": 2,
  "cliente_id": 1,
  "proveedor_id": 1,
  "oferta": "OFERTA 500",
  "solicitado_por": "Nombre de quien solicita",
  "observaciones": "Entregar por la mañana"
}
```

La API verifica que existan el cliente y el proveedor antes de guardar el pedido. `producto` admite entre 1 y 255 caracteres después de quitar espacios externos; `unidades` debe ser mayor que cero; `oferta` admite hasta 25 caracteres y `observaciones`, hasta 1000.

Los estados disponibles para filtrar son `pedido`, `preparado`, `entregado`, `cancelado`, `facturado` y `devuelto`. Un estado no reconocido produce HTTP 422. Los IDs de pedido en las rutas deben ser enteros positivos.

Las respuestas de pedido incluyen los IDs y los objetos anidados `cliente` y `proveedor`. La actualización con `PUT` recibe los campos de creación y conserva el estado actual del pedido.

```text
GET    /api/v1/pedidos/estado/pedido
GET    /api/v1/pedidos/cliente/1/estado/pedido
GET    /api/v1/pedidos/proveedor/1
GET    /api/v1/pedidos/proveedor/1/cliente/1
GET    /api/v1/pedidos/1
PUT    /api/v1/pedidos/1
DELETE /api/v1/pedidos/1
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

Ejecutar los tests de un servicio o router concreto:

```powershell
uv run pytest tests/services/test_cliente_service.py
uv run pytest tests/services/test_proveedor_service.py
uv run pytest tests/routers/test_cliente_router.py
uv run pytest tests/routers/test_proveedor_router.py
uv run pytest tests/routers/test_pedido_router.py
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

