import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { iamApi } from '@/api';
import type { User, LoginRequest, RegisterRequest } from '@/types';

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null);
  const token = ref<string | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value);
  const isAdmin = computed(() => user.value?.role === 'ADMIN');
  const isCliente = computed(() => user.value?.role === 'CLIENTE');
  const userFullName = computed(() => user.value?.nombre || '');

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

  function logout(): void {
    user.value = null;
    token.value = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  }

  function initializeAuth(): void {
    const storedToken = localStorage.getItem('access_token');
    const storedUser = localStorage.getItem('user');
    
    if (storedToken && storedUser) {
      token.value = storedToken;
      try {
        user.value = JSON.parse(storedUser);
      } catch {
        logout();
      }
    }
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
    userFullName,
    // Actions
    login,
    register,
    fetchProfile,
    updateProfile,
    logout,
    initializeAuth,
  };
});
