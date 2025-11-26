# Frontend Eventos Perú (Vanilla Hexagonal)

Frontend ligero construido con HTML5, Bootstrap 5 y JavaScript Vanilla, siguiendo una arquitectura hexagonal simplificada.

## 🚀 Inicio Rápido

### Opción 1: Servidor Local (Node.js)

Si tienes Node.js instalado:

```bash
npx serve .
```

### Opción 2: Python

```bash
python -m http.server 8000
```

Luego abre `http://localhost:8000` en tu navegador.

## 🏗️ Arquitectura

- **`js/adapters/`**: Comunicación con microservicios (Puertos de salida).
- **`js/domain/`**: Lógica de negocio (si fuera necesaria más compleja).
- **`js/app/`**: Controladores de vista.
- **`js/config.js`**: Configuración de entorno.

## 🐳 Docker

```bash
docker build -t eventos-peru/frontend .
docker run -p 8080:80 eventos-peru/frontend
```
