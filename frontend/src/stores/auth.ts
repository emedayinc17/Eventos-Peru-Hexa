import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { iamApi } from '@/api';
import type { User, LoginRequest, RegisterRequest } from '@/types';
import { isTokenExpired, getTokenRemainingTime, willTokenExpireSoon } from '@/utils/jwt';

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null);
  const token = ref<string | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);
  let tokenCheckInterval: number | null = null;

  // Actions (defined before getters that use them if needed, but hoisting works)
  function logout(): void {
    user.value = null;
    token.value = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    stopTokenMonitoring();

    // Redirect to login if not already there
    if (window.location.pathname !== '/login') {
      window.location.href = '/login';
    }
  }

  // Getters
  const isAuthenticated = computed(() => {
    if (!token.value || !user.value) return false;

    // Verify token is not expired
    if (isTokenExpired(token.value)) {
      logout();
      return false;
    }

    return true;
  });

  const isAdmin = computed(() => (user.value?.role || '').toString().toLowerCase() === 'admin');
  const isCliente = computed(() => (user.value?.role || '').toString().toLowerCase() === 'cliente');
  // English alias
  const isClient = computed(() => isCliente.value);
  const userFullName = computed(() => user.value?.nombre || '');
  const tokenRemainingTime = computed(() => {
    if (!token.value) return 0;
    return getTokenRemainingTime(token.value);
  });

  /**
   * Stop token monitoring
   */
  function stopTokenMonitoring(): void {
    if (tokenCheckInterval !== null) {
      clearInterval(tokenCheckInterval);
      tokenCheckInterval = null;
    }
  }

  /**
   * Start periodic token expiration checking
   */
  function startTokenMonitoring(): void {
    // Clear any existing interval
    stopTokenMonitoring();

    // Check token every 30 seconds
    tokenCheckInterval = window.setInterval(() => {
      if (!token.value) {
        stopTokenMonitoring();
        return;
      }

      // Check if token is expired
      if (isTokenExpired(token.value)) {
        console.log('Token expired, logging out');
        logout();
        return;
      }

      // Optional: Show warning if token will expire soon (5 minutes)
      if (willTokenExpireSoon(token.value, 5)) {
        const remaining = getTokenRemainingTime(token.value);
        console.warn(`Token will expire in ${Math.floor(remaining / 60)} minutes`);
        // You could show a toast notification here
      }
    }, 30000); // Check every 30 seconds
  }

  // Actions
  async function login(credentials: LoginRequest): Promise<boolean> {
    loading.value = true;
    error.value = null;

    try {
      const response = await iamApi.login(credentials);

      // Guardar token primero
      token.value = response.access_token;
      localStorage.setItem('access_token', response.access_token);

      // Obtener datos completos del usuario usando el token
      const profile = await iamApi.getProfile();
      user.value = {
        ...profile,
        role: response.role || profile.role, // Usar el role del login como fallback
      };

      // Persistir usuario en localStorage
      localStorage.setItem('user', JSON.stringify(user.value));

      // Start token expiration monitoring
      startTokenMonitoring();

      return true;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al iniciar sesión';
      // Limpiar en caso de error
      token.value = null;
      user.value = null;
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      return false;
    } finally {
      loading.value = false;
    }
  }

  async function register(userData: RegisterRequest): Promise<boolean> {
    loading.value = true;
    error.value = null;

    // Dev/debug helper: log register payload to help verify frontend is sending password
    try {
      const debugAll = (import.meta.env && import.meta.env.VITE_DEBUG_AUTH === 'true');
      if (debugAll) {
        // Verbose: show full payload (use only in development with VITE_DEBUG_AUTH=true)
        // eslint-disable-next-line no-console
        console.debug('[auth] register payload (VERBOSE):', userData);
      } else {
        // Non-verbose: only indicate presence/length to avoid leaking passwords in normal dev
        // eslint-disable-next-line no-console
        console.debug('[auth] register payload:', { email: userData.email, password_present: !!userData.password, password_length: userData.password ? userData.password.length : 0 });
      }
    } catch (e) {
      // ignore if env not available
    }

    try {
      await iamApi.register(userData);
      return true;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al registrarse';
      return false;
    } finally {
      loading.value = false;
    }
  }

  async function fetchProfile(): Promise<void> {
    loading.value = true;
    error.value = null;

    try {
      const profile = await iamApi.getProfile();
      user.value = profile;
      localStorage.setItem('user', JSON.stringify(profile));
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al obtener perfil';
      // Si falla, limpiar sesión
      logout();
    } finally {
      loading.value = false;
    }
  }

  async function updateProfile(userData: Partial<User>): Promise<boolean> {
    loading.value = true;
    error.value = null;

    try {
      const updatedUser = await iamApi.updateProfile(userData);
      user.value = updatedUser;
      localStorage.setItem('user', JSON.stringify(updatedUser));
      return true;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al actualizar perfil';
      return false;
    } finally {
      loading.value = false;
    }
  }

  async function changePassword(currentPassword: string, newPassword: string): Promise<boolean> {
    loading.value = true;
    error.value = null;

    try {
      await iamApi.changePassword(currentPassword, newPassword);
      return true;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al cambiar contraseña';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function initializeAuth(): Promise<void> {
    const storedToken = localStorage.getItem('access_token');
    const storedUser = localStorage.getItem('user');

    if (!storedToken) return;

    // If token exists but is expired, clear everything
    if (isTokenExpired(storedToken)) {
      console.log('Stored token is expired, logging out');
      logout();
      return;
    }

    // Restore token in memory (client interceptor reads from localStorage too)
    token.value = storedToken;

    if (storedUser) {
      try {
        user.value = JSON.parse(storedUser);
        startTokenMonitoring();
        return;
      } catch (e) {
        // If parsing fails, fall through to re-fetch profile
        console.warn('Failed to parse stored user, refetching profile');
      }
    }

    // If we reached here we have a valid token but no usable user object.
    // Try to fetch profile from the API using the token.
    try {
      loading.value = true;
      const profile = await iamApi.getProfile();
      user.value = profile;
      localStorage.setItem('user', JSON.stringify(profile));
      startTokenMonitoring();
    } catch (err: any) {
      console.warn('Failed to initialize auth from token:', err?.response?.data || err?.message);
      // If profile cannot be fetched, clear local storage to avoid loops
      token.value = null;
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
    } finally {
      loading.value = false;
    }
  }

  // Role helper
  function hasRole(roleName: string): boolean {
    if (!user.value || !user.value.role) return false;
    return (user.value.role || '').toString().toLowerCase() === (roleName || '').toString().toLowerCase();
  }

  return {
    // State
    user,
    token,
    loading,
    error,
    // Getters
    isAuthenticated,
    isAdmin,
    isCliente,
    isClient,
    userFullName,
    tokenRemainingTime,
    // Actions
    login,
    register,
    fetchProfile,
    updateProfile,
    changePassword,
    logout,
    initializeAuth,
    hasRole,
  };
});
