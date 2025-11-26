/**
 * Store de autenticación usando Zustand
 * Maneja el estado global del usuario autenticado
 */

import { create } from 'zustand';
import { Usuario } from '../types';
import { authService } from '../services/authService';

interface AuthState {
    user: Usuario | null;
    isLoading: boolean;
    error: string | null;

    // Actions
    setUser: (user: Usuario | null) => void;
    loadUser: () => Promise<void>;
    logout: () => void;
    clearError: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
    user: null,
    isLoading: false,
    error: null,

    setUser: (user) => set({ user, error: null }),

    loadUser: async () => {
        if (!authService.isAuthenticated()) {
            set({ user: null, isLoading: false });
            return;
        }

        set({ isLoading: true, error: null });
        try {
            const user = await authService.getProfile();
            set({ user, isLoading: false });
        } catch (error) {
            console.error('Error loading user:', error);
            set({ user: null, isLoading: false, error: 'Error al cargar el perfil' });
            authService.logout();
        }
    },

    logout: () => {
        authService.logout();
        set({ user: null, error: null });
    },

    clearError: () => set({ error: null }),
}));
