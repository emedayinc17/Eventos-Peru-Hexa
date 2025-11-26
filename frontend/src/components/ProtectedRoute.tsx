/**
 * Componente de ruta protegida
 * Redirige al login si el usuario no está autenticado
 */

import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { Loading } from './shared/Loading';

interface ProtectedRouteProps {
    children: React.ReactNode;
    requireAdmin?: boolean;
}

export const ProtectedRoute = ({ children, requireAdmin = false }: ProtectedRouteProps) => {
    const { isLoading, isAuthenticated, isAdmin } = useAuth();

    if (isLoading) {
        return <Loading message="Verificando autenticación..." />;
    }

    if (!isAuthenticated()) {
        return <Navigate to="/login" replace />;
    }

    if (requireAdmin && !isAdmin()) {
        return <Navigate to="/dashboard" replace />;
    }

    return <>{children}</>;
};
