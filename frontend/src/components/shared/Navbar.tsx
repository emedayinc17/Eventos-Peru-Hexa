/**
 * Componente de navegación principal
 */

import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

export const Navbar = () => {
    const { user, logout, isAdmin } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <nav className="bg-primary-600 text-white shadow-lg">
            <div className="container mx-auto px-4">
                <div className="flex items-center justify-between h-16">
                    {/* Logo */}
                    <Link to="/" className="text-2xl font-bold hover:text-primary-100 transition-colors">
                        Eventos Perú
                    </Link>

                    {/* Navigation Links */}
                    <div className="flex items-center space-x-6">
                        {user ? (
                            <>
                                <Link to="/dashboard" className="hover:text-primary-100 transition-colors">
                                    Dashboard
                                </Link>
                                <Link to="/catalogo" className="hover:text-primary-100 transition-colors">
                                    Catálogo
                                </Link>
                                <Link to="/mis-pedidos" className="hover:text-primary-100 transition-colors">
                                    Mis Pedidos
                                </Link>
                                {isAdmin() && (
                                    <Link to="/admin" className="hover:text-primary-100 transition-colors">
                                        Admin
                                    </Link>
                                )}

                                {/* User Menu */}
                                <div className="flex items-center space-x-4 border-l border-primary-500 pl-6">
                                    <div className="text-sm">
                                        <div className="font-medium">{user.nombre_completo}</div>
                                        <div className="text-primary-200 text-xs">{user.rol}</div>
                                    </div>
                                    <button
                                        onClick={handleLogout}
                                        className="bg-primary-700 hover:bg-primary-800 px-4 py-2 rounded-lg transition-colors"
                                    >
                                        Salir
                                    </button>
                                </div>
                            </>
                        ) : (
                            <>
                                <Link to="/login" className="hover:text-primary-100 transition-colors">
                                    Iniciar Sesión
                                </Link>
                                <Link
                                    to="/register"
                                    className="bg-white text-primary-600 px-4 py-2 rounded-lg font-semibold hover:bg-primary-50 transition-colors"
                                >
                                    Registrarse
                                </Link>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </nav>
    );
};
