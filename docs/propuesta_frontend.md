# 🎨 Propuesta Frontend - Plataforma Eventos Perú

## 📋 Resumen Ejecutivo

**Objetivo**: Desarrollar una aplicación web moderna, responsive y profesional para la gestión integral de eventos en Perú, consumiendo los microservicios backend existentes.

**Stack Tecnológico Recomendado**: **Vue.js 3 + Vite + TypeScript + Tailwind CSS**

**Justificación de la Elección**:
- ✅ **Vue.js 3**: Composición API reactiva, ligero, curva de aprendizaje suave
- ✅ **Vite**: Build ultrarrápido, HMR instantáneo, optimización automática
- ✅ **TypeScript**: Type-safety para endpoints, mejor DX, menos bugs
- ✅ **Tailwind CSS**: Utility-first, diseño consistente, bundle pequeño
- ✅ **Pinia**: State management oficial de Vue 3
- ✅ **Vue Router**: Navegación SPA con guards para autenticación
- ✅ **Axios**: Cliente HTTP con interceptores JWT
- ✅ **Deployment**: Nginx + Docker + Kubernetes (misma arquitectura backend)

---

## 📋 Plan de Implementación Paso a Paso

### 🚀 Fase 0: Instalación y Setup (30 minutos)

#### **Requisitos Previos**
```bash
# 1. Verificar Node.js (mínimo v18)
node --version
# Debe mostrar: v18.x.x o superior

# 2. Si no tienes Node.js:
# Descargar desde https://nodejs.org/
# Recomendado: Node.js 20.x LTS
```

#### **Componentes a Instalar**
```bash
# 1. Crear proyecto Vite + Vue 3 + TypeScript
npm create vite@latest frontend-eventos-peru -- --template vue-ts
cd frontend-eventos-peru

# 2. Instalar Tailwind CSS
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# 3. Instalar dependencias principales
npm install vue-router@4 pinia axios

# 4. Instalar dependencias de UI (componentes headless)
npm install @headlessui/vue @heroicons/vue

# 5. Instalar utilidades
npm install date-fns jwt-decode

# 6. Instalar dependencias de desarrollo
npm install -D @types/node
```

#### **Configuración Inicial**

**1. Configurar Tailwind** (`tailwind.config.js`):
```js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#fef2f2',
          100: '#fee2e2',
          200: '#fecaca',
          300: '#fca5a5',
          400: '#f87171',
          500: '#ef4444',  // Main
          600: '#dc2626',
          700: '#b91c1c',
          800: '#991b1b',
          900: '#7f1d1d',
        },
      },
    },
  },
  plugins: [],
}
```

**2. Crear archivo CSS** (`src/style.css`):
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

**3. Crear estructura de carpetas**:
```bash
mkdir -p src/api src/stores src/router src/views/{public,client,admin}
mkdir -p src/components/{common,forms,layout} src/composables src/types src/utils
```

---

### 📊 Lista Priorizada de Vistas (Orden de Desarrollo)

#### **Iteración 1: Fundación (Semana 1-2)** ✅
1. **Login** → `/login` → `POST /auth/login`
2. **Home Pública** → `/` → Sin endpoints (landing page)
3. **Layout Base** → Componente wrapper con slot
4. **Navbar** → Componente reutilizable (público/cliente/admin)

#### **Iteración 2: Panel Cliente (Semana 3-4)** 🎯
5. **Dashboard Cliente** → `/cliente/dashboard` → `GET /auth/profile`
6. **Catálogo Paquetes** → `/cliente/paquetes` → `GET /paquetes`
7. **Wizard Pedido (Paso 1)** → `/cliente/pedido/nuevo` → `GET /tipos-evento`, `GET /paquetes`
8. **Wizard Pedido (Paso 2)** → `/cliente/pedido/nuevo/servicios` → `GET /servicios`
9. **Wizard Pedido (Paso 3)** → `/cliente/pedido/nuevo/confirmacion` → `POST /pedidos`
10. **Mis Pedidos** → `/cliente/pedidos` → `GET /pedidos`

#### **Iteración 3: Panel Admin (Semana 5-6)** ⚙️
11. **Dashboard Admin** → `/admin/dashboard` → Estadísticas agregadas
12. **Gestión Tipos Evento** → `/admin/tipos-evento` → `GET`, `POST`, `PUT`, `DELETE /tipos-evento`
13. **Gestión Servicios** → `/admin/servicios` → `GET`, `POST`, `PUT`, `DELETE /servicios`
14. **Gestión Paquetes** → `/admin/paquetes` → `GET`, `POST`, `PUT`, `DELETE /paquetes`
15. **Gestión Proveedores** → `/admin/proveedores` → `GET`, `POST`, `PUT`, `DELETE /proveedores`
16. **Gestión Usuarios** → `/admin/usuarios` → `GET`, `POST`, `PUT`, `DELETE /admin/users`

#### **Iteración 4: Features Avanzadas (Semana 7-8)** 🚀
17. **Perfil Usuario** → `/perfil` → `GET /auth/profile`, `PUT /auth/profile`
18. **Notificaciones** → Componente overlay (Toasts)
19. **Búsqueda Global** → Componente modal
20. **Reportes** → `/admin/reportes` → Endpoints personalizados

---

### 🗺️ Mapeo Completo: Vista → Ruta → Endpoints → JSON

#### **1. Login** 🔑
```
┌─────────────────────────────────────────────────────────────────┐
│ Vista: src/views/public/Login.vue                               │
│ Ruta: /login                                                    │
│ Método: Público (sin autenticación)                            │
└─────────────────────────────────────────────────────────────────┘

📡 Endpoint: POST http://localhost:5001/auth/login
Headers: 
  Content-Type: application/json

📤 Request JSON:
{
  "email": "cliente@test.com",
  "password": "cliente123"
}

📥 Response JSON (200):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjbGllbnRlQHRlc3QuY29tIiwicm9sZSI6IkNMSUVOVEUiLCJleHAiOjE3MzI3MTg0MDB9.xyz...",
  "token_type": "bearer",
  "usuario": {
    "id": 1,
    "nombre": "Juan",
    "apellido": "Pérez",
    "email": "cliente@test.com",
    "role": "CLIENTE"
  }
}

🎬 Acciones en Frontend:
1. Guardar access_token en localStorage
2. Guardar usuario en Pinia store (auth.ts)
3. Redirigir según role:
   - CLIENTE → /cliente/dashboard
   - ADMIN → /admin/dashboard
```

... (document continued in full)

