# Registro de Correcciones Técnicas - Persistencia, Reactividad y Seguridad

## 📅 Fecha: 27 Noviembre 2025

### 🎯 Objetivo
Corregir problemas de actualización en UI, errores de CORS por redirecciones en el API Gateway, y asegurar la protección de rutas administrativas.

### 🛠️ Cambios en Backend (Python/FastAPI)

#### 1. Servicio de Catálogo (`catalogo-service`)
*   **Problema**: Los métodos `create_*` y `update_*` en los repositorios devolvían objetos incompletos.
*   **Solución**: Se actualizaron los repositorios para devolver el objeto completo tras la operación.

#### 2. Servicio de Proveedores (`proveedores-service`)
*   **Problema (CORS/Redirección)**: Las rutas administrativas (`/v1/admin/proveedores/`) tenían un slash final. El frontend llamaba sin slash, causando una redirección 307 del backend que saltaba el API Gateway, provocando errores de CORS.
*   **Solución**: Se eliminó el slash final en las definiciones de rutas (`@router.get("")`, `@router.post("")`) en `router_admin.py`.
*   **Seguridad**: Se añadió la dependencia `Depends(require_admin)` al router administrativo para proteger todos los endpoints.

### 🛠️ Cambios en Frontend (Vue.js)

#### 1. Manejo de IDs (UUID vs Number)
*   **Problema**: Inconsistencia de tipos (number vs string) rompía comparaciones.
*   **Solución**: Actualizados Stores y APIs para manejar ambos tipos y usar comparaciones de cadena (`String(id) === String(target)`).

#### 2. Reactividad en Listas (Servicios)
*   **Problema**: Al crear/editar un servicio, la lista desaparecía.
*   **Causa**: Se llamaba a `fetchServicios(true)`, enviando "true" como ID de filtro.
*   **Solución**: Corregido a `fetchServicios(undefined, true)` en `Servicios.vue`.

#### 3. Feedback de Usuario
*   **Mejora**: Se añadieron logs de debug y notificaciones Toast (`ui.showToast`) en operaciones de eliminación para mejor trazabilidad.

---
**Estado Actual**: 
- ✅ CRUDs de Catálogo y Proveedores funcionales.
- ✅ Rutas Admin protegidas y accesibles vía Gateway.
- ✅ Reactividad de UI corregida.
