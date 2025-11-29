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

  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await apiClient.post(`${IAM_BASE}/auth/change-password`, {
      current_password: currentPassword,
      new_password: newPassword,
    });
  },

  // Gestión de usuarios (ADMIN)
  async getUsers(params?: { limit?: number; offset?: number }): Promise<User[]> {
    const response = await apiClient.get<User[]>(`${IAM_BASE}/admin/users`, { params });
    return response.data;
  },

  async createUser(userData: RegisterRequest): Promise<User> {
    const response = await apiClient.post<User>(`${IAM_BASE}/admin/users`, userData);
    return response.data;
  },

  async updateUser(userId: number | string, userData: Partial<User> & { password?: string }): Promise<User> {
    const response = await apiClient.patch<User>(`${IAM_BASE}/admin/users/${userId}`, userData);
    return response.data;
  },

  async deleteUser(userId: number | string): Promise<void> {
    await apiClient.delete(`${IAM_BASE}/admin/users/${userId}`);
  },
};
