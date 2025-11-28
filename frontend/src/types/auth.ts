export interface User {
  id: string;
  nombre: string;
  email: string;
  telefono?: string;
  role: 'CLIENTE' | 'ADMIN' | string;
  status?: number;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  role: string;
}

export interface RegisterRequest {
  nombre: string;
  email: string;
  telefono?: string;
  password: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
}
