import axios, { AxiosError } from 'axios';
import type { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios';

// Base URL para la API - usar API Gateway en producción
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

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

      if (status === 401) {
        // Token inválido o expirado - limpiar y redirigir a login
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      } else if (status === 403) {
        // Forbidden - sin permisos
        console.error('Acceso denegado: No tienes permisos para esta acción');
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
