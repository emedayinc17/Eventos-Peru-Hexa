// config.js (default for local dev)
// Este archivo puede ser sobreescrito por un ConfigMap en Kubernetes.

// ================= IAM Service =================
// Base por defecto para el servicio de Identidad / IAM.
window.IAM_API_BASE = window.IAM_API_BASE || "http://127.0.0.1:8010/iam";

// Compatibilidad hacia atrás: muchos módulos siguen leyendo window.API_BASE.
window.API_BASE = window.API_BASE || window.IAM_API_BASE;

// ================= Catálogo Service =================
// Base por defecto para el servicio de Catálogo (consulta de tipos/servicios/opciones/paquetes).
window.CATALOGO_API_BASE = window.CATALOGO_API_BASE || "http://127.0.0.1:8020/catalogo";

// ================= Proveedores Service =================
// Base por defecto para el servicio de Proveedores (búsqueda y reservas).
window.PROVEEDORES_API_BASE = window.PROVEEDORES_API_BASE || "http://127.0.0.1:8030/proveedores";

// ================= Contratación Service =================
// Base por defecto para el servicio de Contratación (pedidos/reservas).
window.CONTRATACION_API_BASE = window.CONTRATACION_API_BASE || "http://127.0.0.1:8040/contratacion";

// Quicklogin defaults (local dev). Cambia estas variables si quieres credenciales predefinidas.
// Credenciales semilla incluidas en `db/bosstrap_remaste.sql` (uso en local/dev)
window.QUICKLOGIN_CLIENT_EMAIL = window.QUICKLOGIN_CLIENT_EMAIL || "demo@eventos.pe";
window.QUICKLOGIN_CLIENT_PASSWORD = window.QUICKLOGIN_CLIENT_PASSWORD || "Admin_2025!";
// En este esquema demo no hay un admin seed por separado; por conveniencia local usamos
// las mismas credenciales para el botón Admin (puedes cambiarlo en entornos reales).
window.QUICKLOGIN_ADMIN_EMAIL = window.QUICKLOGIN_ADMIN_EMAIL || "demo@eventos.pe";
window.QUICKLOGIN_ADMIN_PASSWORD = window.QUICKLOGIN_ADMIN_PASSWORD || "Admin_2025!";
