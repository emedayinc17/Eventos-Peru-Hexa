# Pruebas del Servicio IAM

Este directorio contiene las pruebas automatizadas para el servicio de Identity & Access Management (IAM).

## Estructura
- `test_iam_service.py`: Script consolidado que incluye pruebas unitarias (seguridad) y de integración (endpoints).
- `conftest.py`: Configuración de rutas para importar módulos compartidos.
- `pytest.ini`: Configuración base de pytest.
- `report_iam.html`: Reporte de resultados (generado automáticamente).

## Requisitos Previos
Asegúrate de tener el entorno virtual activado y las dependencias instaladas:

```powershell
# Desde la raíz del proyecto
.\Scripts\activate

# Instalar dependencias de prueba si no las tienes
pip install pytest pytest-html httpx
```

## Ejecución de Pruebas

### Opción 1: Ejecución Estándar (Consola)
Para ver los resultados directamente en la terminal:

```powershell
cd services/iam-service
pytest test/test_iam_service.py
```

### Opción 2: Generando Reporte HTML (Recomendado)
Para generar un reporte visual detallado de los resultados:

```powershell
cd services/iam-service
pytest test/test_iam_service.py --html=test/report_iam.html --self-contained-html
```

El reporte se guardará en este mismo directorio como `report_iam.html`.

## Cobertura de las Pruebas
El script `test_iam_service.py` valida los siguientes aspectos:

1. **Pruebas Unitarias (Caja Blanca)**:
   - Hashing y verificación de contraseñas.
   - Generación y decodificación de tokens JWT.

2. **Pruebas de Integración (API Flow)**:
   - **Health Check**: Disponibilidad del servicio.
   - **Registro**: Creación de nuevos usuarios.
   - **Autenticación**: Login exitoso para roles Cliente y Admin.
   - **Perfil**: Acceso a datos propios (`/me`).
   - **Gestión Admin**: Listar, ver detalle, actualizar y eliminar usuarios.
   - **Seguridad RBAC**: Verificación de que usuarios sin permisos no pueden acceder a rutas administrativas.
