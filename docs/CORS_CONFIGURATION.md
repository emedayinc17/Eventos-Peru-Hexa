# Configuración de CORS (Cross-Origin Resource Sharing)

## Problema Identificado
El frontend, al ejecutarse en un puerto distinto al del backend (ej. `http://localhost:5500` vs `http://localhost:8010`), es bloqueado por las políticas de seguridad del navegador (CORS) si el servidor no autoriza explícitamente el origen.

Error típico:
```
Access to fetch at 'http://localhost:8010/auth/login' from origin 'http://localhost:5500' has been blocked by CORS policy...
```

## Solución Implementada

Se ha centralizado la configuración de CORS en la librería compartida `ev_shared`, que es utilizada por todos los microservicios (IAM, Catálogo, Proveedores, Contratación).

### Archivo Modificado
`libs/shared/ev_shared/config.py`

### Variable de Configuración
`CORS_ORIGINS`

### Orígenes Permitidos por Defecto
- `http://localhost:3000`
- `http://127.0.0.1:3000`
- `http://localhost:8000`
- `http://127.0.0.1:8000`
- `http://localhost:5500` (Nuevo Frontend Vanilla)
- `http://127.0.0.1:5500`

## Cómo Agregar Nuevos Orígenes

Para permitir nuevos dominios o puertos, tienes dos opciones:

1. **Variable de Entorno (Recomendado para Producción)**:
   Define la variable `CORS_ORIGINS` en el entorno de ejecución o en el archivo `.env`.
   ```bash
   CORS_ORIGINS="http://mi-dominio.com,https://mi-app.com"
   ```

2. **Modificar Código (Desarrollo)**:
   Edita `libs/shared/ev_shared/config.py` y agrega el origen a la lista por defecto.

## Verificación
Después de aplicar los cambios, es necesario **reiniciar los microservicios** para que tomen la nueva configuración.
