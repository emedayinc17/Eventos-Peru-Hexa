# Herramientas de Utilidad (Tools)

Este directorio contiene scripts de utilidad para el mantenimiento, verificación y configuración del ecosistema de microservicios de Eventos Perú.

## Scripts Disponibles

### 🔐 Seguridad y Usuarios

- **`hash_password.py`**
  - **Uso**: `python tools/hash_password.py "MiPassword"`
  - **Descripción**: Genera un hash seguro (Bcrypt) compatible con la base de datos de usuarios. Utiliza la librería compartida `ev_shared`.
  
- **`setup_admin_user.py`**
  - **Uso**: `python tools/setup_admin_user.py`
  - **Descripción**: Script interactivo o automatizado para crear o resetear el usuario administrador inicial en la base de datos IAM.

### 🔍 Verificación y Diagnóstico

- **`check_db_connection.py`**
  - **Uso**: `python tools/check_db_connection.py`
  - **Descripción**: Verifica la conectividad con las bases de datos MySQL configuradas en el entorno.

- **`check_audit_log.py`**
  - **Uso**: `python tools/check_audit_log.py`
  - **Descripción**: Consulta y verifica que los registros de auditoría se estén escribiendo correctamente en la base de datos.

- **`check_root.py`**
  - **Uso**: `python tools/check_root.py`
  - **Descripción**: Herramienta de diagnóstico para probar credenciales de root de MySQL en entornos locales.

- **`validate_frontend_endpoints.py`**
  - **Uso**: `python tools/validate_frontend_endpoints.py`
  - **Descripción**: Script de integración que valida que los endpoints clave requeridos por el Frontend estén activos y respondiendo correctamente.

- **`verify_architecture.py`**
  - **Uso**: `python tools/verify_architecture.py`
  - **Descripción**: Analiza estáticamente el código para asegurar que se respeten las reglas de dependencia de la Arquitectura Hexagonal (ej. Dominio no debe depender de Infraestructura).

### 📄 Documentación

- **`generate_iam_ppt.py`**
  - **Uso**: `python tools/generate_iam_ppt.py`
  - **Descripción**: Genera diapositivas o recursos visuales para la documentación del servicio IAM. (Ver `README_generate_ppt.md` para más detalles).

## Notas
- La mayoría de estos scripts requieren que el entorno virtual esté activado (`Scripts\activate`).
- Algunos scripts dependen de la librería compartida `libs/shared`, asegúrate de que `PYTHONPATH` esté configurado correctamente si los ejecutas manualmente (aunque los scripts suelen manejar esto).
