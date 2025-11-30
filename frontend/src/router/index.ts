import { createRouter, createWebHistory } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router';
import { useAuthStore } from '@/stores';

// Layouts
import PublicLayout from '@/components/layout/PublicLayout.vue';
import ClientLayout from '@/components/layout/ClientLayout.vue';
import AdminLayout from '@/components/layout/AdminLayout.vue';

const routes: RouteRecordRaw[] = [
  // Public routes
  {
    path: '/',
    component: PublicLayout,
    children: [
      {
        path: '',
        name: 'home',
        component: () => import('@/views/public/Home.vue'),
      },
      {
        path: 'login',
        name: 'login',
        component: () => import('@/views/public/Login.vue'),
        meta: { guestOnly: true },
      },
      {
        path: 'paquetes',
        name: 'paquetes',
        component: () => import('@/views/public/Paquetes.vue'),
      },
      {
        path: 'paquetes/:id',
        name: 'paquete-detalle',
        component: () => import('@/views/public/PaqueteDetalle.vue'),
      },
      {
        path: 'proveedores',
        name: 'proveedores',
        component: () => import('@/views/public/Proveedores.vue'),
      },
    ],
  },

  // Client routes
  {
    path: '/cliente',
    component: ClientLayout,
    meta: { requiresAuth: true, role: 'CLIENTE' },
    children: [
      {
        path: 'dashboard',
        name: 'cliente-dashboard',
        component: () => import('@/views/client/Dashboard.vue'),
      },
      {
        path: 'paquetes',
        name: 'cliente-paquetes',
        component: () => import('@/views/client/Paquetes.vue'),
      },
      {
        path: 'pedidos',
        name: 'cliente-pedidos',
        component: () => import('@/views/client/MisPedidos.vue'),
      },
      {
        path: 'pedido/nuevo',
        name: 'cliente-pedido-nuevo',
        component: () => import('@/views/client/CreateOrderWizard.vue'),
      },
      {
        path: 'perfil',
        name: 'perfil',
        component: () => import('@/views/client/Profile.vue'),
      },
    ],
  },

  // Perfil route (Shortcut)
  {
    path: '/perfil',
    component: ClientLayout,
    meta: { requiresAuth: true, role: 'CLIENTE' },
    children: [
      {
        path: '',
        name: 'perfil-direct',
        component: () => import('@/views/client/Profile.vue'),
      },
    ],
  },

  // Admin routes
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true, role: 'ADMIN' },
    children: [
      {
        path: 'dashboard',
        name: 'admin-dashboard',
        component: () => import('@/views/admin/Dashboard.vue'),
      },
      {
        path: 'tipos-evento',
        name: 'admin-tipos-evento',
        component: () => import('@/views/admin/TiposEvento.vue'),
      },
      {
        path: 'servicios',
        name: 'admin-servicios',
        component: () => import('@/views/admin/Servicios.vue'),
      },
      {
        path: 'paquetes',
        name: 'admin-paquetes',
        component: () => import('@/views/admin/Paquetes.vue'),
      },
      {
        path: 'proveedores',
        name: 'admin-proveedores',
        component: () => import('@/views/admin/Proveedores.vue'),
      },
      {
        path: 'pedidos',
        name: 'admin-pedidos',
        component: () => import('@/views/admin/Pedidos.vue'),
      },
      {
        path: 'usuarios',
        name: 'admin-usuarios',
        component: () => import('@/views/admin/Usuarios.vue'),
      },
    ],
  },

  // Fallback 404
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/public/NotFound.vue'),
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    } else {
      return { top: 0 };
    }
  },
});

// Navigation guards
router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore();

  // Inicializar autenticación desde localStorage solo si hay token pero no user
  if (!authStore.user && localStorage.getItem('access_token')) {
    // initializeAuth is synchronous but awaiting is safe if it becomes async later
    await authStore.initializeAuth();
  }

  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  const guestOnly = to.matched.some(record => record.meta.guestOnly);
  const requiredRole = to.meta.role as string | undefined;

  // Ruta solo para invitados (login cuando ya está autenticado)
  if (guestOnly && authStore.isAuthenticated) {
    if (authStore.isAdmin) {
      next('/admin/dashboard');
    } else {
      next('/cliente/dashboard');
    }
    return;
  }

  // Ruta que requiere autenticación
  if (requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } });
    return;
  }

  // Verificar rol si es necesario
  if (requiredRole && authStore.user?.role !== requiredRole) {
    // Si el usuario tiene rol diferente, redirigir a su dashboard
    if (authStore.isAdmin) {
      next('/admin/dashboard');
    } else {
      next('/cliente/dashboard');
    }
    return;
  }

  next();
});

export default router;
