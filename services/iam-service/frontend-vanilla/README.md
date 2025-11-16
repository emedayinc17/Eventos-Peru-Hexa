# Frontend Vanilla + Bootstrap — Eventos Perú (MVP)

Este es un starter mínimo para consumir el **IAM-service** de tu proyecto con HTML+CSS+JS (vanilla) y Bootstrap.

## Requisitos
- Backend IAM corriendo localmente en: `http://localhost:8000/iam` (puedes cambiarlo).

## Configuración rápida
1. Abre `index.html` en el navegador **o** sirve la carpeta con cualquier servidor estático.
2. Ajusta la base de la API cambiando la variable global en `index.html`:
   ```html
   <script>window.API_BASE = "http://localhost:8000/iam";</script>
   ```

## Vistas incluidas
- **Home**: landing del MVP.
- **Login**: formulario que invoca `POST /auth/login` y guarda el token en `sessionStorage`.
- **Mi Perfil**: llama `GET /me` usando el Bearer.
- **Admin Usuarios**: tabla con `GET /admin/users` (requiere rol ADMIN).

## Estructura
```
index.html
js/
  api.js   // cliente fetch + endpoints IAM
  auth.js  // sesión: login/logout/me + sessionStorage
  app.js   // router por hash y wiring de vistas
```

## Siguientes pasos (opcionales)
- Manejar 401/403 con redirección a /login y mensajes más claros.
- Loading states en las vistas.
- Implementar /auth/refresh en el backend y renovar tokens automáticamente.
- Agregar vistas de Catálogo/Proveedores en modo lectura.


python -m http.server 8000

docker build -t emeday17/eventos-iam-frontend:1.0.0 .
docker push emeday17/eventos-iam-frontend:1.0.0