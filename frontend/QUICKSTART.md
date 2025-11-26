# 🎉 Frontend Eventos Perú - Guía de Inicio Rápido

## ✅ Estado del Proyecto

El frontend ha sido creado exitosamente con la siguiente estructura:

```
frontend/
├── src/
│   ├── services/          # ✅ 4 adaptadores API (IAM, Catálogo, Proveedores, Contratación)
│   ├── hooks/             # ✅ Custom hooks (useAuth, usePedidos, useCatalogo)
│   ├── stores/            # ✅ Store de autenticación (Zustand)
│   ├── components/        # ✅ Componentes UI (auth, shared)
│   ├── pages/             # ✅ 5 páginas principales
│   ├── types/             # ✅ Tipos TypeScript completos
│   └── lib/               # ✅ Configuración y utilidades
├── k8s/                   # ✅ Manifiestos de Kubernetes
├── Dockerfile             # ✅ Multi-stage build
├── nginx.conf             # ✅ Configuración de nginx
└── README.md              # ✅ Documentación
```

## 🚀 Cómo Ejecutar

### 1. El servidor de desarrollo YA ESTÁ CORRIENDO

```
✅ URL: http://localhost:5173
✅ Hot reload activado
✅ Listo para desarrollo
```

### 2. Asegúrate de que tu backend esté corriendo

Ejecuta en otra terminal (desde la raíz del proyecto):

```powershell
.\start-services.ps1
```

Esto iniciará los 4 microservicios:
- IAM Service: http://localhost:8010
- Catálogo Service: http://localhost:8020
- Proveedores Service: http://localhost:8030
- Contratación Service: http://localhost:8040

### 3. Abre el navegador

Navega a: **http://localhost:5173**

## 🔐 Credenciales de Prueba

```
Email: demo@eventos.pe
Password: Admin_2025!
```

## 📱 Páginas Disponibles

1. **Login** (`/login`) - ✅ Implementado
2. **Registro** (`/register`) - ✅ Implementado
3. **Dashboard** (`/dashboard`) - ✅ Implementado
4. **Catálogo** (`/catalogo`) - ✅ Implementado
5. **Mis Pedidos** (`/mis-pedidos`) - ✅ Implementado

## 🏗️ Arquitectura Hexagonal Implementada

### Capa de Dominio
- ✅ Tipos TypeScript en `src/types/`
- ✅ Entidades: Usuario, Pedido, Servicio, Paquete, Proveedor

### Capa de Aplicación
- ✅ Custom Hooks (casos de uso)
- ✅ `useAuth` - Autenticación
- ✅ `usePedidos` - Gestión de pedidos
- ✅ `useCatalogo` - Gestión de catálogo

### Capa de Infraestructura (Adaptadores)
- ✅ `authService` - Adaptador IAM
- ✅ `catalogoService` - Adaptador Catálogo
- ✅ `proveedoresService` - Adaptador Proveedores
- ✅ `contratacionService` - Adaptador Contratación

### Capa de Presentación
- ✅ Componentes React
- ✅ Rutas protegidas
- ✅ UI moderna con Tailwind CSS

## 🎨 Características Implementadas

- ✅ **Autenticación JWT** - Login/Registro/Logout
- ✅ **Rutas Protegidas** - Verificación de autenticación
- ✅ **Roles** - Soporte para ADMIN y CLIENT
- ✅ **Estado Global** - Zustand para auth
- ✅ **HTTP Client** - Axios con interceptores JWT
- ✅ **TypeScript** - Type safety completo
- ✅ **Responsive Design** - Tailwind CSS
- ✅ **Loading States** - Spinners y feedback
- ✅ **Error Handling** - Alertas y mensajes
- ✅ **Dark Mode** - Soporte automático

## 🐳 Despliegue en Kubernetes

### Construir imagen Docker

```bash
cd frontend
docker build -t eventos-peru/frontend:latest .
```

### Desplegar en Kubernetes

```bash
# Aplicar todos los manifiestos
kubectl apply -f k8s/

# Verificar despliegue
kubectl get pods -l app=frontend
kubectl get svc frontend-service
kubectl get ingress eventos-peru-ingress
```

## 📊 Próximos Pasos Sugeridos

### Para MVP Académico (Prioridad Alta)
1. ✅ **COMPLETADO**: Estructura base y autenticación
2. ✅ **COMPLETADO**: Integración con backend
3. 🔄 **PENDIENTE**: Página de detalle de paquete
4. 🔄 **PENDIENTE**: Formulario de crear pedido
5. 🔄 **PENDIENTE**: Panel de administración

### Para Producción (Futuro)
1. Testing (Vitest + React Testing Library)
2. CI/CD Pipeline
3. Monitoreo y logging
4. Optimización de performance
5. SEO y meta tags

## 🛠️ Comandos Útiles

```bash
# Desarrollo
npm run dev              # Iniciar servidor de desarrollo

# Build
npm run build            # Crear build de producción
npm run preview          # Preview del build

# Linting
npm run lint             # Ejecutar ESLint

# Docker
docker build -t eventos-peru/frontend .
docker run -p 8080:80 eventos-peru/frontend

# Kubernetes
kubectl apply -f k8s/
kubectl delete -f k8s/
kubectl logs -f deployment/frontend
```

## 📝 Notas Importantes

1. **Variables de Entorno**: Las URLs de los microservicios se configuran en `.env.development` para desarrollo local y en `ConfigMap` para Kubernetes.

2. **CORS**: Asegúrate de que tus microservicios backend tengan CORS configurado para aceptar peticiones desde `http://localhost:5173`.

3. **Proxy**: Vite está configurado con proxy para desarrollo local, redirigiendo `/api/*` a los microservicios correspondientes.

4. **TypeScript**: Todos los tipos están definidos en `src/types/index.ts` y mapean directamente a los modelos del backend.

## 🎓 Para Presentación Académica

### Puntos Clave a Destacar:

1. **Arquitectura Hexagonal**:
   - Separación clara de capas
   - Puertos (interfaces) y Adaptadores
   - Independencia del framework

2. **Escalabilidad**:
   - Listo para Kubernetes
   - Microservicios independientes
   - Horizontal scaling

3. **Buenas Prácticas**:
   - TypeScript para type safety
   - Custom hooks reutilizables
   - Componentes modulares
   - Estado global centralizado

4. **Integración**:
   - Comunicación con 4 microservicios
   - Autenticación JWT
   - Manejo de errores robusto

## 📞 Soporte

Si encuentras algún problema:

1. Verifica que todos los servicios backend estén corriendo
2. Revisa la consola del navegador para errores
3. Verifica los logs del servidor de desarrollo
4. Asegúrate de que las URLs en `.env.development` sean correctas

---

**¡El frontend está listo para demostrar tu MVP académico!** 🚀

© 2025 Emeday Inc.
