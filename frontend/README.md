# Frontend - Eventos Perú

Frontend moderno construido con **Vite + React + TypeScript** siguiendo **Arquitectura Hexagonal**.

## 🏗️ Arquitectura

```
src/
├── services/          # Adaptadores API (Hexagonal - Puertos)
├── hooks/             # Custom hooks (Lógica de aplicación)
├── stores/            # Estado global (Zustand)
├── components/        # Componentes UI
├── pages/             # Páginas de la aplicación
├── types/             # Tipos TypeScript
└── lib/               # Utilidades y configuración
```

## 🚀 Inicio Rápido

### Desarrollo Local

```bash
# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev

# La aplicación estará disponible en http://localhost:5173
```

### Build de Producción

```bash
# Crear build optimizado
npm run build

# Preview del build
npm run preview
```

## 🔧 Configuración

### Variables de Entorno

Crea un archivo `.env.local` para sobrescribir las URLs de desarrollo:

```env
VITE_IAM_URL=http://localhost:8010
VITE_CATALOGO_URL=http://localhost:8020
VITE_PROVEEDORES_URL=http://localhost:8030
VITE_CONTRATACION_URL=http://localhost:8040
```

## 🐳 Docker

### Construir imagen

```bash
docker build -t eventos-peru/frontend:latest .
```

### Ejecutar contenedor

```bash
docker run -p 8080:80 eventos-peru/frontend:latest
```

## ☸️ Kubernetes

### Desplegar en Kubernetes

```bash
# Aplicar ConfigMap
kubectl apply -f k8s/configmap.yaml

# Aplicar Deployment
kubectl apply -f k8s/deployment.yaml

# Aplicar Service
kubectl apply -f k8s/service.yaml

# Aplicar Ingress
kubectl apply -f k8s/ingress.yaml
```

### Verificar despliegue

```bash
# Ver pods
kubectl get pods -l app=frontend

# Ver logs
kubectl logs -f deployment/frontend

# Ver servicio
kubectl get svc frontend-service
```

## 📦 Tecnologías

- **Vite** - Build tool ultrarrápido
- **React 18** - Librería UI
- **TypeScript** - Type safety
- **React Router** - Routing
- **Zustand** - State management
- **Axios** - HTTP client
- **Tailwind CSS** - Styling

## 🎨 Características

- ✅ Arquitectura Hexagonal (Puertos y Adaptadores)
- ✅ TypeScript para type safety
- ✅ Autenticación JWT
- ✅ Rutas protegidas
- ✅ Estado global con Zustand
- ✅ Custom hooks reutilizables
- ✅ Diseño responsive con Tailwind
- ✅ Optimizado para producción
- ✅ Listo para Kubernetes

## 🔐 Credenciales de Prueba

```
Email: demo@eventos.pe
Password: Admin_2025!
```

## 📝 Scripts Disponibles

- `npm run dev` - Inicia servidor de desarrollo
- `npm run build` - Crea build de producción
- `npm run preview` - Preview del build
- `npm run lint` - Ejecuta linter

## 🌐 Integración con Backend

El frontend se comunica con 4 microservicios:

1. **IAM Service** (8010) - Autenticación y usuarios
2. **Catálogo Service** (8020) - Servicios y paquetes
3. **Proveedores Service** (8030) - Gestión de proveedores
4. **Contratación Service** (8040) - Pedidos y cotizaciones

## 📖 Documentación Adicional

Ver el README principal del proyecto para más información sobre la arquitectura general del sistema.

---

© 2025 Emeday Inc. Todos los derechos reservados.
