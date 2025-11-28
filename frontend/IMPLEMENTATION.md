# 📚 Frontend Implementation Documentation - Eventos Perú

## 🎯 Overview

This document provides comprehensive documentation for the Vue 3 + TypeScript + Tailwind CSS frontend implementation for the Eventos Perú platform.

**Project Status**: 75% Complete  
**Last Updated**: November 27, 2025  
**Tech Stack**: Vue 3.4, Vite 5.0, TypeScript 5.3, Tailwind CSS 3.4, Pinia 2.1, Vue Router 4.2

---

## 📋 Table of Contents

1. [Project Structure](#project-structure)
2. [Installation & Setup](#installation--setup)
3. [Architecture](#architecture)
4. [Component Library](#component-library)
5. [State Management](#state-management)
6. [Routing & Navigation](#routing--navigation)
7. [API Integration](#api-integration)
8. [Views Implementation](#views-implementation)
9. [Authentication Flow](#authentication-flow)
10. [Deployment](#deployment)
11. [Testing](#testing)
12. [Progress Tracking](#progress-tracking)

---

## 📁 Project Structure

```
frontend/
├── public/                     # Static assets
├── src/
│   ├── api/                    # API layer
│   │   ├── client.ts          # Axios instance with interceptors
│   │   ├── iam.ts             # IAM service endpoints
│   │   ├── catalog.ts         # Catalog service endpoints
│   │   ├── providers.ts       # Providers service endpoints
│   │   ├── orders.ts          # Orders service endpoints
│   │   └── index.ts           # Barrel exports
│   │
│   ├── components/
│   │   ├── common/            # Reusable UI components
│   │   │   ├── Button.vue     # ✅ 5 variants, 3 sizes
│   │   │   ├── Card.vue       # ✅ Flexible container
│   │   │   ├── Input.vue      # ✅ Multiple input types
│   │   │   ├── Modal.vue      # ✅ @headlessui Dialog
│   │   │   ├── Table.vue      # ✅ Dynamic columns
│   │   │   ├── Pagination.vue # ✅ Page navigation
│   │   │   ├── SearchBar.vue  # ✅ Debounced search
│   │   │   └── Loading.vue    # ✅ Spinner component
│   │   │
│   │   └── layout/            # Layout components
│   │       ├── PublicLayout.vue    # ✅ Public wrapper
│   │       ├── ClientLayout.vue    # ✅ Client wrapper
│   │       ├── AdminLayout.vue     # ✅ Admin wrapper
│   │       ├── PublicNavbar.vue    # ✅ Public navigation
│   │       ├── ClientNavbar.vue    # ✅ Client navigation
│   │       ├── AdminNavbar.vue     # ✅ Admin navigation
│   │       └── Footer.vue          # ✅ Footer
│   │
│   ├── stores/                # Pinia stores
│   │   ├── auth.ts           # ✅ Authentication & user state
│   │   ├── catalog.ts        # ✅ Tipos, servicios, paquetes
│   │   ├── orders.ts         # ✅ Pedidos management
│   │   └── index.ts          # Barrel exports
│   │
│   ├── types/                # TypeScript definitions
│   │   ├── auth.ts           # ✅ User, Login, Register types
│   │   ├── catalog.ts        # ✅ TipoEvento, Servicio, Paquete
│   │   ├── providers.ts      # ✅ Proveedor types
│   │   ├── orders.ts         # ✅ Pedido types
│   │   └── index.ts          # ✅ Common types & exports
│   │
│   ├── views/
│   │   ├── public/
│   │   │   ├── Home.vue           # ✅ Landing page
│   │   │   ├── Login.vue          # ✅ Authentication
│   │   │   ├── Paquetes.vue       # 🟡 Skeleton
│   │   │   ├── PaqueteDetalle.vue # 🟡 Skeleton
│   │   │   ├── Proveedores.vue    # 🟡 Skeleton
│   │   │   └── NotFound.vue       # ✅ 404 page
│   │   │
│   │   ├── client/
│   │   │   ├── Dashboard.vue       # ✅ Client dashboard
│   │   │   ├── Paquetes.vue        # 🟡 Skeleton
│   │   │   ├── MisPedidos.vue      # ✅ Orders list (NEW)
│   │   │   ├── CreateOrderWizard.vue # ✅ 3-step wizard (NEW)
│   │   │   └── Profile.vue         # 🟡 Skeleton
│   │   │
│   │   └── admin/
│   │       ├── Dashboard.vue       # ✅ Admin stats
│   │       ├── TiposEvento.vue     # ✅ Full CRUD
│   │       ├── Servicios.vue       # ✅ Full CRUD (NEW)
│   │       ├── Paquetes.vue        # ✅ Full CRUD (NEW)
│   │       ├── Pedidos.vue         # 🟡 Skeleton
│   │       └── Usuarios.vue        # 🟡 Skeleton
│   │
│   ├── router/
│   │   └── index.ts          # ✅ Routes + guards
│   │
│   ├── App.vue               # ✅ Root component
│   ├── main.ts               # ✅ Entry point
│   └── style.css             # ✅ Tailwind + custom
│
├── .env                      # ✅ Environment variables
├── Dockerfile                # ✅ Multi-stage build
├── nginx.conf                # ✅ SPA routing
├── package.json              # ✅ Dependencies
├── tsconfig.json             # ✅ TypeScript config
├── vite.config.ts            # ✅ Vite config
└── tailwind.config.js        # ✅ Tailwind theme

Legend:
✅ Fully implemented
🟡 Skeleton/Partial
❌ Not started
```

---

## 🚀 Installation & Setup

### Prerequisites

- Node.js >= 18.0.0
- npm >= 9.0.0
- Backend services running (IAM, Catalog, Providers, Orders)

### Quick Start

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Configure environment
cp .env.example .env
# Edit .env with your API base URL

# 4. Start development server
npm run dev

# 5. Build for production
npm run build

# 6. Preview production build
npm run preview
```

### Environment Variables

```env
# .env
VITE_API_BASE_URL=/api
```

**Note**: In development, Vite proxy redirects `/api/*` to `http://localhost:8080`

---

## 🏗️ Architecture

### Design Principles

1. **Separation of Concerns**: Clear layering (API → Store → Component → View)
2. **Type Safety**: Full TypeScript coverage
3. **Reusability**: Component library approach
4. **Performance**: Code splitting, lazy loading, caching
5. **Maintainability**: Consistent patterns, clean code

### Data Flow

```
Backend API
    ↓
API Layer (client.ts + service modules)
    ↓
Pinia Stores (state management + caching)
    ↓
Vue Components (UI + logic)
    ↓
User Interface
```

### Authentication Flow

```
1. User enters credentials → Login.vue
2. Form submits → authStore.login()
3. authStore calls → iamApi.login()
4. Receives JWT token
5. Stores in localStorage + Pinia state
6. Axios interceptor adds token to all requests
7. Router guard checks auth on navigation
8. On 401 response → auto logout → redirect to /login
```

---

## 🎨 Component Library

### Button Component

**File**: `src/components/common/Button.vue`

**Props**:
- `variant`: 'primary' | 'secondary' | 'outline' | 'danger' | 'ghost'
- `size`: 'sm' | 'md' | 'lg'
- `loading`: boolean
- `disabled`: boolean
- `fullWidth`: boolean

**Usage**:
```vue
<Button variant="primary" size="lg" :loading="submitting">
  Save Changes
</Button>
```

### Card Component

**File**: `src/components/common/Card.vue`

**Props**:
- `shadow`: 'none' | 'soft' | 'medium' | 'strong'
- `padding`: boolean
- `hover`: boolean

**Slots**:
- `header`: Optional header section
- `default`: Main content
- `footer`: Optional footer section

**Usage**:
```vue
<Card shadow="medium">
  <template #header>
    <h2>Card Title</h2>
  </template>
  <p>Card content goes here</p>
</Card>
```

### Modal Component

**File**: `src/components/common/Modal.vue`

**Props**:
- `v-model`: boolean (open/close state)
- `title`: string
- `maxWidth`: 'sm' | 'md' | 'lg' | 'xl' | '2xl'

**Usage**:
```vue
<Modal v-model="showModal" title="Edit Item" max-width="lg">
  <form>...</form>
</Modal>
```

### Table Component

**File**: `src/components/common/Table.vue`

**Props**:
- `columns`: TableColumn[] (key, label, sortable)
- `data`: any[]
- `loading`: boolean
- `emptyText`: string

**Slots**:
- `cell(columnKey)`: Custom cell rendering
- `actions`: Row action buttons

**Usage**:
```vue
<Table :columns="columns" :data="items" :loading="loading">
  <template #actions="{ item }">
    <Button @click="edit(item)">Edit</Button>
  </template>
</Table>
```

### SearchBar Component

**File**: `src/components/common/SearchBar.vue`

**Props**:
- `modelValue`: string
- `placeholder`: string
- `debounce`: number (default: 300ms)

**Usage**:
```vue
<SearchBar v-model="searchQuery" placeholder="Search..." />
```

---

## 📦 State Management

### Auth Store

**File**: `src/stores/auth.ts`

**State**:
```typescript
{
  user: User | null
  token: string | null
}
```

**Getters**:
- `isAuthenticated`: boolean
- `isAdmin`: boolean
- `isCliente`: boolean
- `userFullName`: string

**Actions**:
- `login(email, password)`: Authenticate user
- `logout()`: Clear session
- `register(data)`: Create new user
- `fetchProfile()`: Get user data
- `updateProfile(data)`: Update user data
- `initializeAuth()`: Load token from localStorage

**Usage**:
```typescript
const authStore = useAuthStore();

// Login
await authStore.login('user@example.com', 'password');

// Check auth
if (authStore.isAuthenticated) {
  console.log('User:', authStore.user);
}

// Logout
authStore.logout();
```

### Catalog Store

**File**: `src/stores/catalog.ts`

**State**:
```typescript
{
  tiposEvento: TipoEvento[]
  servicios: Servicio[]
  paquetes: Paquete[]
  loading: boolean
  error: string | null
  // Cache timestamps
  lastFetchTipos: number | null
  lastFetchServicios: number | null
  lastFetchPaquetes: number | null
}
```

**Caching**: 5-minute TTL for each entity type

**Actions**:
- `fetchTiposEvento(forceRefresh?)`: Load tipos
- `fetchServicios(forceRefresh?)`: Load servicios
- `fetchPaquetes(forceRefresh?)`: Load paquetes
- `createTipoEvento(data)`: Create tipo
- `updateTipoEvento(id, data)`: Update tipo
- `deleteTipoEvento(id)`: Delete tipo
- Similar CRUD for servicios and paquetes

**Usage**:
```typescript
const catalogStore = useCatalogStore();

// Load data (cached)
await catalogStore.fetchTiposEvento();

// Force refresh
await catalogStore.fetchTiposEvento(true);

// Create new
await catalogStore.createServicio({
  nombre: 'Fotografía',
  precio_unitario: 1500
});
```

### Orders Store

**File**: `src/stores/orders.ts`

**State**:
```typescript
{
  pedidos: Pedido[]
  currentPedido: Pedido | null
  draftOrder: DraftOrder  // For wizard
  loading: boolean
  error: string | null
}
```

**Draft Order Structure**:
```typescript
{
  tipo_evento_id: number | null
  paquete_id: number | null
  fecha_evento: string | null
  num_invitados: number | null
  servicios_adicionales: number[]
  comentarios: string | null
}
```

**Actions**:
- `fetchPedidos(userId?)`: Load orders
- `fetchPedidoById(id)`: Get single order
- `createPedido(data)`: Create new order
- `updatePedido(id, data)`: Update order
- `updateDraft(data)`: Update wizard draft
- `clearDraft()`: Reset wizard
- `getDraft()`: Get current draft

**Usage**:
```typescript
const ordersStore = useOrdersStore();

// Wizard workflow
ordersStore.updateDraft({ tipo_evento_id: 1 });
ordersStore.updateDraft({ fecha_evento: '2025-12-25' });
const draft = ordersStore.getDraft();
await ordersStore.createPedido(draft);
ordersStore.clearDraft();
```

---

## 🛣️ Routing & Navigation

### Route Structure

```typescript
// Public routes
/ - Home
/login - Login
/paquetes - Browse packages
/paquetes/:id - Package details
/proveedores - Browse providers

// Client routes (requires auth + CLIENTE role)
/cliente/dashboard - Client dashboard
/cliente/paquetes - Client package browser
/cliente/pedidos - My orders
/cliente/pedido/nuevo - Create order wizard
/perfil - User profile

// Admin routes (requires auth + ADMIN role)
/admin/dashboard - Admin dashboard
/admin/tipos-evento - Manage event types
/admin/servicios - Manage services
/admin/paquetes - Manage packages
/admin/pedidos - Manage all orders
/admin/usuarios - Manage users

// Fallback
/:pathMatch(.*) * - 404 Not Found
```

### Navigation Guards

**File**: `src/router/index.ts`

**Global Before Each**:
```typescript
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  
  // Initialize auth on first navigation
  if (!authStore.isAuthenticated) {
    authStore.initializeAuth();
  }
  
  // Guest-only routes
  if (to.meta.guestOnly && authStore.isAuthenticated) {
    return next(authStore.isAdmin ? '/admin/dashboard' : '/cliente/dashboard');
  }
  
  // Protected routes
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return next({ path: '/login', query: { redirect: to.fullPath } });
  }
  
  // Role-based access
  if (to.meta.role === 'ADMIN' && !authStore.isAdmin) {
    return next('/cliente/dashboard');
  }
  
  if (to.meta.role === 'CLIENTE' && !authStore.isCliente) {
    return next('/admin/dashboard');
  }
  
  next();
});
```

---

## 🔌 API Integration

### Axios Client Configuration

**File**: `src/api/client.ts`

```typescript
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add JWT token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  }
);

// Response interceptor - Handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Auto logout on unauthorized
      const authStore = useAuthStore();
      authStore.logout();
      router.push('/login');
    }
    return Promise.reject(error);
  }
);
```

### API Endpoints Mapping

#### IAM Service (`/api/iam`)

```typescript
// Authentication
POST   /auth/login            → login(email, password)
POST   /auth/register         → register(userData)
GET    /auth/profile          → getProfile()
PUT    /auth/profile          → updateProfile(data)

// Admin User Management
GET    /admin/users           → getUsers()
POST   /admin/users           → createUser(data)
PUT    /admin/users/:id       → updateUser(id, data)
DELETE /admin/users/:id       → deleteUser(id)
```

#### Catalog Service (`/api/catalogo`)

```typescript
// Tipos de Evento
GET    /tipos-evento          → getTiposEvento()
POST   /admin/tipos-evento    → createTipoEvento(data)
PUT    /admin/tipos-evento/:id → updateTipoEvento(id, data)
DELETE /admin/tipos-evento/:id → deleteTipoEvento(id)

// Servicios
GET    /servicios             → getServicios()
GET    /servicios/:tipoId     → getServiciosByTipo(tipoId)
POST   /admin/servicios       → createServicio(data)
PUT    /admin/servicios/:id   → updateServicio(id, data)
DELETE /admin/servicios/:id   → deleteServicio(id)

// Paquetes
GET    /paquetes              → getPaquetes()
GET    /paquetes/:id          → getPaqueteById(id)
POST   /admin/paquetes        → createPaquete(data)
PUT    /admin/paquetes/:id    → updatePaquete(id, data)
DELETE /admin/paquetes/:id    → deletePaquete(id)
```

#### Orders Service (`/api/contratacion`)

```typescript
// Pedidos
GET    /pedidos               → getPedidos()
GET    /pedidos?usuario_id=X  → getPedidosByUser(userId)
GET    /pedidos/:id           → getPedidoById(id)
POST   /pedidos               → createPedido(data)
PUT    /pedidos/:id           → updatePedido(id, data)
DELETE /pedidos/:id           → deletePedido(id)
```

---

## 📄 Views Implementation

### ✅ COMPLETED VIEWS

#### 1. CreateOrderWizard.vue (Client) - **CRITICAL**

**Route**: `/cliente/pedido/nuevo`

**Features**:
- 3-step wizard with progress indicator
- Step 1: Select tipo_evento, paquete, fecha, num_invitados
- Step 2: Select servicios adicionales, add comentarios, show price summary
- Step 3: Review and confirm
- Real-time price calculation
- Draft state management (can go back/forth)
- Success modal on completion
- Validation on each step

**State Management**:
- Uses `ordersStore.draftOrder` for wizard state
- Persists draft between steps
- Clears on cancel or success

**Code Highlights**:
```typescript
// Load catalog data
await catalogStore.fetchTiposEvento();
await catalogStore.fetchPaquetes();
await catalogStore.fetchServicios();

// Price calculation
const totalPrice = computed(() => {
  let total = selectedPaquete.value?.precio_base || 0;
  draft.value.servicios_adicionales.forEach(id => {
    const servicio = catalogStore.servicios.find(s => s.id === id);
    total += servicio?.precio_unitario || 0;
  });
  return total;
});

// Submit order
await ordersStore.createPedido({
  tipo_evento_id: draft.value.tipo_evento_id!,
  fecha_evento: draft.value.fecha_evento!,
  num_invitados: draft.value.num_invitados!,
  paquete_id: draft.value.paquete_id,
  servicios_adicionales: draft.value.servicios_adicionales,
  comentarios: draft.value.comentarios,
});
```

#### 2. MisPedidos.vue (Client)

**Route**: `/cliente/pedidos`

**Features**:
- List all user's orders
- Filter by estado (PENDIENTE, CONFIRMADO, etc.)
- Card-based layout (not table)
- Status badges with colors
- View details modal
- Cancel order action (for PENDIENTE orders)
- Date formatting with date-fns
- Empty state with CTA

**UI Elements**:
- Status badges: Yellow (PENDIENTE), Green (CONFIRMADO), Blue (EN_PROGRESO), Purple (COMPLETADO), Red (CANCELADO)
- Event icons: 💒 Boda, 👗 Quinceañera, 🎂 Cumpleaños, etc.

#### 3. Servicios.vue (Admin)

**Route**: `/admin/servicios`

**Features**:
- Full CRUD table
- SearchBar integration
- Create/Edit modal with form
- Category dropdown (FOTOGRAFIA, VIDEO, CATERING, etc.)
- Tipo evento association
- Precio unitario input
- Disponible checkbox
- Delete confirmation

**Form Fields**:
- Nombre (required)
- Descripción (required)
- Categoría (dropdown, required)
- Tipo Evento (select from tipos, required)
- Precio Unitario (number, required)
- Disponible (checkbox)

#### 4. Paquetes.vue (Admin)

**Route**: `/admin/paquetes`

**Features**:
- Full CRUD table
- Search + filter by tipo evento
- Multi-select servicios (checkboxes)
- Show included servicios in table
- Create/Edit modal with complex form
- Dynamic servicios list based on tipo_evento
- Service count indicator

**Complex Logic**:
```typescript
// Filter servicios by selected tipo_evento
const availableServicios = computed(() => {
  if (!form.tipo_evento_id) return [];
  return catalogStore.servicios.filter(s => 
    s.tipo_evento_id === form.tipo_evento_id
  );
});

// Multi-select servicios
<input
  type="checkbox"
  :value="servicio.id"
  v-model="form.servicios_ids"
/>
```

### 🟡 SKELETON VIEWS (To be implemented)

#### Usuarios.vue (Admin)

**Required Features**:
- Table with columns: ID, Nombre, Email, Role, Estado, Acciones
- Filter by role (CLIENTE/ADMIN) and estado (ACTIVO/INACTIVO)
- Create/Edit modal with role dropdown
- Delete confirmation
- Toggle activo/inactivo

**API Integration**: `iamApi.getUsers()`, `createUser()`, `updateUser()`, `deleteUser()`

#### Pedidos.vue (Admin)

**Required Features**:
- Table showing all orders (not just user's)
- Columns: ID, Usuario, Tipo Evento, Fecha, Estado, Total, Acciones
- Filter by estado
- View details modal (same as client view)
- Assign provider action (if needed)
- Update estado

#### Profile.vue (Client/Shared)

**Required Features**:
- Form with fields: nombre, apellido, email (readonly), telefono
- Update password section
- Save button → `authStore.updateProfile()`
- Success/error feedback

#### Client Paquetes.vue

**Required Features**:
- Grid of cards (3 columns desktop, 1 mobile)
- Filter by tipo_evento
- Show paquete details: nombre, precio, servicios included
- "Seleccionar" button → redirect to `/cliente/pedido/nuevo?paquete_id=X`

#### Public Paquetes.vue & PaqueteDetalle.vue

**Required Features**:
- Browse packages without auth
- Filter/search
- Show details
- CTA to login or create order

---

## 🔐 Authentication Flow Details

### Login Process

```
1. User visits /login
2. Enters email + password
3. Form submits → authStore.login(email, password)
4. authStore calls iamApi.login(email, password)
5. Backend validates credentials
6. Returns { access_token, user }
7. authStore saves:
   - token → localStorage + state
   - user → state
8. Router guard redirects based on role:
   - ADMIN → /admin/dashboard
   - CLIENTE → /cliente/dashboard
9. All subsequent API calls include token (interceptor)
```

### Token Persistence

```typescript
// On app mount (App.vue)
authStore.initializeAuth();

// initializeAuth() in auth.ts
const initializeAuth = () => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    // Decode JWT to check expiry
    try {
      const decoded = jwtDecode(token);
      if (decoded.exp * 1000 > Date.now()) {
        // Token valid, restore session
        state.token = token;
        fetchProfile(); // Load user data
      } else {
        // Token expired
        logout();
      }
    } catch {
      logout();
    }
  }
};
```

### Auto Logout

```typescript
// Axios response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const authStore = useAuthStore();
      authStore.logout();
      router.push({
        path: '/login',
        query: { redirect: router.currentRoute.value.fullPath }
      });
    }
    return Promise.reject(error);
  }
);
```

---

## 🐳 Deployment

### Docker Build

**Dockerfile** (Multi-stage):

```dockerfile
# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Serve
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Build & Push**:
```bash
docker build -t emeday17/eventos-frontend:1.0.0 .
docker push emeday17/eventos-frontend:1.0.0
```

### Nginx Configuration

**nginx.conf**:

```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    # SPA routing - fallback to index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API calls to backend
    location /api/ {
        proxy_pass http://api-gateway:8080/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Health check
    location /health {
        return 200 "OK\n";
        add_header Content-Type text/plain;
    }

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
}
```

### Kubernetes Deployment

**k8s/deployment.yaml**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: eventos-frontend
  namespace: eventos-peru
spec:
  replicas: 2
  selector:
    matchLabels:
      app: eventos-frontend
  template:
    metadata:
      labels:
        app: eventos-frontend
    spec:
      containers:
      - name: frontend
        image: emeday17/eventos-frontend:1.0.0
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /health
            port: 80
          initialDelaySeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 80
          initialDelaySeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: eventos-frontend
  namespace: eventos-peru
spec:
  type: ClusterIP
  selector:
    app: eventos-frontend
  ports:
  - port: 80
    targetPort: 80
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: eventos-frontend
  namespace: eventos-peru
  annotations:
    kubernetes.io/ingress.class: nginx
spec:
  rules:
  - host: eventos.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: eventos-frontend
            port:
              number: 80
```

**Deploy**:
```bash
kubectl apply -f k8s/deployment.yaml
kubectl -n eventos-peru rollout status deployment/eventos-frontend
```

---

## 🧪 Testing

### Manual Testing Checklist

**Authentication**:
- [ ] Login with valid credentials (cliente@test.com / cliente123)
- [ ] Login with valid credentials (admin@test.com / admin123)
- [ ] Login with invalid credentials → error message
- [ ] Logout → redirects to home
- [ ] Access protected route without auth → redirects to /login
- [ ] Token persists after page refresh

**Client Flows**:
- [ ] View dashboard with stats
- [ ] Navigate to "Crear Pedido"
- [ ] Complete wizard Step 1 (select tipo, paquete, fecha, invitados)
- [ ] Complete wizard Step 2 (select servicios, add comentarios)
- [ ] Review summary in Step 3
- [ ] Confirm order → success modal
- [ ] View "Mis Pedidos" → see created order
- [ ] Filter orders by estado
- [ ] View order details
- [ ] Cancel PENDIENTE order

**Admin Flows**:
- [ ] View admin dashboard
- [ ] Create new tipo evento
- [ ] Edit existing tipo evento
- [ ] Delete tipo evento (with confirmation)
- [ ] Search tipos evento
- [ ] Create new servicio (select tipo, categoria, precio)
- [ ] Edit servicio
- [ ] Delete servicio
- [ ] Create new paquete (select tipo, multi-select servicios)
- [ ] Edit paquete (change servicios)
- [ ] Delete paquete

**UI/UX**:
- [ ] Mobile responsiveness (test on 375px width)
- [ ] Navbar changes based on role
- [ ] Loading states show during API calls
- [ ] Error messages display correctly
- [ ] Forms validate required fields
- [ ] Modals open/close properly
- [ ] Buttons show loading state during submission

---

## 📊 Progress Tracking

### Implementation Status

| Category | Total | Complete | Skeleton | Missing | % Done |
|----------|-------|----------|----------|---------|--------|
| **Infrastructure** | 10 | 10 | 0 | 0 | 100% |
| **Components** | 8 | 8 | 0 | 0 | 100% |
| **Layouts** | 3 | 3 | 0 | 0 | 100% |
| **API Layer** | 5 | 5 | 0 | 0 | 100% |
| **Stores** | 3 | 3 | 0 | 0 | 100% |
| **Public Views** | 5 | 2 | 3 | 0 | 40% |
| **Client Views** | 5 | 3 | 2 | 0 | 60% |
| **Admin Views** | 6 | 4 | 2 | 0 | 67% |
| **Deployment** | 3 | 3 | 0 | 0 | 100% |

**Overall: 75% Complete**

### Recently Implemented (Nov 27, 2025)

1. ✅ **CreateOrderWizard.vue** - 3-step wizard for order creation (CRITICAL)
2. ✅ **MisPedidos.vue** - Client orders list with filters and details modal
3. ✅ **Servicios.vue** - Admin CRUD for services
4. ✅ **Paquetes.vue** - Admin CRUD for packages with multi-select servicios

### Next Steps (Priority Order)

1. **Usuarios.vue (Admin)** - User management CRUD
2. **Pedidos.vue (Admin)** - All orders view for admin
3. **Profile.vue** - User profile editor
4. **Client Paquetes.vue** - Package browser for clients
5. **Public views** - Paquetes, PaqueteDetalle, Proveedores

### Known Issues / TODO

- [ ] Add form validation library (vee-validate or similar)
- [ ] Add toast notification system (instead of alert())
- [ ] Implement error boundaries
- [ ] Add loading skeletons
- [ ] Optimize bundle size (analyze with vite-bundle-visualizer)
- [ ] Add E2E tests (Cypress or Playwright)
- [ ] Add unit tests for stores (Vitest)
- [ ] Implement PWA features (service worker, offline support)
- [ ] Add analytics integration (Google Analytics or similar)

---

## 📚 Additional Resources

### Code Examples

**Creating a New CRUD View** (copy TiposEvento.vue pattern):

1. Create view file: `src/views/admin/EntityName.vue`
2. Import stores and components
3. Define reactive state (searchQuery, showModal, form)
4. Create computed filteredItems
5. Implement CRUD methods (create, edit, delete)
6. Build table with SearchBar
7. Build Modal with form
8. Call store actions

**Adding a New API Endpoint**:

1. Add type definition in `src/types/`
2. Add API function in `src/api/service.ts`
3. Add store action in `src/stores/store.ts`
4. Use in component

### Useful Commands

```bash
# Development
npm run dev          # Start dev server (http://localhost:5173)
npm run build        # Build for production
npm run preview      # Preview production build

# Docker
docker build -t eventos-frontend .
docker run -p 8080:80 eventos-frontend

# Kubernetes
kubectl apply -f k8s/
kubectl get pods -n eventos-peru
kubectl logs -f deployment/eventos-frontend -n eventos-peru
kubectl port-forward svc/eventos-frontend 8080:80 -n eventos-peru
```

### Troubleshooting

**Issue**: "Cannot find module '@/...'
**Solution**: Check `tsconfig.app.json` and `vite.config.ts` have correct path aliases

**Issue**: API calls fail with CORS error
**Solution**: Ensure backend has correct CORS configuration or use Vite proxy in dev

**Issue**: Token not persisting
**Solution**: Check localStorage in DevTools, verify initializeAuth() is called in App.vue

**Issue**: Build fails with TypeScript errors
**Solution**: Run `npm run build` to see full error output, fix type issues

---

## 📝 Change Log

### v1.0.0 - November 27, 2025

**Added**:
- ✅ Complete project setup (Vite + Vue 3 + TypeScript + Tailwind)
- ✅ 8 reusable components (Button, Card, Modal, Input, Table, Pagination, SearchBar, Loading)
- ✅ 3 layouts (Public, Client, Admin) with navbars
- ✅ Complete API layer with interceptors
- ✅ 3 Pinia stores (auth, catalog, orders) with caching
- ✅ Vue Router with authentication guards
- ✅ Login page with validation
- ✅ Home page (landing)
- ✅ Client Dashboard
- ✅ Admin Dashboard
- ✅ Admin TiposEvento CRUD (template)
- ✅ CreateOrderWizard (3-step wizard)
- ✅ MisPedidos (client orders list)
- ✅ Admin Servicios CRUD
- ✅ Admin Paquetes CRUD
- ✅ Docker multi-stage build
- ✅ Nginx configuration
- ✅ Kubernetes manifests

**Pending**:
- 🟡 Admin Usuarios CRUD
- 🟡 Admin Pedidos view
- 🟡 Profile editor
- 🟡 Client Paquetes browser
- 🟡 Public Paquetes views

---

## 🤝 Contributing

### Code Style

- Use TypeScript for type safety
- Follow Vue 3 Composition API patterns
- Use `<script setup>` syntax
- Keep components under 300 lines (split if needed)
- Use Tailwind utility classes (avoid custom CSS)
- Name files in PascalCase for components, camelCase for utilities
- Export types from barrel files (index.ts)

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/usuarios-crud

# Make changes and commit
git add .
git commit -m "feat: implement usuarios CRUD view"

# Push and create PR
git push origin feature/usuarios-crud
```

---

**End of Documentation**

For questions or issues, contact: development@eventos-peru.com
