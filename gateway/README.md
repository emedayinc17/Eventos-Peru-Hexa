# API Gateway

Gateway de enrutamiento para los microservicios de Eventos Peru.

## Puerto

- **8000** - Punto de entrada único

## Servicios Backend

| Ruta | Servicio | Puerto Real |
|------|----------|-------------|
| `/api/iam/*` | IAM Service | 8010 |
| `/api/catalogo/*` | Catálogo Service | 8020 |
| `/api/proveedores/*` | Proveedores Service | 8030 |
| `/api/contratacion/*` | Contratación Service | 8040 |

## Uso

```bash
# Desde el directorio gateway
run.bat

# O manualmente
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Ejemplo de Peticiones

```bash
# Login (enruta a IAM:8010)
curl -X POST http://localhost:8000/api/iam/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@eventos.com", "password": "admin123"}'

# Obtener paquetes (enruta a Catálogo:8020)
curl http://localhost:8000/api/catalogo/paquetes

# Obtener proveedores (enruta a Proveedores:8030)
curl http://localhost:8000/api/proveedores/proveedores

# Crear pedido (enruta a Contratación:8040)
curl -X POST http://localhost:8000/api/contratacion/pedidos \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

## Health Check

```bash
curl http://localhost:8000/health
```

## Dependencias

- `fastapi`
- `uvicorn`
- `httpx` (para proxy requests)

## CORS

Permite requests desde:
- `http://localhost:5173` (Vite default)
- `http://localhost:5174` (Vite alternate)
- `http://localhost:3000` (React/Next.js)
