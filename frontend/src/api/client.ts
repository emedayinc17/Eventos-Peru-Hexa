import axios, { AxiosError } from 'axios';
import type { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios';

// Base URL para la API - preferir runtime config (`window.__APP_CONFIG__`) if está disponible,
// otherwise usar la variable de build `VITE_API_BASE_URL` o fallback a '/api'.
function getRuntimeApiBase() {
  try {
    const cfg = (window as any).__APP_CONFIG__;
    if (cfg && cfg.VITE_API_BASE_URL) return cfg.VITE_API_BASE_URL;
  } catch (e) {
    // ignore
  }
  return (import.meta.env.VITE_API_BASE_URL as string) || '/api';
}

const API_BASE_URL = getRuntimeApiBase();

// Crear instancia de Axios
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor de Request - Agregar JWT token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token');
    
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Interceptor de Response - Manejo de errores global
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error: AxiosError) => {
    // If the request set the `X-Suppress-Error` header, skip global error handling/logging
    const cfg = (error.config as any) || {};
    const suppress = cfg.headers && (cfg.headers['X-Suppress-Error'] || cfg.headers['x-suppress-error']);

    if (error.response) {
      // El servidor respondió con un status code fuera del rango 2xx
      const status = error.response.status;
      
      if (suppress) {
        return Promise.reject(error);
      }
        // FIX: Distinguish token problems vs permission checks and avoid logging out
        // for 401s coming from non-auth routes (e.g. admin endpoints). Force
        // logout only when the backend detail indicates an invalid/expired token
        // AND the request appears to be an IAM/auth related call (path contains '/iam').
        // This prevents legitimate 401/403 permission rejections from kicking users out.
        if (status === 401) {
          // Diferenciar 401 por token inválido/expirado vs 401 por otros motivos.
          // Algunas rutas pueden devolver 401/403 por permisos; no queremos cerrar
          // la sesión por un 401 que signifique simplemente "no tiene acceso a
          // este recurso". Revisamos el body.detail para detectar errores de token.
          const detail = (error.response.data && error.response.data.detail) || null;
          const detailStr = typeof detail === 'string' ? detail : JSON.stringify(detail || '');
          const isTokenProblem = /token inv[aá]lido|expirad|falta authorization|claims?/i.test(detailStr);
          // Determine request URL (may be relative e.g. '/api/iam/me')
          const reqUrl = (error.config && (error.config.url || error.config.baseURL)) || '';
          const isIamPath = typeof reqUrl === 'string' && reqUrl.toLowerCase().includes('/iam');

          if (isTokenProblem && isIamPath) {
            // Token inválido/expirado en endpoints IAM => cerrar sesión
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');
            window.location.href = '/login';
            return Promise.reject(error);
          }

          // Otherwise do NOT logout: emit event so UI can show permission message
          console.warn('401 recibido pero no parece ser problema de token:', detailStr);
          try {
            window.dispatchEvent(new CustomEvent('auth:insufficient', { detail: { status: 401, detail: detailStr, url: reqUrl } }));
          } catch (e) {
            // ignore if CustomEvent unsupported in environment
          }
          return Promise.reject(error);
        } else if (status === 403) {
          // Forbidden - sin permisos. No forzamos logout, permitimos que la UI muestre un 403.
          console.warn('Acceso denegado (403): No tienes permisos para esta acción');
          try {
            window.dispatchEvent(new CustomEvent('auth:insufficient', { detail: { status: 403, detail: error.response.data?.detail || null } }));
          } catch (e) {
            // ignore
          }
        } else if (status === 404) {
        console.error('Recurso no encontrado');
      } else if (status >= 500) {
        console.error('Error del servidor. Por favor intenta más tarde.');
      }
    } else if (error.request) {
      // La petición fue hecha pero no hubo respuesta
      if (!suppress) console.error('Error de red: No se pudo conectar con el servidor');
    } else {
      // Algo pasó al configurar la petición
      if (!suppress) console.error('Error al procesar la petición:', error.message);
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
