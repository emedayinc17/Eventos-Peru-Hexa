/**
 * Custom hook para autenticación
 */

import { useAuthStore } from '../stores/authStore';
import { authService } from '../services/authService';
import { LoginCredentials, RegisterData } from '../types';
import { useState } from 'react';

export const useAuth = () => {
    const { user, isLoading, error, setUser, loadUser, logout, clearError } = useAuthStore();
    const [loginLoading, setLoginLoading] = useState(false);
    const [registerLoading, setRegisterLoading] = useState(false);

    const login = async (credentials: LoginCredentials) => {
        setLoginLoading(true);
        clearError();
        try {
            await authService.login(credentials);
            await loadUser();
            return true;
        } catch (error: any) {
            console.error('Login error:', error);
            throw new Error(error.response?.data?.detail || 'Error al iniciar sesión');
        } finally {
            setLoginLoading(false);
        }
    };

    const register = async (data: RegisterData) => {
        setRegisterLoading(true);
        clearError();
        try {
            await authService.register(data);
            await loadUser();
            return true;
        } catch (error: any) {
            console.error('Register error:', error);
            throw new Error(error.response?.data?.detail || 'Error al registrarse');
        } finally {
            setRegisterLoading(false);
        }
    };

    const isAuthenticated = () => {
        return !!user;
    };

    const isAdmin = () => {
        return user?.rol === 'ADMIN';
    };

    return {
        user,
        isLoading: isLoading || loginLoading || registerLoading,
        error,
        login,
        register,
        logout,
        loadUser,
        isAuthenticated,
        isAdmin,
    };
};
