Siguientes pasos (sin código de aplicación aún)

Cargar este SQL en tu MySQL 8 de dev (o en tu StatefulSet de K8s).

Configurar usuarios y conexiones por servicio: usa las cuentas app_* creadas y no hardcodees credenciales (solo .env local y Vault en K8s).

Definir contratos por servicio (OpenAPI “thin”): describe únicamente los DTOs/queries finales (no expongas detalles de tablas).

Mapear casos de uso por capa application:

IAM: register, login, me, admin.users CRUD, forgot/reset, con políticas require_role("admin").

Catálogo: CRUD admin + consultas públicas (con alias legacy).

Proveedores: CRUD admin, GET disponibilidad y POST reserva temporal (TTL).

Contratación: POST pedido (desde paquete o custom items), GET mios/{id}, enviar-resumen → insert a outbox, admin cambios de estado y asignación de proveedor.

Estrategia de seguridad: JWT HS256 con sub, role, jti, iat, exp; hash de contraseñas bcrypt cost=12 (como definiste).

Observabilidad: homogeneiza logs con correlation_id y responde X-Correlation-ID; expón /health (sin DB) y /ready (ping DB).

Pruebas: para cada endpoint principal, define tests de éxito, validación y autorización (401/403); añade pruebas de idempotencia (request_id, correlation_id).

Contenedores: Dockerfile multi-stage slim, sin herramientas extras, con ENV leídos de Vault cuando VAULT_ENABLED=1.

Kubernetes: readiness/liveness, anotaciones de Vault, ingressclass correcta, límites/requests y políticas de red mínimas.

Jobs/Workers:

Cleaner de holds ya está como EVENT; si prefieres, muévelo a un cronjob K8s.

Email sender: proceso periódico que toma status=0/3, envía correo y marca sent_at/status.