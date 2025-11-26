/**
 * ADAPTADOR - IAM Service
 * Implementa la comunicación con el microservicio de autenticación
 */

import axiosClient from '../lib/axios';
import { API_CONFIG, APP_CONFIG } from '../lib/config';
import { LoginCredentials, RegisterData, AuthResponse, Usuario } from '../types';

class AuthService {
    private baseURL = API_CONFIG.IAM;

    /**
     * Login de usuario
     */
    async login(credentials: LoginCredentials): Promise<AuthResponse> {
        const response = await axiosClient.post<AuthResponse>(
            `${this.baseURL}/auth/login`,
            credentials
        );

        // Guardar token en localStorage
        if (response.data.access_token) {
            localStorage.setItem(APP_CONFIG.TOKEN_KEY, response.data.access_token);
        }

        return response.data;
    }

    /**
     * Registro de nuevo usuario
     */
    async register(data: RegisterData): Promise<AuthResponse> {
        const response = await axiosClient.post<AuthResponse>(
            `${this.baseURL}/auth/register`,
            data
        );

        // Guardar token en localStorage
        if (response.data.access_token) {
            localStorage.setItem(APP_CONFIG.TOKEN_KEY, response.data.access_token);
        }

        return response.data;
    }

    /**
     * Obtener perfil del usuario actual
     */
    async getProfile(): Promise<Usuario> {
        const response = await axiosClient.get<Usuario>(`${this.baseURL}/me`);
        return response.data;
    }

    /**
     * Logout (elimina token)
     */
    logout(): void {
        localStorage.removeItem(APP_CONFIG.TOKEN_KEY);
    }

    /**
     * Verificar si hay un token guardado
     */
    isAuthenticated(): boolean {
        return !!localStorage.getItem(APP_CONFIG.TOKEN_KEY);
    }

    /**
     * Obtener token actual
     */
    getToken(): string | null {
        return localStorage.getItem(APP_CONFIG.TOKEN_KEY);
    }

    // ========== ADMIN ENDPOINTS ==========

    /**
     * Listar todos los usuarios (ADMIN)
     */
    async listUsers(limit = 50, offset = 0): Promise<Usuario[]> {
        const response = await axiosClient.get<Usuario[]>(
            `${this.baseURL}/admin/users`,
            { params: { limit, offset } }
        );
        return response.data;
    }

    /**
     * Obtener usuario por ID (ADMIN)
     */
    async getUserById(id: string): Promise<Usuario> {
        const response = await axiosClient.get<Usuario>(
            `${this.baseURL}/admin/users/${id}`
        );
        return response.data;
    }

    /**
     * Crear usuario (ADMIN)
     */
    async createUser(data: RegisterData & { rol?: string }): Promise<Usuario> {
        const response = await axiosClient.post<Usuario>(
            `${this.baseURL}/admin/users`,
            data
        );
        return response.data;
    }

    /**
     * Actualizar usuario (ADMIN)
     */
    async updateUser(id: string, data: Partial<Usuario>): Promise<Usuario> {
        const response = await axiosClient.patch<Usuario>(
            `${this.baseURL}/admin/users/${id}`,
            data
        );
        return response.data;
    }

    /**
     * Eliminar usuario (ADMIN)
     */
    async deleteUser(id: string): Promise<void> {
        await axiosClient.delete(`${this.baseURL}/admin/users/${id}`);
    }
}

// Exportar instancia singleton
export const authService = new AuthService();
