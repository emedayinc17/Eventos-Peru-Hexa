# Checklist de Integración Frontend-Backend

## Endpoints y Flujos Implementados

### Autenticación y Usuarios (IAM)
- [x] POST /iam/auth/login — Login de usuario
- [x] GET /iam/me — Perfil de usuario autenticado
- [x] GET /iam/admin/users — Listado de usuarios (admin)
- [x] POST /iam/admin/users — Crear usuario (admin)
- [x] PUT /iam/admin/users/{id} — Editar usuario (admin)
- [x] DELETE /iam/admin/users/{id} — Eliminar usuario (admin)

### Catálogo
- [x] GET /catalogo/tipos-evento — Listar tipos de evento
- [x] POST /catalogo/tipos-evento — Crear tipo de evento
- [x] PUT /catalogo/tipos-evento/{id} — Editar tipo de evento
- [x] DELETE /catalogo/tipos-evento/{id} — Eliminar tipo de evento
- [x] GET /catalogo/servicios — Listar servicios
- [x] POST /catalogo/servicios — Crear servicio
- [x] PUT /catalogo/servicios/{id} — Editar servicio
- [x] DELETE /catalogo/servicios/{id} — Eliminar servicio
- [x] GET /catalogo/paquetes — Listar paquetes
- [x] POST /catalogo/paquetes — Crear paquete
- [x] PUT /catalogo/paquetes/{id} — Editar paquete
- [x] DELETE /catalogo/paquetes/{id} — Eliminar paquete

### Contratación / Pedidos
- [x] GET /contratacion/pedidos — Listar pedidos
- [x] POST /contratacion/pedidos — Crear pedido
- [x] PUT /contratacion/pedidos/{id} — Editar pedido
- [x] DELETE /contratacion/pedidos/{id} — Eliminar pedido

### Proveedores
- [ ] GET /proveedores/proveedores — Listar proveedores
- [ ] POST /proveedores/proveedores — Crear proveedor
- [ ] PUT /proveedores/proveedores/{id} — Editar proveedor
- [ ] DELETE /proveedores/proveedores/{id} — Eliminar proveedor

### Flujos UI probados
- [x] Login y redirección por rol
- [x] Dashboard cliente y admin
- [x] CRUD de tipos de evento, servicios, paquetes, usuarios
- [x] Wizard de creación de pedido (cliente)
- [x] Listado y detalle de pedidos (cliente y admin)

## Pendientes / Por Validar
- [ ] Integración completa de proveedores (CRUD y vistas)
- [ ] Reportes, notificaciones, búsqueda global (si aplica)
- [ ] Validación de endpoints avanzados (descarga PDF, contratos, etc.)
- [ ] Mejorar mensajes de error y UX en casos límite
- [ ] Documentar endpoints personalizados adicionales

## Estado estimado de avance

- **Autenticación y usuarios:** 100%
- **Catálogo (tipos, servicios, paquetes):** 100%
- **Contratación/pedidos:** 100%
- **Proveedores:** 0-30% (pendiente integración CRUD y vistas)
- **Flujos avanzados:** 0-20% (según requerimientos)

---

_Actualiza este checklist conforme avances en la integración o surjan nuevos endpoints._
