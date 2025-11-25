# Frontend Vanilla + Bootstrap — Eventos Perú (MVP)

Sistema frontend completo para gestión de eventos con arquitectura de microservicios, integrado con **IAM**, **Catálogo**, **Proveedores** y **Contratación** services.

## 🎯 Características Phase 3

### Cliente
- ✅ Explorar catálogo de paquetes y servicios
- ✅ Crear pedidos desde paquetes
- ✅ Ver mis pedidos con filtros por estado
- ✅ Ver detalle de pedidos con items y precios
- ✅ Estadísticas personales (total, confirmados, pendientes, cancelados)

### Administrador
- ✅ **Vista de todos los pedidos del sistema**
- ✅ **Filtros avanzados:** estado, ID, cliente
- ✅ **Cambiar estados** con validación de transiciones
- ✅ **Asignar proveedores** a items (solo en estado APROBADO)
- ✅ **Agregar/Eliminar items** de pedidos
- ✅ **Estadísticas globales** por estado (6 métricas)
- ✅ Gestión completa de usuarios (IAM)

## 📋 Requisitos

### Servicios Backend (todos deben estar corriendo)
```bash
# IAM Service
http://localhost:8010/iam

# Catálogo Service
http://localhost:8020/catalogo

# Proveedores Service
http://localhost:8030/proveedores

# Contratación Service
http://localhost:8040/contratacion
```

### Base de Datos
- MySQL con esquema `ev_contratacion` actualizado (ver `db/bosstrap_remaste.sql`)

## 🚀 Inicio Rápido

### Opción 1: Servidor Python
```bash
cd frontend-vanilla
python -m http.server 8000
```
Luego abrir: `http://localhost:8000`

### Opción 2: Live Server (VSCode)
1. Instalar extensión "Live Server"
2. Click derecho en `index.html` → "Open with Live Server"

### Opción 3: Docker
```bash
docker build -t eventos-frontend:latest .
docker run -p 8080:80 eventos-frontend:latest
```
Abrir: `http://localhost:8080`

## ⚙️ Configuración

### URLs de Servicios
Editar `config.js`:
```javascript
window.IAM_API_BASE = "http://localhost:8010/iam";
window.CATALOGO_API_BASE = "http://localhost:8020/catalogo";
window.PROVEEDORES_API_BASE = "http://localhost:8030/proveedores";
window.CONTRATACION_API_BASE = "http://localhost:8040/contratacion";
```

### Credenciales de Prueba
```
Admin:
  Email: admin@eventos.pe
  Password: admin123

Cliente:
  Email: cliente@eventos.pe
  Password: cliente123
```

## 📁 Estructura del Proyecto

```
frontend-vanilla/
├── index.html              # HTML principal con modales
├── config.js               # Configuración de endpoints
├── CHANGELOG.md            # 🆕 Historial de cambios
├── GUIA_USO.md            # 🆕 Guía completa para usuarios
├── TECHNICAL.md           # 🆕 Documentación técnica para devs
├── js/
│   ├── api.js             # Cliente HTTP para IAM y Catálogo
│   ├── services.js        # Cliente HTTP para Proveedores y Contratación
│   ├── auth.js            # Gestión de sesión y JWT
│   └── app.js             # Router, lógica de vistas, modales
├── k8s/
│   └── iam-frontend.yaml  # Deployment Kubernetes
└── README.md              # Este archivo
```

## 🎨 Vistas Principales

### Públicas
- `/` - Home landing
- `/catalogo` - Catálogo de paquetes (lectura)
- `/login` - Login de usuarios

### Autenticadas (Cliente/Admin)
- `/me` - Perfil del usuario
- `/contratacion` - Mis pedidos (Cliente) o Gestión de pedidos (Admin)
- `/proveedores` - Búsqueda de proveedores disponibles

### Solo Admin
- `/admin` - Gestión de usuarios IAM
- `/admin-register` - Crear nuevos usuarios

## 🔧 Funcionalidades Técnicas

### Autenticación JWT
```javascript
// Login
const response = await IAM.login(email, password);
// Token guardado en sessionStorage
// Header automático: Authorization: Bearer <token>
```

### Gestión de Estados de Pedidos
```javascript
// Estados válidos: 0-5
const TRANSICIONES_VALIDAS = {
  0: [1, 5],  // DRAFT → COTIZADO, CANCELADO
  1: [2, 5],  // COTIZADO → APROBADO, CANCELADO
  2: [3, 5],  // APROBADO → ASIGNADO, CANCELADO
  3: [4, 5],  // ASIGNADO → CERRADO, CANCELADO
  4: [],      // CERRADO (final)
  5: []       // CANCELADO (final)
};
```

### Notificaciones Toast
```javascript
showNotification('Operación exitosa', 'success');
showNotification('Error al procesar', 'error');
showNotification('Advertencia', 'warning');
showNotification('Información', 'info');
```

### Endpoints Principales

#### Cliente
```javascript
// Crear pedido desde paquete
CONTRATACION.crearPedido({
  paquete_id: "paq_boda_clasica",
  fecha_evento: "2025-12-25",
  hora_inicio: "18:00:00",
  ubicacion: "Lima"
});

// Mis pedidos
CONTRATACION.misPedidos();

// Detalle de pedido
CONTRATACION.detallePedido(id);
```

#### Admin
```javascript
// Todos los pedidos del sistema
CONTRATACION.adminTodosPedidos();

// Cambiar estado
CONTRATACION.adminCambiarEstado(id, { estado: 2 });

// Asignar proveedor
CONTRATACION.adminAsignarProveedor(id, {
  item_pedido_ids: ["item1", "item2"],
  proveedor_id: "prov-uuid"
});

// Agregar items
CONTRATACION.adminAgregarItems(id, {
  items: [{
    opcion_servicio_id: "opt_foto",
    cantidad: 2,
    precio_unit_vigente: 150.00
  }]
});

// Eliminar items
CONTRATACION.adminEliminarItems(id, {
  item_ids: ["item1", "item2"]
});
```

## 🧪 Testing Manual

### Flujo Completo: Crear Pedido → Asignar Proveedores → Cerrar

1. **Login como Cliente:**
   - Email: `cliente@eventos.pe`
   - Password: `cliente123`

2. **Crear Pedido:**
   - Ir a `/catalogo`
   - Click "Reservar / Contratar" en un paquete
   - Completar formulario (fecha, hora, ubicación)
   - Confirmar → Pedido creado en estado BORRADOR (0)

3. **Logout → Login como Admin:**
   - Email: `admin@eventos.pe`
   - Password: `admin123`

4. **Cotizar Pedido:**
   - Ir a `/contratacion`
   - Buscar pedido del cliente
   - Cambiar estado: BORRADOR → COTIZADO (1)

5. **Aprobar Pedido:**
   - Cambiar estado: COTIZADO → APROBADO (2)

6. **Asignar Proveedores:**
   - Click "Asignar" en el pedido
   - Seleccionar items
   - Ingresar proveedor_id (UUID)
   - Confirmar → Estado cambia a ASIGNADO (3)

7. **Cerrar Pedido:**
   - Cambiar estado: ASIGNADO → CERRADO (4)

## 📚 Documentación Adicional

- **[CHANGELOG.md](CHANGELOG.md)** - Historial completo de cambios por versión
- **[GUIA_USO.md](GUIA_USO.md)** - Guía paso a paso para usuarios finales
- **[TECHNICAL.md](TECHNICAL.md)** - Documentación técnica para desarrolladores

## 🐛 Troubleshooting

### Error: "Transición no permitida"
**Causa:** Intentas cambiar a un estado fuera del flujo válido.
**Solución:** Revisar tabla de transiciones válidas en GUIA_USO.md

### Error: "Solo se pueden asignar proveedores a pedidos APROBADOS"
**Causa:** El pedido no está en estado 2 (APROBADO).
**Solución:** Cambiar primero el estado a APROBADO.

### No se ven los servicios
**Causa:** Servicios backend no están corriendo.
**Solución:** Verificar que los 4 servicios estén activos:
```bash
# IAM
curl http://localhost:8010/iam/health

# Catálogo
curl http://localhost:8020/catalogo/health

# Proveedores
curl http://localhost:8030/proveedores/health

# Contratación
curl http://localhost:8040/contratacion/health
```

### Error CORS
**Causa:** Backend no permite requests desde origen del frontend.
**Solución:** Verificar configuración CORS en cada servicio:
```python
# En cada main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_methods=["*"],
    allow_headers=["*"]
)
```

## 🚀 Deployment

### Kubernetes
```bash
# Aplicar deployment
kubectl apply -f k8s/iam-frontend.yaml

# Verificar
kubectl get pods -l app=iam-frontend
kubectl get svc iam-frontend
```

### Docker Build
```bash
# Build
docker build -t emeday17/eventos-frontend:1.0.0 .

# Push
docker push emeday17/eventos-frontend:1.0.0

# Run
docker run -d -p 8080:80 emeday17/eventos-frontend:1.0.0
```

## 🔐 Seguridad

- ✅ JWT tokens almacenados en `sessionStorage` (se limpian al cerrar pestaña)
- ✅ Header `Authorization: Bearer <token>` en todos los requests autenticados
- ✅ Validación de roles en backend (frontend solo oculta UI)
- ✅ Sanitización HTML para prevenir XSS
- ⚠️ **Producción:** Usar HTTPS, tokens en httpOnly cookies, CSP headers

## 📊 Métricas

### Rendimiento
- Carga inicial: ~200ms (sin backend)
- Render de catálogo: ~50ms para 20 paquetes
- Actualización de pedidos: ~100ms para 50 pedidos

### Compatibilidad
- ✅ Chrome/Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Mobile responsive (Bootstrap 5 grid)

## 🎓 Stack Tecnológico

- **HTML5** - Estructura semántica
- **CSS3 + Bootstrap 5.3.3** - Estilos y componentes
- **Vanilla JavaScript ES6+** - Lógica sin frameworks
- **Fetch API** - HTTP requests
- **Bootstrap Icons 1.11.3** - Iconografía
- **Tom Select** - Comboboxes mejorados (opcional)

## 🤝 Contribuir

1. Fork del repositorio
2. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -am 'Agrega nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

## 📄 Licencia

Este proyecto es parte de un MVP académico para demostración de arquitectura hexagonal con microservicios.

---
**Configuración recomendada para despliegue (ConfigMap / render de config.js)**

- Resumen: monta o inyecta `config.js` en el contenedor en runtime en vez de reconstruir la imagen.
- Archivo `config.js` mínimo:
```javascript
window.IAM_API_BASE = "https://mi-domino/iam";
window.API_BASE = window.IAM_API_BASE;
```
- Ejemplo rápido de ConfigMap:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: iam-frontend-config
data:
  config.js: |
    window.IAM_API_BASE = "https://eventos.emeday.inc/iam/iam";
    window.API_BASE = window.IAM_API_BASE;
```

 - Nota: la forma recomendada en Kubernetes es montar un `ConfigMap` que provea `config.js` al contenedor (sin reempaquetar la imagen).
 - Opcional (requiere modificar la imagen): un script `render-config.sh` puede escribir `config.js` desde variables de entorno en el entrypoint; esto sí implica cambiar el `Dockerfile` y volver a construir la imagen.


**Versión:** Phase 3 Complete  
**Última Actualización:** 2025-11-22  
**Autor:** emedayinc17  
**Asistente:** GitHub Copilot