# REPORTE DE VALIDACIÓN DE ENDPOINTS - Eventos Perú Hexagonal

## Fecha: 2025-11-24

## Resumen Ejecutivo

Se ejecutó una validación integral de todos los endpoints del sistema con dos perfiles de usuario:
- **ADMIN**: `demo@eventos.pe` / `Admin_2025!`
- **CLIENTE**: `cliente_test@eventos.pe` / `Client_2025!`

## Resultados por Servicio

### ✅ IAM Service (http://localhost:8010/iam)
- **Login ADMIN**: ✅ OK
- **Login CLIENTE**: ✅ OK  
- **GET /me**: ✅ OK
- **GET /admin/users**: ❌ FAIL (403 Forbidden)
  - **Causa**: El usuario `demo@eventos.pe` tiene rol `CLIENTE`, no `ADMIN`
  - **Solución**: Actualizar el rol en la BD o usar un usuario con rol ADMIN

### ✅ CATÁLOGO Service (http://localhost:8020/catalogo)
- **GET /v1/catalogo/tipos**: ✅ OK (8 tipos encontrados)
- **GET /v1/catalogo/servicios**: ✅ OK (33 servicios encontrados)

### ⚠️ PROVEEDORES Service (http://localhost:8030/proveedores)
- **Endpoints de escritura**: ⚠️ NO EXPUESTOS
  - No hay endpoints públicos para crear/editar proveedores
  - Solo existe `/v1/proveedores/disponibles` (consulta)
  - Los endpoints internos requieren `X-Service-Token`

### ❌ CONTRATACIÓN Service (http://localhost:8040/contratacion)
- **POST /pedidos**: ❌ FAIL (500 Internal Server Error)
- **GET /pedidos/mios**: ❌ FAIL (500 Internal Server Error)

## Problemas Identificados

### 1. Error 500 en Contratación Service
**Síntoma**: Todos los endpoints de contratación devuelven 500

**Posibles causas**:
1. **Mismatch de esquema BD vs Código**:
   - El modelo `Pedido` espera campo `paquete_id` (Optional)
   - La tabla `pedido_evento` NO tiene este campo
   - Ya se corrigió en `repositories.py` para derivarlo de `item_pedido_evento`

2. **Campos faltantes en `item_pedido_evento`**:
   - La tabla tiene campos duplicados (legacy vs nuevos)
   - `tipo_item` es VARCHAR ('SERVICIO'/'PAQUETE'), no INT
   - Posible error al insertar items

3. **Validación de schema Pydantic**:
   - `CrearPedidoCustom` espera `hora_inicio: time` y `hora_fin: time`
   - El payload envía strings "HH:MM"
   - Pydantic debería convertir automáticamente, pero puede fallar

**Acción requerida**:
- Revisar logs del servicio `contratacion-service` para ver el traceback completo
- Verificar que el use case `CrearPedidoCustom` esté usando los campos correctos de la BD

### 2. Usuario ADMIN sin rol correcto
**Síntoma**: `demo@eventos.pe` no puede acceder a `/admin/users`

**Causa**: El usuario tiene rol `CLIENTE` en lugar de `ADMIN`

**Solución**:
```sql
-- Verificar rol actual
SELECT u.email, r.codigo 
FROM ev_iam.usuario u
JOIN ev_iam.usuario_rol ur ON ur.usuario_id = u.id
JOIN ev_iam.rol r ON r.id = ur.rol_id
WHERE u.email = 'demo@eventos.pe';

-- Actualizar a ADMIN
UPDATE ev_iam.usuario_rol 
SET rol_id = 'aaaa1111-1111-1111-1111-aaaaaaaaaaa1'  -- ADMIN
WHERE usuario_id = 'aaaa2222-2222-2222-2222-aaaaaaaaaaa2';
```

## Próximos Pasos

1. **Prioridad ALTA**: Resolver error 500 en Contratación
   - Revisar logs del servicio
   - Verificar que `crear_pedido_custom_use_case` use los campos correctos
   - Asegurar que `item_pedido_evento` se inserte con `tipo_item='SERVICIO'` (VARCHAR)

2. **Prioridad MEDIA**: Corregir rol de usuario demo
   - Actualizar `bosstrap_remaste.sql` para asignar rol ADMIN
   - O crear un usuario admin separado

3. **Prioridad BAJA**: Documentar endpoints faltantes
   - Proveedores: endpoints de escritura solo internos
   - Considerar si se necesitan endpoints públicos para CRUD de proveedores

## Endpoints Validados Exitosamente

| Servicio | Método | Endpoint | Status |
|----------|--------|----------|--------|
| IAM | POST | /auth/login | ✅ 200 |
| IAM | POST | /auth/register | ✅ 201 |
| IAM | GET | /me | ✅ 200 |
| CATÁLOGO | GET | /v1/catalogo/tipos | ✅ 200 |
| CATÁLOGO | GET | /v1/catalogo/servicios | ✅ 200 |

## Endpoints con Errores

| Servicio | Método | Endpoint | Status | Error |
|----------|--------|----------|--------|-------|
| IAM | GET | /admin/users | ❌ 403 | Forbidden (rol incorrecto) |
| CONTRATACIÓN | POST | /pedidos | ❌ 500 | Internal Server Error |
| CONTRATACIÓN | GET | /pedidos/mios | ❌ 500 | Internal Server Error |

## Notas Técnicas

- Base de datos poblada con `script2.sql` (150+ registros de prueba)
- CORS configurado correctamente para localhost:3000 y localhost:8000
- Todos los servicios responden al health check
- La autenticación JWT funciona correctamente
