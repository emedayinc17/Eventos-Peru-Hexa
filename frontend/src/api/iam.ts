import apiClient from './client';
import type { LoginRequest, LoginResponse, RegisterRequest, User } from '@/types';

// Note: `apiClient` already has baseURL `/api`, so IAM paths should be relative
// to that base to avoid `//api/api/...` being requested by the dev proxy.
const IAM_BASE = '/iam';

export const iamApi = {
  // Autenticación
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>(`${IAM_BASE}/auth/login`, credentials);
    return response.data;
  },

  async register(userData: RegisterRequest): Promise<User> {
    const response = await apiClient.post<User>(`${IAM_BASE}/auth/register`, userData);
    return response.data;
  },

  async getProfile(): Promise<User> {
    const response = await apiClient.get<User>(`${IAM_BASE}/me`);
    return response.data;
  },

  async updateProfile(userData: Partial<User>): Promise<User> {
    const response = await apiClient.put<User>(`${IAM_BASE}/auth/profile`, userData);
    return response.data;
  },

  // Gestión de usuarios (ADMIN)
  async getUsers(): Promise<{ data: User[] }> {
    const response = await apiClient.get<{ data: User[] }>(`${IAM_BASE}/admin/users`);
    return response.data;
  },

  async createUser(userData: RegisterRequest): Promise<User> {
    const response = await apiClient.post<User>(`${IAM_BASE}/admin/users`, userData);
    return response.data;
  },

  async updateUser(userId: number, userData: Partial<User>): Promise<User> {
    const response = await apiClient.put<User>(`${IAM_BASE}/admin/users/${userId}`, userData);
    return response.data;
  },

  async deleteUser(userId: number): Promise<void> {
    await apiClient.delete(`${IAM_BASE}/admin/users/${userId}`);
  },
};
