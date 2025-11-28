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
          500: '#ef4444',
          600: '#dc2626',
          700: '#b91c1c',
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

#### **2. Dashboard Cliente** 👤
```
┌─────────────────────────────────────────────────────────────────┐
│ Vista: src/views/client/Dashboard.vue                          │
│ Ruta: /cliente/dashboard                                       │
│ Método: Requiere autenticación + role CLIENTE                  │
└─────────────────────────────────────────────────────────────────┘

📡 Endpoint 1: GET http://localhost:5001/auth/profile
Headers: 
  Authorization: Bearer {token}

📥 Response JSON (200):
{
  "id": 1,
  "nombre": "Juan",
  "apellido": "Pérez",
  "email": "cliente@test.com",
  "telefono": "+51 987654321",
  "role": "CLIENTE"
}

📡 Endpoint 2: GET http://localhost:5003/pedidos?usuario_id=1
Headers: 
  Authorization: Bearer {token}

📥 Response JSON (200):
{
  "data": [
    {
      "id": 101,
      "fecha_evento": "2025-12-25",
      "estado": "CONFIRMADO",
      "total": 15000.00,
      "tipo_evento_nombre": "Boda",
      "num_invitados": 150
    },
    {
      "id": 102,
      "fecha_evento": "2026-02-10",
      "estado": "PENDIENTE",
      "total": 10000.00,
      "tipo_evento_nombre": "Quinceañera",
      "num_invitados": 100
    }
  ],
  "total": 2
}

🎨 Elementos UI:
- Saludo personalizado: "Bienvenido, Juan Pérez"
- Tarjetas de estadísticas:
  * Próximos eventos (count)
  * Total gastado (sum)
  * Pedidos completados (count)
- Lista de próximos pedidos (ordenados por fecha_evento)
- Botón CTA: "+ Crear Nuevo Pedido" → /cliente/pedido/nuevo
```

#### **3. Catálogo de Paquetes** 📦
```
┌─────────────────────────────────────────────────────────────────┐
│ Vista: src/views/client/CatalogoPaquetes.vue                   │
│ Ruta: /cliente/paquetes                                        │
│ Método: Requiere autenticación + role CLIENTE                  │
└─────────────────────────────────────────────────────────────────┘

📡 Endpoint: GET http://localhost:5002/paquetes
Headers: 
  Authorization: Bearer {token}

Query Params (opcional):
  ?tipo_evento_id=1  (filtrar por tipo evento)

📥 Response JSON (200):
{
  "data": [
    {
      "id": 1,
      "nombre": "Paquete Boda Clásica",
      "descripcion": "Incluye decoración, catering básico, fotografía",
      "precio_base": 12000.00,
      "tipo_evento_id": 1,
      "tipo_evento_nombre": "Boda",
      "servicios": [
        {
          "id": 1,
          "nombre": "Decoración Floral Premium",
          "categoria": "DECORACION"
        },
        {
          "id": 2,
          "nombre": "Buffet 150 personas",
          "categoria": "CATERING"
        },
        {
          "id": 3,
          "nombre": "Fotografía 6 horas",
          "categoria": "FOTOGRAFIA"
        }
      ]
    },
    {
      "id": 2,
      "nombre": "Paquete Quinceañera Elegante",
      "descripcion": "Todo incluido para 15 años inolvidables",
      "precio_base": 8000.00,
      "tipo_evento_id": 2,
      "tipo_evento_nombre": "Quinceañera",
      "servicios": [
        {
          "id": 5,
          "nombre": "Decoración Temática",
          "categoria": "DECORACION"
        },
        {
          "id": 6,
          "nombre": "Buffet 100 personas",
          "categoria": "CATERING"
        }
      ]
    }
  ],
  "total": 2
}

🎨 Elementos UI:
- Filtro dropdown: Tipo de Evento (carga de GET /tipos-evento)
- Grid de tarjetas responsive (3 columnas desktop, 1 móvil)
- Cada tarjeta muestra:
  * Nombre del paquete
  * Descripción (truncada a 2 líneas)
  * Precio (formato: S/ 12,000.00)
  * Lista de servicios incluidos (badges)
  * Botón "Seleccionar" → redirige a /cliente/pedido/nuevo?paquete_id=1
```

#### **4. Wizard Pedido - Paso 1 (Tipo Evento + Paquete)** 🎯
```
┌─────────────────────────────────────────────────────────────────┐
│ Vista: src/views/client/PedidoWizard/Paso1.vue                 │
│ Ruta: /cliente/pedido/nuevo                                    │
│ Método: Requiere autenticación + role CLIENTE                  │
└─────────────────────────────────────────────────────────────────┘

📡 Endpoint 1: GET http://localhost:5002/tipos-evento
Headers: 
  Authorization: Bearer {token}

📥 Response JSON (200):
{
  "data": [
    {"id": 1, "nombre": "Boda", "descripcion": "Ceremonias matrimoniales"},
    {"id": 2, "nombre": "Quinceañera", "descripcion": "Celebración 15 años"},
    {"id": 3, "nombre": "Cumpleaños", "descripcion": "Fiestas de cumpleaños"}
  ]
}

📡 Endpoint 2: GET http://localhost:5002/paquetes?tipo_evento_id=1
Headers: 
  Authorization: Bearer {token}

📥 Response JSON (200):
{
  "data": [
    {
      "id": 1,
      "nombre": "Paquete Boda Clásica",
      "precio_base": 12000.00,
      "servicios": [...]
    },
    {
      "id": 2,
      "nombre": "Paquete Boda Premium",
      "precio_base": 18000.00,
      "servicios": [...]
    }
  ]
}

📝 Formulario (Campos):
1. Select: Tipo de Evento * (obligatorio)
   - Carga opciones de GET /tipos-evento
   - onChange → carga paquetes filtrados

2. Radio Group: Selección de Paquete (opcional)
   - Opción: "Sin paquete (servicios a la carta)"
   - Lista de paquetes como radio buttons
   - Cada opción muestra: nombre, precio, servicios incluidos

3. Date Picker: Fecha del Evento * (obligatorio)
   - Validación: fecha futura (min: hoy + 30 días)
   - Format: DD/MM/YYYY

4. Input Number: Número de Invitados * (obligatorio)
   - Min: 10, Max: 1000
   - Step: 10

💾 Estado Local (Pinia store):
{
  tipo_evento_id: 1,
  paquete_id: 1,  // null si "sin paquete"
  fecha_evento: "2025-12-25",
  num_invitados: 150
}

🎬 Botones:
- "Cancelar" → Redirige a /cliente/dashboard
- "Siguiente →" → Valida campos, guarda en store, redirige a paso 2
```

#### **5. Wizard Pedido - Paso 2 (Servicios Adicionales)** ➕
```
┌─────────────────────────────────────────────────────────────────┐
│ Vista: src/views/client/PedidoWizard/Paso2.vue                 │
│ Ruta: /cliente/pedido/nuevo/servicios                          │
│ Método: Requiere autenticación + role CLIENTE                  │
└─────────────────────────────────────────────────────────────────┘

📡 Endpoint: GET http://localhost:5002/servicios?tipo_evento_id=1
Headers: 
  Authorization: Bearer {token}

📥 Response JSON (200):
{
  "data": [
    {
      "id": 5,
      "nombre": "Fotografía Premium",
      "descripcion": "Fotógrafo profesional, 8 horas",
      "categoria": "FOTOGRAFIA",
      "precio_unitario": 1500.00,
      "disponible": true
    },
    {
      "id": 6,
      "nombre": "Video 4K",
      "descripcion": "Videografía cinematográfica",
      "categoria": "VIDEO",
      "precio_unitario": 2000.00,
      "disponible": true
    },
    {
      "id": 7,
      "nombre": "DJ Profesional",
      "descripcion": "DJ + equipo de sonido",
      "categoria": "ENTRETENIMIENTO",
      "precio_unitario": 800.00,
      "disponible": false
    }
  ]
}

📝 Formulario:
1. Servicios Adicionales (Checkbox Group)
   - Agrupados por categoría (FOTOGRAFIA, VIDEO, ENTRETENIMIENTO, etc.)
   - Cada checkbox muestra:
     * Nombre del servicio
     * Descripción corta
     * Precio unitario
     * Badge "No disponible" si disponible=false (disabled)

2. Textarea: Comentarios Especiales (opcional)
   - Max length: 500 caracteres
   - Placeholder: "Ej: Preferencia por colores pasteles, alergia a flores..."

💰 Resumen de Precio (Panel lateral):
┌──────────────────────────────────────────┐
│ Subtotal Paquete:        S/ 12,000.00    │
│ Servicios Adicionales:                   │
│   - Fotografía Premium   S/  1,500.00    │
│   - Video 4K             S/  2,000.00    │
│ ──────────────────────────────────────   │
│ TOTAL:                   S/ 15,500.00    │
└──────────────────────────────────────────┘

💾 Estado Local (Pinia store):
{
  ...paso1,
  servicios_adicionales: [5, 6],  // IDs de servicios seleccionados
  comentarios: "Preferencia por colores pasteles"
}

🎬 Botones:
- "← Atrás" → Vuelve a paso 1 (mantiene datos)
- "Siguiente →" → Guarda en store, redirige a paso 3
```

#### **6. Wizard Pedido - Paso 3 (Confirmación)** ✅
```
┌─────────────────────────────────────────────────────────────────┐
│ Vista: src/views/client/PedidoWizard/Paso3.vue                 │
│ Ruta: /cliente/pedido/nuevo/confirmacion                       │
│ Método: Requiere autenticación + role CLIENTE                  │
└─────────────────────────────────────────────────────────────────┘

📡 Endpoint: POST http://localhost:5003/pedidos
Headers: 
  Authorization: Bearer {token}
  Content-Type: application/json

📤 Request JSON:
{
  "tipo_evento_id": 1,
  "fecha_evento": "2025-12-25",
  "num_invitados": 150,
  "paquete_id": 1,
  "servicios_adicionales": [5, 6],
  "comentarios": "Preferencia por colores pasteles"
}

📥 Response JSON (201):
{
  "id": 103,
  "fecha_evento": "2025-12-25",
  "estado": "PENDIENTE",
  "total": 15500.00,
  "created_at": "2025-11-27T10:30:00",
  "tipo_evento_nombre": "Boda"
}

🎨 Elementos UI (Resumen Completo):
┌──────────────────────────────────────────────────────────┐
│ Resumen de tu Pedido                                     │
├──────────────────────────────────────────────────────────┤
│ Tipo de Evento: Boda                                     │
│ Fecha: 25 de Diciembre de 2025                           │
│ Invitados: 150 personas                                  │
├──────────────────────────────────────────────────────────┤
│ Paquete Seleccionado:                                    │
│ • Paquete Boda Clásica - S/ 12,000.00                    │
│   Incluye:                                               │
│   - Decoración Floral Premium                            │
│   - Buffet 150 personas                                  │
│   - Fotografía 6 horas                                   │
├──────────────────────────────────────────────────────────┤
│ Servicios Adicionales:                                   │
│ • Fotografía Premium - S/ 1,500.00                       │
│ • Video 4K - S/ 2,000.00                                 │
├──────────────────────────────────────────────────────────┤
│ Comentarios:                                             │
│ "Preferencia por colores pasteles"                      │
├──────────────────────────────────────────────────────────┤
│ TOTAL A PAGAR: S/ 15,500.00                              │
└──────────────────────────────────────────────────────────┘

🎬 Botones:
- "← Editar" → Vuelve a paso 2
- "Confirmar Pedido" → Envía POST /pedidos
  - Loading state mientras procesa
  - Success → Modal de éxito + redirige a /cliente/pedidos
  - Error → Toast de error con mensaje
```

#### **7. Mis Pedidos (Cliente)** 📋
```
┌─────────────────────────────────────────────────────────────────┐
│ Vista: src/views/client/MisPedidos.vue                         │
│ Ruta: /cliente/pedidos                                         │
│ Método: Requiere autenticación + role CLIENTE                  │
└─────────────────────────────────────────────────────────────────┘

📡 Endpoint: GET http://localhost:5003/pedidos?usuario_id=1
Headers: 
  Authorization: Bearer {token}

Query Params (opcional):
  ?estado=PENDIENTE  (filtrar por estado)

📥 Response JSON (200):
{
  "data": [
    {
      "id": 103,
      "tipo_evento_nombre": "Boda",
      "fecha_evento": "2025-12-25",
      "num_invitados": 150,
      "estado": "PENDIENTE",
      "total": 15500.00,
      "created_at": "2025-11-27T10:30:00"
    },
    {
      "id": 101,
      "tipo_evento_nombre": "Boda",
      "fecha_evento": "2025-12-25",
      "num_invitados": 150,
      "estado": "CONFIRMADO",
      "total": 15000.00,
      "created_at": "2025-10-15T09:00:00"
    }
  ],
  "total": 2
}

🎨 Elementos UI:
- Filtro dropdown: Estado (TODOS, PENDIENTE, CONFIRMADO, CANCELADO)
- Lista de tarjetas (no tabla, más visual):
  ┌──────────────────────────────────────────────┐
  │ 🎂 Boda - 25 Dic 2025                        │
  │ Estado: [PENDIENTE]  Total: S/ 15,500.00     │
  │ Invitados: 150  •  Creado: 27 Nov 2025       │
  │ [Ver Detalles] [Descargar PDF]               │
  └──────────────────────────────────────────────┘
- Badge de color según estado:
  * PENDIENTE → amarillo
  * CONFIRMADO → verde
  * CANCELADO → rojo
```

#### **8. Gestión Tipos de Evento (Admin)** ⚙️
```
┌─────────────────────────────────────────────────────────────────┐
│ Vista: src/views/admin/TiposEvento.vue                         │
│ Ruta: /admin/tipos-evento                                      │
│ Método: Requiere autenticación + role ADMIN                    │
└─────────────────────────────────────────────────────────────────┘

📡 Endpoint 1: GET http://localhost:5002/tipos-evento
Headers: 
  Authorization: Bearer {token}

📥 Response JSON (200):
{
  "data": [
    {
      "id": 1,
      "nombre": "Boda",
      "descripcion": "Ceremonias matrimoniales",
      "created_at": "2025-01-15T08:00:00"
    },
    {
      "id": 2,
      "nombre": "Quinceañera",
      "descripcion": "Celebración 15 años",
      "created_at": "2025-01-15T08:00:00"
    }
  ]
}

📡 Endpoint 2: POST http://localhost:5002/tipos-evento
Headers: 
  Authorization: Bearer {token}
  Content-Type: application/json

📤 Request JSON:
{
  "nombre": "Conferencia Corporativa",
  "descripcion": "Eventos empresariales y seminarios"
}

📥 Response JSON (201):
{
  "id": 10,
  "nombre": "Conferencia Corporativa",
  "descripcion": "Eventos empresariales y seminarios",
  "created_at": "2025-11-27T11:00:00"
}

📡 Endpoint 3: PUT http://localhost:5002/tipos-evento/10
📤 Request JSON:
{
  "nombre": "Conferencia Empresarial",
  "descripcion": "Eventos corporativos, seminarios y talleres"
}

📡 Endpoint 4: DELETE http://localhost:5002/tipos-evento/10
📥 Response: 204 No Content

🎨 Elementos UI:
- Header con botón "+ Nuevo Tipo Evento" → Abre modal
- Barra de búsqueda (filtra local por nombre/descripción)
- Tabla responsive:
  ┌──────┬───────────────────┬──────────────────────────┬────────────┐
  │  ID  │ Nombre            │ Descripción              │ Acciones   │
  ├──────┼───────────────────┼──────────────────────────┼────────────┤
  │   1  │ Boda              │ Ceremonias matrimoniales │ [✏️] [🗑️] │
  │   2  │ Quinceañera       │ Celebración 15 años      │ [✏️] [🗑️] │
  └──────┴───────────────────┴──────────────────────────┴────────────┘
- Paginación (10 items por página)

📝 Modal Crear/Editar:
┌──────────────────────────────────┐
│ Nuevo Tipo de Evento         [✕] │
├──────────────────────────────────┤
│ Nombre *                         │
│ [_________________________]      │
│                                  │
│ Descripción *                    │
│ [_________________________]      │
│ [_________________________]      │
│                                  │
│      [Cancelar]  [Guardar]       │
└──────────────────────────────────┘

🗑️ Modal Confirmar Eliminación:
┌──────────────────────────────────┐
│ Confirmar Eliminación        [✕] │
├──────────────────────────────────┤
│ ⚠️ ¿Estás seguro de eliminar el │
│ tipo de evento "Boda"?           │
│                                  │
│ Esta acción no se puede deshacer.│
│                                  │
│      [Cancelar]  [Eliminar]      │
└──────────────────────────────────┘
```

#### **9. Gestión Usuarios (Admin)** 👥
```
┌─────────────────────────────────────────────────────────────────┐
│ Vista: src/views/admin/Usuarios.vue                            │
│ Ruta: /admin/usuarios                                          │
│ Método: Requiere autenticación + role ADMIN                    │
└─────────────────────────────────────────────────────────────────┘

📡 Endpoint 1: GET http://localhost:5001/admin/users
Headers: 
  Authorization: Bearer {token}

📥 Response JSON (200):
{
  "data": [
    {
      "id": 1,
      "nombre": "Juan",
      "apellido": "Pérez",
      "email": "cliente@test.com",
      "telefono": "+51 987654321",
      "role": "CLIENTE",
      "activo": true,
      "created_at": "2025-10-01T08:00:00"
    },
    {
      "id": 2,
      "nombre": "Admin",
      "apellido": "Sistema",
      "email": "admin@test.com",
      "telefono": null,
      "role": "ADMIN",
      "activo": true,
      "created_at": "2025-01-01T08:00:00"
    }
  ]
}

📡 Endpoint 2: POST http://localhost:5001/admin/users
📤 Request JSON:
{
  "nombre": "María",
  "apellido": "García",
  "email": "maria@test.com",
  "telefono": "+51 999888777",
  "password": "maria123",
  "role": "CLIENTE"
}

📡 Endpoint 3: PUT http://localhost:5001/admin/users/1
📤 Request JSON:
{
  "role": "ADMIN"  // Cambiar role
}

📡 Endpoint 4: DELETE http://localhost:5001/admin/users/1
📥 Response: 204 No Content

🎨 Elementos UI:
- Filtros:
  * Select: Role (TODOS, CLIENTE, ADMIN)
  * Select: Estado (TODOS, ACTIVO, INACTIVO)
  * Search: Email/Nombre
- Botón: "+ Nuevo Usuario"
- Tabla:
  ┌────┬──────────────┬────────────────────┬─────────┬────────┬────────────┐
  │ ID │ Nombre       │ Email              │ Role    │ Estado │ Acciones   │
  ├────┼──────────────┼────────────────────┼─────────┼────────┼────────────┤
  │  1 │ Juan Pérez   │ cliente@test.com   │ CLIENTE │ ✅     │ [✏️] [🗑️] │
  │  2 │ Admin Sist.  │ admin@test.com     │ ADMIN   │ ✅     │ [✏️] [🗑️] │
  └────┴──────────────┴────────────────────┴─────────┴────────┴────────────┘
```

---

### 🎨 Wireframes ASCII de Pantallas Principales

#### **Wireframe 1: Landing Page** 🏠
```
┌───────────────────────────────────────────────────────────────────┐
│  [LOGO] EventosPeru       [Inicio] [Servicios] [Login] [Registrar]│
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│              ╔═══════════════════════════════════════╗            │
│              ║   Organiza el Evento de tus Sueños    ║            │
│              ║   Bodas • Quinceañeras • Cumpleaños   ║            │
│              ╚═══════════════════════════════════════╝            │
│                                                                   │
│                    [ Explorar Paquetes ]                          │
│                    [ ¿Cómo funciona? ]                            │
│                                                                   │
├───────────────────────────────────────────────────────────────────┤
│  Nuestros Servicios                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │   🎂 Bodas   │  │ 👗 Quinceañ.  │  │ 🎉 Cumpleaños│            │
│  │              │  │               │  │              │            │
│  │ Desde        │  │ Desde         │  │ Desde        │            │
│  │ S/ 8,000     │  │ S/ 5,000      │  │ S/ 2,000     │            │
│  │              │  │               │  │              │            │
│  │ [Ver más →]  │  │ [Ver más →]   │  │ [Ver más →]  │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
│                                                                   │
├───────────────────────────────────────────────────────────────────┤
│  ¿Cómo funciona?                                                  │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ 1️⃣ Elige tu tipo de evento                                  │  │
│  │ 2️⃣ Selecciona paquete o servicios a la carta                │  │
│  │ 3️⃣ Confirma y recibe cotización                             │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                   │
├───────────────────────────────────────────────────────────────────┤
│  © 2025 EventosPeru | Términos | Privacidad | Contacto           │
└───────────────────────────────────────────────────────────────────┘
```

#### **Wireframe 2: Login** 🔑
```
┌───────────────────────────────────────────────────────────────────┐
│  [LOGO] EventosPeru                         [← Volver a Inicio]   │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│                   ┌───────────────────────────┐                   │
│                   │   Iniciar Sesión          │                   │
│                   ├───────────────────────────┤                   │
│                   │ Email:                    │                   │
│                   │ [______________________]  │                   │
│                   │                           │                   │
│                   │ Contraseña:               │                   │
│                   │ [______________________] 👁│                   │
│                   │                           │                   │
│                   │ ☐ Recordarme              │                   │
│                   │                           │                   │
│                   │ [  Iniciar Sesión  ]      │                   │
│                   │                           │                   │
│                   │ ¿Olvidaste tu contraseña? │                   │
│                   │                           │                   │
│                   │ ─────── o ───────         │                   │
│                   │                           │                   │
│                   │ ¿No tienes cuenta?        │                   │
│                   │ [   Registrarse   ]       │                   │
│                   └───────────────────────────┘                   │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

#### **Wireframe 3: Dashboard Cliente** 👤
```
┌───────────────────────────────────────────────────────────────────┐
│ [☰] EventosPeru  [🏠 Dashboard] [📦 Paquetes] [📋 Mis Pedidos] [👤 Juan Pérez ▾] │
├───────────────────────────────────────────────────────────────────┤
│  Bienvenido, Juan Pérez                        [+ Crear Pedido]   │
├───────────────────────────────────────────────────────────────────┤
│  Estadísticas Rápidas                                             │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐     │
│  │ Próximos        │ │ Total Gastado   │ │ Pedidos         │     │
│  │ Eventos         │ │                 │ │ Completados     │     │
│  │                 │ │                 │ │                 │     │
│  │      2          │ │  S/ 25,000      │ │       5         │     │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘     │
├───────────────────────────────────────────────────────────────────┤
│  Próximos Eventos                                    [Ver todos →]│
│  ┌───────────────────────────────────────────────────────────┐    │
│  │ 🎂 Boda - 25 Dic 2025                                     │    │
│  │ Estado: [CONFIRMADO] | Total: S/ 15,000                   │    │
│  │ Invitados: 150  •  Paquete: Boda Clásica                  │    │
│  │ [Ver Detalles] [Descargar Contrato]                       │    │
│  └───────────────────────────────────────────────────────────┘    │
│  ┌───────────────────────────────────────────────────────────┐    │
│  │ 👗 Quinceañera - 10 Feb 2026                              │    │
│  │ Estado: [PENDIENTE] | Total: S/ 10,000                    │    │
│  │ Invitados: 100  •  Paquete: Quinceañera Elegante          │    │
│  │ [Ver Detalles] [Completar Pago]                           │    │
│  └───────────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────────┘
```

#### **Wireframe 4: Wizard Pedido - Paso 1** 🎯
```
┌───────────────────────────────────────────────────────────────────┐
│ [☰] EventosPeru                             [👤 Juan Pérez ▾]     │
├───────────────────────────────────────────────────────────────────┤
│  Crear Nuevo Pedido                                               │
│  [●──────○──────○]  1. Tipo Evento  2. Servicios  3. Confirmar   │
├───────────────────────────────────────────────────────────────────┤
│  Tipo de Evento *                                                 │
│  ┌─────────────────────────────────────────────────────────┐      │
│  │ Selecciona un tipo de evento                           ▾│      │
│  └─────────────────────────────────────────────────────────┘      │
│                                                                   │
│  Selecciona un Paquete (Opcional)                                 │
│  ○ Sin paquete (servicios a la carta)                             │
│  ◉ Paquete Boda Clásica - S/ 12,000                               │
│    ✓ Decoración Floral  ✓ Catering  ✓ Fotografía                 │
│  ○ Paquete Boda Premium - S/ 18,000                               │
│    ✓ Todo lo del clásico  ✓ Video 4K  ✓ DJ                       │
│                                                                   │
│  Fecha del Evento *                                               │
│  [📅 25/12/2025]           (Mínimo 30 días de anticipación)       │
│                                                                   │
│  Número de Invitados *                                            │
│  [150]                     (Mín: 10, Máx: 1000)                   │
│                                                                   │
│                            [Cancelar]  [Siguiente →]              │
└───────────────────────────────────────────────────────────────────┘
```

#### **Wireframe 5: Wizard Pedido - Paso 2** ➕
```
┌───────────────────────────────────────────────────────────────────┐
│ [☰] EventosPeru                             [👤 Juan Pérez ▾]     │
├───────────────────────────────────────────────────────────────────┤
│  Crear Nuevo Pedido                                               │
│  [●──────●──────○]  1. Tipo Evento  2. Servicios  3. Confirmar   │
├───────────────────────────────────────────────────────────────────┤
│  Servicios Adicionales                                            │
│                                                                   │
│  📸 Fotografía & Video                                            │
│  ☑ Fotografía Premium - S/ 1,500                                  │
│     Fotógrafo profesional, 8 horas, 200+ fotos editadas           │
│  ☑ Video 4K - S/ 2,000                                            │
│     Videografía cinematográfica, highlights 5 min                 │
│                                                                   │
│  🎵 Entretenimiento                                               │
│  ☐ DJ Profesional - S/ 800                                        │
│     DJ + equipo de sonido + luces básicas                         │
│  ☐ Banda en Vivo - S/ 2,500                                       │
│     Banda de 5 integrantes, 3 horas                               │
│                                                                   │
│  🎨 Decoración Extra                                              │
│  ☐ Luces LED Ambientales - S/ 600                                 │
│  ☐ Alfombra Roja - S/ 300                                         │
│                                                                   │
│  Comentarios Especiales (Opcional)                                │
│  ┌─────────────────────────────────────────────────────────┐      │
│  │ Preferencia por colores pasteles, evitar flores rojas  │      │
│  │                                                         │      │
│  └─────────────────────────────────────────────────────────┘      │
│                                                                   │
│  ┌────────────────────────────────────────────┐                   │
│  │ Resumen de Precio                          │                   │
│  │ ────────────────────────────────────────   │                   │
│  │ Subtotal Paquete:        S/ 12,000.00      │                   │
│  │ Servicios Adicionales:   S/  3,500.00      │                   │
│  │ ────────────────────────────────────────   │                   │
│  │ TOTAL:                   S/ 15,500.00      │                   │
│  └────────────────────────────────────────────┘                   │
│                                                                   │
│                       [← Atrás]  [Siguiente →]                    │
└───────────────────────────────────────────────────────────────────┘
```

#### **Wireframe 6: Gestión Tipos Evento (Admin)** ⚙️
```
┌───────────────────────────────────────────────────────────────────┐
│ [☰] EventosPeru  [📊 Dashboard] [🎯 Tipos] [📦 Servicios] [👥 Usuarios] [👤 Admin ▾] │
├───────────────────────────────────────────────────────────────────┤
│  Gestión de Tipos de Evento                 [+ Nuevo Tipo Evento]│
├───────────────────────────────────────────────────────────────────┤
│  🔍 [Buscar tipos de evento...]              [🔄 Refresh]         │
├─────┬─────────────────────┬───────────────────────────┬───────────┤
│ ID  │ Nombre              │ Descripción               │ Acciones  │
├─────┼─────────────────────┼───────────────────────────┼───────────┤
│  1  │ Boda                │ Ceremonias matrimoniales  │ [✏️] [🗑️]│
├─────┼─────────────────────┼───────────────────────────┼───────────┤
│  2  │ Quinceañera         │ Celebración 15 años       │ [✏️] [🗑️]│
├─────┼─────────────────────┼───────────────────────────┼───────────┤
│  3  │ Cumpleaños          │ Fiestas de cumpleaños     │ [✏️] [🗑️]│
├─────┼─────────────────────┼───────────────────────────┼───────────┤
│  4  │ Conferencia Corp.   │ Eventos corporativos      │ [✏️] [🗑️]│
└─────┴─────────────────────┴───────────────────────────┴───────────┘
│  Mostrando 4 de 4 registros                   [1] [2] [3] [→]     │
└───────────────────────────────────────────────────────────────────┘

Modal Crear/Editar:
┌────────────────────────────────────┐
│ Nuevo Tipo de Evento           [✕] │
├────────────────────────────────────┤
│ Nombre *                           │
│ [___________________________]      │
│                                    │
│ Descripción *                      │
│ [___________________________]      │
│ [___________________________]      │
│ [___________________________]      │
│                                    │
│        [Cancelar]  [Guardar]       │
└────────────────────────────────────┘

Modal Eliminar:
┌────────────────────────────────────┐
│ Confirmar Eliminación          [✕] │
├────────────────────────────────────┤
│ ⚠️ ¿Estás seguro de eliminar el   │
│ tipo de evento "Boda"?             │
│                                    │
│ Esta acción no se puede deshacer.  │
│                                    │
│        [Cancelar]  [Eliminar]      │
└────────────────────────────────────┘
```

---

## 🎯 Arquitectura Frontend Propuesta

### **Opción Recomendada: SPA (Single Page Application)**

```
eventos-peru-frontend/
├── public/
│   ├── favicon.ico
│   └── assets/
│       └── images/
├── src/
│   ├── main.ts                    # Entry point
│   ├── App.vue                    # Root component
│   ├── router/
│   │   └── index.ts               # Vue Router config + guards
│   ├── stores/                    # Pinia stores (state management)
│   │   ├── auth.ts                # JWT, user, roles
│   │   ├── catalog.ts             # Tipos evento, servicios, paquetes
│   │   ├── providers.ts           # Proveedores
│   │   └── orders.ts              # Pedidos/contratación
│   ├── api/                       # Axios clients
│   │   ├── client.ts              # Axios instance + interceptors
│   │   ├── iam.ts                 # IAM endpoints
│   │   ├── catalog.ts             # Catálogo endpoints
│   │   ├── providers.ts           # Proveedores endpoints
│   │   └── contracts.ts           # Contratación endpoints
│   ├── composables/               # Vue 3 Composition API
│   │   ├── useAuth.ts             # Auth logic (login, logout, token)
│   │   ├── usePermissions.ts      # Role-based permissions
│   │   └── useNotifications.ts    # Toast/alerts
│   ├── components/                # Reusable components
│   │   ├── layout/
│   │   │   ├── Navbar.vue         # Navigation (role-based menu)
│   │   │   ├── Sidebar.vue        # Admin sidebar
│   │   │   └── Footer.vue
│   │   ├── common/
│   │   │   ├── Button.vue
│   │   │   ├── Input.vue
│   │   │   ├── Select.vue
│   │   │   ├── Modal.vue
│   │   │   ├── Card.vue
│   │   │   ├── Table.vue
│   │   │   ├── Pagination.vue
│   │   │   └── Loading.vue
│   │   └── forms/
│   │       ├── LoginForm.vue
│   │       ├── EventTypeForm.vue
│   │       ├── ServiceForm.vue
│   │       ├── PackageForm.vue
│   │       ├── ProviderForm.vue
│   │       └── OrderForm.vue
│   ├── views/                     # Page components
│   │   ├── public/
│   │   │   ├── Home.vue           # Landing page
│   │   │   ├── Login.vue
│   │   │   ├── Register.vue
│   │   │   ├── Catalog.vue        # Browse eventos/paquetes
│   │   │   ├── PackageDetails.vue
│   │   │   └── Providers.vue      # Browse proveedores
│   │   ├── client/
│   │   │   ├── Dashboard.vue      # Cliente dashboard
│   │   │   ├── MyOrders.vue       # Mis pedidos
│   │   │   ├── CreateOrder.vue    # Crear pedido
│   │   │   └── Profile.vue
│   │   └── admin/
│   │       ├── Dashboard.vue      # Admin dashboard
│   │       ├── EventTypes.vue     # CRUD tipos evento
│   │       ├── Services.vue       # CRUD servicios
│   │       ├── Options.vue        # CRUD opciones
│   │       ├── Packages.vue       # CRUD paquetes
│   │       ├── Providers.vue      # CRUD proveedores
│   │       ├── Orders.vue         # Gestión pedidos
│   │       └── Users.vue          # Gestión usuarios
│   ├── types/                     # TypeScript definitions
│   │   ├── auth.ts
│   │   ├── catalog.ts
│   │   ├── providers.ts
│   │   └── orders.ts
│   ├── utils/
│   │   ├── constants.ts
│   │   ├── formatters.ts
│   │   └── validators.ts
│   └── assets/
│       └── styles/
│           ├── main.css           # Tailwind imports
│           └── custom.css         # Custom styles
├── .env.development               # API URLs development
├── .env.production                # API URLs production
├── Dockerfile                     # Multi-stage build
├── nginx.conf                     # Nginx config
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

---

## 🔐 Gestión de Autenticación JWT

### **1. Axios Interceptor (src/api/client.ts)**

```typescript
import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import { useAuthStore } from '@/stores/auth';
import router from '@/router';

const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: Agregar token JWT
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const authStore = useAuthStore();
    const token = authStore.token;
    
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: Manejar 401 Unauthorized
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const authStore = useAuthStore();
      authStore.logout();
      router.push('/login');
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

### **2. Auth Store (src/stores/auth.ts)**

```typescript
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { loginUser, getProfile } from '@/api/iam';

interface User {
  id: number;
  email: string;
  nombre: string;
  role: 'CLIENTE' | 'ADMIN';
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('auth_token'));
  const user = ref<User | null>(null);

  const isAuthenticated = computed(() => !!token.value);
  const isAdmin = computed(() => user.value?.role === 'ADMIN');
  const isClient = computed(() => user.value?.role === 'CLIENTE');

  async function login(email: string, password: string) {
    const response = await loginUser(email, password);
    token.value = response.access_token;
    localStorage.setItem('auth_token', response.access_token);
    await fetchProfile();
  }

  async function fetchProfile() {
    const profile = await getProfile();
    user.value = profile;
  }

  function logout() {
    token.value = null;
    user.value = null;
    localStorage.removeItem('auth_token');
  }

  return {
    token,
    user,
    isAuthenticated,
    isAdmin,
    isClient,
    login,
    logout,
    fetchProfile,
  };
});
```

### **3. Router Guards (src/router/index.ts)**

```typescript
import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const routes: RouteRecordRaw[] = [
  // Rutas públicas
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/public/Home.vue'),
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/public/Login.vue'),
    meta: { guest: true },
  },
  {
    path: '/catalog',
    name: 'Catalog',
    component: () => import('@/views/public/Catalog.vue'),
  },
  
  // Rutas de cliente (requiere autenticación)
  {
    path: '/client',
    component: () => import('@/layouts/ClientLayout.vue'),
    meta: { requiresAuth: true, role: 'CLIENTE' },
    children: [
      {
        path: 'dashboard',
        name: 'ClientDashboard',
        component: () => import('@/views/client/Dashboard.vue'),
      },
      {
        path: 'orders',
        name: 'MyOrders',
        component: () => import('@/views/client/MyOrders.vue'),
      },
      {
        path: 'orders/create',
        name: 'CreateOrder',
        component: () => import('@/views/client/CreateOrder.vue'),
      },
    ],
  },
  
  // Rutas de admin (requiere rol ADMIN)
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAuth: true, role: 'ADMIN' },
    children: [
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: () => import('@/views/admin/Dashboard.vue'),
      },
      {
        path: 'event-types',
        name: 'EventTypes',
        component: () => import('@/views/admin/EventTypes.vue'),
      },
      {
        path: 'services',
        name: 'Services',
        component: () => import('@/views/admin/Services.vue'),
      },
      {
        path: 'packages',
        name: 'Packages',
        component: () => import('@/views/admin/Packages.vue'),
      },
      {
        path: 'providers',
        name: 'AdminProviders',
        component: () => import('@/views/admin/Providers.vue'),
      },
      {
        path: 'orders',
        name: 'AdminOrders',
        component: () => import('@/views/admin/Orders.vue'),
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/admin/Users.vue'),
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Navigation Guard
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();

  // Rutas que requieren autenticación
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return next('/login');
  }

  // Rutas solo para guests (login/register)
  if (to.meta.guest && authStore.isAuthenticated) {
    return next('/');
  }

  // Verificar rol
  if (to.meta.role && authStore.user?.role !== to.meta.role) {
    return next('/'); // Redirigir a home si no tiene el rol
  }

  next();
});

export default router;
```

---

## 🎨 Diseño UI/UX - Sistema de Diseño

### **Paleta de Colores (Tailwind Custom)**

```javascript
// tailwind.config.js
module.exports = {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // Colores primarios (Eventos Perú Brand)
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
        // Colores secundarios (Elegancia)
        secondary: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',  // Main
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
        },
        // Acento (Dorado/Oro para eventos premium)
        accent: {
          50: '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',  // Main
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Poppins', 'sans-serif'],
      },
      borderRadius: {
        'xl': '1rem',
        '2xl': '1.5rem',
        '3xl': '2rem',
      },
      boxShadow: {
        'soft': '0 2px 15px -3px rgba(0, 0, 0, 0.07), 0 10px 20px -2px rgba(0, 0, 0, 0.04)',
        'medium': '0 4px 25px -3px rgba(0, 0, 0, 0.1), 0 15px 30px -5px rgba(0, 0, 0, 0.08)',
        'strong': '0 10px 40px -5px rgba(0, 0, 0, 0.15), 0 20px 50px -10px rgba(0, 0, 0, 0.12)',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
};
```

### **Componentes Base Reutilizables**

#### **Button.vue**
```vue
<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :class="buttonClasses"
    @click="handleClick"
  >
    <svg v-if="loading" class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
    <slot />
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  type?: 'button' | 'submit' | 'reset';
  disabled?: boolean;
  loading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  type: 'button',
  disabled: false,
  loading: false,
});

const emit = defineEmits<{
  click: [event: MouseEvent];
}>();

const buttonClasses = computed(() => {
  const base = 'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2';
  
  const variants = {
    primary: 'bg-primary-500 hover:bg-primary-600 text-white focus:ring-primary-500 shadow-md hover:shadow-lg',
    secondary: 'bg-secondary-100 hover:bg-secondary-200 text-secondary-900 focus:ring-secondary-500',
    danger: 'bg-red-500 hover:bg-red-600 text-white focus:ring-red-500 shadow-md hover:shadow-lg',
    ghost: 'bg-transparent hover:bg-gray-100 text-gray-700 focus:ring-gray-500',
  };
  
  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };
  
  const disabledClass = props.disabled || props.loading ? 'opacity-50 cursor-not-allowed' : '';
  
  return `${base} ${variants[props.variant]} ${sizes[props.size]} ${disabledClass}`;
});

const handleClick = (event: MouseEvent) => {
  if (!props.disabled && !props.loading) {
    emit('click', event);
  }
};
</script>
```

#### **Card.vue**
```vue
<template>
  <div :class="cardClasses">
    <div v-if="$slots.header" class="px-6 py-4 border-b border-gray-200">
      <slot name="header" />
    </div>
    <div :class="bodyClasses">
      <slot />
    </div>
    <div v-if="$slots.footer" class="px-6 py-4 border-t border-gray-200 bg-gray-50">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  shadow?: 'none' | 'soft' | 'medium' | 'strong';
  padding?: boolean;
  hover?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  shadow: 'soft',
  padding: true,
  hover: false,
});

const cardClasses = computed(() => {
  const base = 'bg-white rounded-xl overflow-hidden transition-all duration-200';
  const shadows = {
    none: '',
    soft: 'shadow-soft',
    medium: 'shadow-medium',
    strong: 'shadow-strong',
  };
  const hoverClass = props.hover ? 'hover:shadow-medium hover:-translate-y-1' : '';
  
  return `${base} ${shadows[props.shadow]} ${hoverClass}`;
});

const bodyClasses = computed(() => {
  return props.padding ? 'px-6 py-4' : '';
});
</script>
```

---

## 📱 Navegación Role-Based (Navbar.vue)

```vue
<template>
  <nav class="bg-white shadow-soft sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <!-- Logo -->
        <div class="flex items-center">
          <router-link to="/" class="flex items-center space-x-2">
            <img src="/logo.svg" alt="Eventos Perú" class="h-8 w-8" />
            <span class="text-xl font-display font-bold text-primary-600">Eventos Perú</span>
          </router-link>
        </div>

        <!-- Navigation Links (Desktop) -->
        <div class="hidden md:flex items-center space-x-4">
          <!-- Public Links -->
          <router-link
            to="/catalog"
            class="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition"
          >
            Catálogo
          </router-link>
          <router-link
            to="/providers"
            class="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition"
          >
            Proveedores
          </router-link>

          <!-- Client Links -->
          <template v-if="authStore.isClient">
            <router-link
              to="/client/dashboard"
              class="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition"
            >
              Mi Panel
            </router-link>
            <router-link
              to="/client/orders"
              class="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition"
            >
              Mis Pedidos
            </router-link>
          </template>

          <!-- Admin Links -->
          <template v-if="authStore.isAdmin">
            <router-link
              to="/admin/dashboard"
              class="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition"
            >
              Admin
            </router-link>
          </template>

          <!-- Auth Buttons -->
          <template v-if="!authStore.isAuthenticated">
            <router-link to="/login">
              <Button variant="ghost" size="sm">Iniciar Sesión</Button>
            </router-link>
            <router-link to="/register">
              <Button variant="primary" size="sm">Registrarse</Button>
            </router-link>
          </template>
          
          <!-- User Menu (Authenticated) -->
          <div v-else class="relative">
            <button
              @click="toggleUserMenu"
              class="flex items-center space-x-2 text-gray-700 hover:text-primary-600"
            >
              <div class="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center">
                <span class="text-primary-600 font-medium text-sm">
                  {{ authStore.user?.nombre.charAt(0).toUpperCase() }}
                </span>
              </div>
              <ChevronDownIcon class="h-4 w-4" />
            </button>
            
            <!-- Dropdown Menu -->
            <div
              v-if="showUserMenu"
              class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-medium py-1"
            >
              <router-link
                to="/profile"
                class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              >
                Mi Perfil
              </router-link>
              <button
                @click="handleLogout"
                class="w-full text-left block px-4 py-2 text-sm text-red-600 hover:bg-red-50"
              >
                Cerrar Sesión
              </button>
            </div>
          </div>
        </div>

        <!-- Mobile Menu Button -->
        <div class="md:hidden flex items-center">
          <button @click="toggleMobileMenu" class="text-gray-700">
            <MenuIcon class="h-6 w-6" />
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile Menu -->
    <div v-if="showMobileMenu" class="md:hidden border-t border-gray-200">
      <div class="px-2 pt-2 pb-3 space-y-1">
        <!-- Mobile links here -->
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';
import Button from '@/components/common/Button.vue';

const authStore = useAuthStore();
const router = useRouter();
const showUserMenu = ref(false);
const showMobileMenu = ref(false);

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value;
};

const toggleMobileMenu = () => {
  showMobileMenu.value = !showMobileMenu.value;
};

const handleLogout = () => {
  authStore.logout();
  router.push('/');
};
</script>
```

---

## 📝 Formularios CRUD

### **Ejemplo: EventTypeForm.vue (Admin)**

```vue
<template>
  <form @submit.prevent="handleSubmit" class="space-y-6">
    <div>
      <label for="nombre" class="block text-sm font-medium text-gray-700">Nombre del Tipo de Evento</label>
      <input
        id="nombre"
        v-model="form.nombre"
        type="text"
        required
        class="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
      />
      <p v-if="errors.nombre" class="mt-1 text-sm text-red-600">{{ errors.nombre }}</p>
    </div>

    <div>
      <label for="descripcion" class="block text-sm font-medium text-gray-700">Descripción</label>
      <textarea
        id="descripcion"
        v-model="form.descripcion"
        rows="3"
        class="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
      ></textarea>
    </div>

    <div class="flex items-center">
      <input
        id="activo"
        v-model="form.activo"
        type="checkbox"
        class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
      />
      <label for="activo" class="ml-2 block text-sm text-gray-900">Activo</label>
    </div>

    <div class="flex justify-end space-x-3">
      <Button variant="ghost" type="button" @click="emit('cancel')">
        Cancelar
      </Button>
      <Button variant="primary" type="submit" :loading="loading">
        {{ isEdit ? 'Actualizar' : 'Crear' }}
      </Button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue';
import Button from '@/components/common/Button.vue';
import { createEventType, updateEventType } from '@/api/catalog';

interface Props {
  eventType?: {
    tipo_evento_id: number;
    nombre: string;
    descripcion?: string;
    activo: boolean;
  };
}

const props = defineProps<Props>();
const emit = defineEmits<{
  success: [];
  cancel: [];
}>();

const isEdit = ref(!!props.eventType);
const loading = ref(false);
const errors = reactive<Record<string, string>>({});

const form = reactive({
  nombre: props.eventType?.nombre || '',
  descripcion: props.eventType?.descripcion || '',
  activo: props.eventType?.activo ?? true,
});

const handleSubmit = async () => {
  loading.value = true;
  errors.nombre = '';

  try {
    if (isEdit.value && props.eventType) {
      await updateEventType(props.eventType.tipo_evento_id, form);
    } else {
      await createEventType(form);
    }
    emit('success');
  } catch (error: any) {
    if (error.response?.data?.detail) {
      errors.nombre = error.response.data.detail;
    }
  } finally {
    loading.value = false;
  }
};
</script>
```

### **Vista Admin con Tabla CRUD (EventTypes.vue)**

```vue
<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <h1 class="text-3xl font-display font-bold text-gray-900">Tipos de Evento</h1>
      <Button variant="primary" @click="openCreateModal">
        + Nuevo Tipo
      </Button>
    </div>

    <!-- Search & Filters -->
    <Card>
      <div class="flex items-center space-x-4">
        <input
          v-model="searchQuery"
          type="search"
          placeholder="Buscar tipos de evento..."
          class="flex-1 rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
        />
        <Button variant="secondary" @click="loadEventTypes">
          Buscar
        </Button>
      </div>
    </Card>

    <!-- Table -->
    <Card :padding="false">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Nombre
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Descripción
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Estado
              </th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="eventType in eventTypes" :key="eventType.tipo_evento_id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {{ eventType.nombre }}
              </td>
              <td class="px-6 py-4 text-sm text-gray-500">
                {{ eventType.descripcion || '-' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="eventType.activo ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                  class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                >
                  {{ eventType.activo ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                <button
                  @click="openEditModal(eventType)"
                  class="text-primary-600 hover:text-primary-900"
                >
                  Editar
                </button>
                <button
                  @click="confirmDelete(eventType)"
                  class="text-red-600 hover:text-red-900"
                >
                  Eliminar
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </Card>

    <!-- Modal CRUD -->
    <Modal v-model="showModal" :title="isEdit ? 'Editar Tipo de Evento' : 'Nuevo Tipo de Evento'">
      <EventTypeForm
        :event-type="selectedEventType"
        @success="handleSuccess"
        @cancel="showModal = false"
      />
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { getEventTypes, deleteEventType } from '@/api/catalog';
import Card from '@/components/common/Card.vue';
import Button from '@/components/common/Button.vue';
import Modal from '@/components/common/Modal.vue';
import EventTypeForm from '@/components/forms/EventTypeForm.vue';

const eventTypes = ref([]);
const searchQuery = ref('');
const showModal = ref(false);
const isEdit = ref(false);
const selectedEventType = ref(null);

const loadEventTypes = async () => {
  const data = await getEventTypes();
  eventTypes.value = data;
};

const openCreateModal = () => {
  isEdit.value = false;
  selectedEventType.value = null;
  showModal.value = true;
};

const openEditModal = (eventType: any) => {
  isEdit.value = true;
  selectedEventType.value = eventType;
  showModal.value = true;
};

const confirmDelete = async (eventType: any) => {
  if (confirm(`¿Eliminar "${eventType.nombre}"?`)) {
    await deleteEventType(eventType.tipo_evento_id);
    await loadEventTypes();
  }
};

const handleSuccess = async () => {
  showModal.value = false;
  await loadEventTypes();
};

onMounted(() => {
  loadEventTypes();
});
</script>
```

---

## 🐳 Deployment con Docker + Kubernetes

### **1. Dockerfile (Multi-stage build)**

```dockerfile
# Stage 1: Build
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy source code
COPY . .

# Build for production
RUN npm run build

# Stage 2: Production
FROM nginx:1.25-alpine

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Non-root user
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx && \
    touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/run/nginx.pid

USER nginx

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### **2. nginx.conf**

```nginx
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
    gzip_min_length 1000;

    # SPA routing (fallback to index.html)
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Health check
    location /health {
        access_log off;
        return 200 "OK\n";
        add_header Content-Type text/plain;
    }
}
```

### **3. Kubernetes Deployment**

```yaml
# k8s/frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: eventos-peru
  labels:
    app: frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: emeday17/eventos-peru-frontend:1.0.0
        ports:
        - containerPort: 80
          name: http
        env:
        - name: VITE_API_BASE_URL
          value: "http://api-gateway.eventos-peru.svc.cluster.local"
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /health
            port: 80
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: frontend
  namespace: eventos-peru
spec:
  type: ClusterIP
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 80
    name: http
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: frontend-ingress
  namespace: eventos-peru
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: eventos.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 80
```

### **4. ConfigMap para Variables de Entorno**

```yaml
# k8s/frontend-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: frontend-config
  namespace: eventos-peru
data:
  VITE_API_BASE_URL: "http://api.eventos-peru.svc.cluster.local"
  VITE_IAM_URL: "http://api.eventos-peru.svc.cluster.local/api/iam"
  VITE_CATALOGO_URL: "http://api.eventos-peru.svc.cluster.local/api/catalogo"
  VITE_PROVEEDORES_URL: "http://api.eventos-peru.svc.cluster.local/api/proveedores"
  VITE_CONTRATACION_URL: "http://api.eventos-peru.svc.cluster.local/api/contratacion"
```

---

## 🚀 Scripts de Build & Deploy

### **package.json**

```json
{
  "name": "eventos-peru-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext .vue,.js,.jsx,.cjs,.mjs,.ts,.tsx,.cts,.mts --fix --ignore-path .gitignore",
    "format": "prettier --write src/",
    "docker:build": "docker build -t emeday17/eventos-peru-frontend:latest .",
    "docker:push": "docker push emeday17/eventos-peru-frontend:latest",
    "k8s:deploy": "kubectl apply -f k8s/",
    "k8s:delete": "kubectl delete -f k8s/"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.5",
    "pinia": "^2.1.7",
    "axios": "^1.6.2"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "typescript": "^5.3.3",
    "vue-tsc": "^1.8.27",
    "vite": "^5.0.8",
    "tailwindcss": "^3.4.0",
    "@tailwindcss/forms": "^0.5.7",
    "@tailwindcss/typography": "^0.5.10",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "eslint": "^8.55.0",
    "prettier": "^3.1.1"
  }
}
```

### **Script de Deploy Completo**

```powershell
# deploy-frontend.ps1
param(
    [string]$TAG = "latest"
)

Write-Host "🚀 Deploying Frontend to Kubernetes" -ForegroundColor Cyan

# 1. Build
Write-Host "`n📦 Building application..." -ForegroundColor Yellow
npm run build

# 2. Docker Build
Write-Host "`n🐳 Building Docker image..." -ForegroundColor Yellow
docker build -t "emeday17/eventos-peru-frontend:$TAG" .

# 3. Docker Push
Write-Host "`n📤 Pushing to Docker Hub..." -ForegroundColor Yellow
docker push "emeday17/eventos-peru-frontend:$TAG"

# 4. Update Kubernetes
Write-Host "`n☸️  Deploying to Kubernetes..." -ForegroundColor Yellow
kubectl apply -f k8s/

# 5. Wait for rollout
Write-Host "`n⏳ Waiting for deployment..." -ForegroundColor Yellow
kubectl rollout status deployment/frontend -n eventos-peru

# 6. Get Ingress URL
Write-Host "`n✅ Deployment complete!" -ForegroundColor Green
kubectl get ingress -n eventos-peru
```

---

## 📊 Estructura de API Calls

### **src/api/catalog.ts**

```typescript
import apiClient from './client';

// Event Types
export const getEventTypes = async () => {
  const response = await apiClient.get('/api/catalogo/tipos-evento');
  return response.data;
};

export const createEventType = async (data: any) => {
  const response = await apiClient.post('/api/catalogo/admin/tipos-evento', data);
  return response.data;
};

export const updateEventType = async (id: number, data: any) => {
  const response = await apiClient.put(`/api/catalogo/admin/tipos-evento/${id}`, data);
  return response.data;
};

export const deleteEventType = async (id: number) => {
  await apiClient.delete(`/api/catalogo/admin/tipos-evento/${id}`);
};

// Services
export const getServicesByEventType = async (tipoEventoId: number) => {
  const response = await apiClient.get(`/api/catalogo/servicios/${tipoEventoId}`);
  return response.data;
};

// Packages
export const getPackages = async (tipoEventoId?: number) => {
  const url = tipoEventoId 
    ? `/api/catalogo/paquetes/${tipoEventoId}` 
    : '/api/catalogo/paquetes';
  const response = await apiClient.get(url);
  return response.data;
};

export const getPackageDetails = async (paqueteId: number) => {
  const response = await apiClient.get(`/api/catalogo/paquetes/${paqueteId}/detalle`);
  return response.data;
};

// ... más endpoints
```

---

## 🎯 Flujos Principales

### **1. Flujo Cliente - Crear Pedido**

```
1. Cliente navega a /catalog
2. Selecciona tipo de evento (Boda, Cumpleaños, etc.)
3. Ve paquetes predefinidos o arma uno personalizado
4. Si arma personalizado:
   a. Selecciona servicios disponibles
   b. Para cada servicio, elige opciones (con precio)
   c. Ve proveedores disponibles para cada opción
5. Agrega al carrito / Crea pedido (draft)
6. Confirma pedido → Estado DRAFT
7. Admin asigna proveedor → Estado EN_PROGRESO
8. Cliente ve el pedido en "Mis Pedidos"
```

### **2. Flujo Admin - Gestión**

```
1. Admin accede a /admin/dashboard
2. Navegación lateral con opciones:
   - Tipos de Evento (CRUD)
   - Servicios (CRUD)
   - Opciones de Servicio (CRUD)
   - Paquetes (CRUD)
   - Proveedores (CRUD + Habilidades)
   - Pedidos (Ver todos, asignar proveedores)
   - Usuarios (CRUD, cambiar roles)
3. Cada sección tiene tabla con search/filters
4. Modals para crear/editar
5. Confirmación para eliminar
```

---

## 📈 Performance & Optimización

### **1. Code Splitting**

```typescript
// router/index.ts
const routes = [
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'), // Lazy load
    children: [
      {
        path: 'event-types',
        component: () => import('@/views/admin/EventTypes.vue'), // Lazy load
      },
    ],
  },
];
```

### **2. Caching de Catálogo**

```typescript
// stores/catalog.ts
export const useCatalogStore = defineStore('catalog', () => {
  const eventTypes = ref([]);
  const lastFetch = ref<number | null>(null);
  const CACHE_TTL = 5 * 60 * 1000; // 5 minutos

  async function fetchEventTypes(forceRefresh = false) {
    const now = Date.now();
    if (!forceRefresh && lastFetch.value && (now - lastFetch.value) < CACHE_TTL) {
      return eventTypes.value; // Return cached
    }

    const data = await getEventTypes();
    eventTypes.value = data;
    lastFetch.value = now;
    return data;
  }

  return { eventTypes, fetchEventTypes };
});
```

### **3. Image Optimization**

```html
<!-- Usar lazy loading para imágenes -->
<img 
  :src="imageSrc" 
  loading="lazy" 
  class="w-full h-64 object-cover rounded-lg"
  alt="Evento"
/>
```

---

## 📋 Checklist de Implementación

### **Fase 1: Setup Inicial (Semana 1)**
- [ ] Crear proyecto con Vite + Vue 3 + TypeScript
- [ ] Configurar Tailwind CSS + custom theme
- [ ] Configurar Vue Router con guards
- [ ] Configurar Pinia stores
- [ ] Crear Axios client con interceptors
- [ ] Implementar componentes base (Button, Card, Input, Modal, Table)
- [ ] Implementar layouts (Public, Client, Admin)

### **Fase 2: Autenticación (Semana 2)**
- [ ] Página de Login
- [ ] Página de Registro
- [ ] Auth store con JWT
- [ ] Navigation guards role-based
- [ ] Navbar con menú dinámico
- [ ] User profile page

### **Fase 3: Vistas Públicas (Semana 3)**
- [ ] Landing page (Home)
- [ ] Catálogo de eventos
- [ ] Detalle de paquetes
- [ ] Lista de proveedores
- [ ] Responsive design para mobile

### **Fase 4: Panel Cliente (Semana 4)**
- [ ] Dashboard del cliente
- [ ] Crear pedido (wizard multi-step)
- [ ] Mis pedidos (lista + detalle)
- [ ] Perfil del usuario

### **Fase 5: Panel Admin (Semana 5-6)**
- [ ] Dashboard admin con stats
- [ ] CRUD Tipos de Evento
- [ ] CRUD Servicios
- [ ] CRUD Opciones de Servicio
- [ ] CRUD Paquetes
- [ ] CRUD Proveedores (+ Habilidades)
- [ ] Gestión de Pedidos (asignar proveedores)
- [ ] Gestión de Usuarios

### **Fase 6: Docker + Kubernetes (Semana 7)**
- [ ] Dockerfile multi-stage
- [ ] nginx.conf optimizado
- [ ] Kubernetes deployment YAML
- [ ] ConfigMap para env vars
- [ ] Ingress para routing
- [ ] Scripts de deploy automatizados
- [ ] CI/CD con GitHub Actions

### **Fase 7: Testing & Polish (Semana 8)**
- [ ] Unit tests (Vitest)
- [ ] E2E tests (Cypress/Playwright)
- [ ] Performance optimization
- [ ] Accessibility (a11y)
- [ ] SEO meta tags
- [ ] Error boundaries
- [ ] Loading states
- [ ] Toast notifications

---

## 🎨 Mockups de Diseño

### **Home Page**
```
╔═══════════════════════════════════════════════════════════╗
║  [Logo] Eventos Perú     Catálogo | Proveedores | Login  ║
╠═══════════════════════════════════════════════════════════╣
║                                                            ║
║       🎉 Organiza tu Evento Perfecto en Perú 🎉          ║
║     Bodas • Cumpleaños • Corporativos • Y más...         ║
║                                                            ║
║         [Ver Catálogo]  [Contactar]                      ║
║                                                            ║
║  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      ║
║  │   💒 Bodas  │  │🎂 Cumpleaños│  │🏢 Corporativo│     ║
║  │  50 paquetes│  │  30 paquetes│  │  20 paquetes │     ║
║  └─────────────┘  └─────────────┘  └─────────────┘      ║
║                                                            ║
║  Proveedores Verificados • Paquetes Personalizables      ║
╚═══════════════════════════════════════════════════════════╝
```

### **Admin Dashboard**
```
╔═════════════════════╦═══════════════════════════════════════╗
║  EVENTOS PERÚ       ║  [Usuario Admin ▼]                   ║
╠═════════════════════╬═══════════════════════════════════════╣
║ 📊 Dashboard        ║  Estadísticas Generales              ║
║ 🎯 Tipos Evento     ║  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐   ║
║ 🛠️  Servicios        ║  │ 152 │ │  50 │ │  30 │ │  15 │   ║
║ 📦 Paquetes         ║  │Users│ │Provd│ │Pedid│ │Paqt │   ║
║ 👥 Proveedores      ║  └─────┘ └─────┘ └─────┘ └─────┘   ║
║ 📝 Pedidos          ║                                       ║
║ 👤 Usuarios         ║  Pedidos Recientes                   ║
║                     ║  ┌─────────────────────────────────┐ ║
║                     ║  │ #001 | Boda | DRAFT | Jorge M. │ ║
║                     ║  │ #002 | Cumple | EN_PROGRESO    │ ║
║                     ║  └─────────────────────────────────┘ ║
╚═════════════════════╩═══════════════════════════════════════╝
```

---

## 💡 Recomendaciones Finales

### **1. Por qué Vue.js 3 + Vite es la mejor opción**

✅ **Performance**: Vite ofrece HMR instantáneo y builds optimizados  
✅ **Developer Experience**: Vue 3 Composition API es intuitivo y poderoso  
✅ **Ecosystem**: Vue Router + Pinia están maduros y bien mantenidos  
✅ **TypeScript**: Excelente integración out-of-the-box  
✅ **Bundle Size**: Vue 3 es ligero (~33KB gzipped)  
✅ **Deployment**: Nginx estático es simple, rápido y escalable  
✅ **Kubernetes**: Mismo patrón que backend (Docker + K8s)

### **2. Alternativas Consideradas**

| Framework | Pros | Contras | Veredicto |
|-----------|------|---------|-----------|
| **React** | Ecosistema grande, jobs | Más complejo, más boilerplate | ❌ Overkill |
| **Angular** | Enterprise-ready | Muy pesado, curva empinada | ❌ Too heavy |
| **Svelte** | Muy rápido, simple | Ecosistema pequeño | ⚠️ Riesgoso |
| **Vue 3** | Balance perfecto | - | ✅ **RECOMENDADO** |

### **3. Timeline Estimado**

- **Setup + Auth**: 2 semanas
- **Vistas Públicas**: 1 semana
- **Panel Cliente**: 1 semana
- **Panel Admin**: 2 semanas
- **Docker + K8s**: 1 semana
- **Testing + Polish**: 1 semana

**Total: ~8 semanas** (2 meses con 1 desarrollador full-time)

---

## 🚀 Comandos de Inicio Rápido

```bash
# 1. Crear proyecto
npm create vite@latest eventos-peru-frontend -- --template vue-ts
cd eventos-peru-frontend

# 2. Instalar dependencias
npm install vue-router@4 pinia axios
npm install -D tailwindcss@latest postcss autoprefixer
npm install -D @tailwindcss/forms @tailwindcss/typography

# 3. Inicializar Tailwind
npx tailwindcss init -p

# 4. Configurar estructura
mkdir -p src/{api,components/{common,forms,layout},composables,router,stores,types,utils,views/{public,client,admin}}

# 5. Desarrollar
npm run dev

# 6. Build para producción
npm run build

# 7. Build Docker
docker build -t emeday17/eventos-peru-frontend:1.0.0 .

# 8. Deploy a Kubernetes
kubectl apply -f k8s/
```

---

## 📚 Recursos Adicionales

- [Vue 3 Docs](https://vuejs.org/)
- [Vite Guide](https://vitejs.dev/guide/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Vue Router](https://router.vuejs.org/)
- [Pinia](https://pinia.vuejs.org/)
- [TypeScript](https://www.typescriptlang.org/docs/)

---

**¿Listo para implementar? Este plan cubre todos los aspectos necesarios para un frontend profesional, escalable y mantenible.** 🎯

**Próximo paso sugerido**: Crear el proyecto base con Vite y configurar la estructura de carpetas. 🚀
