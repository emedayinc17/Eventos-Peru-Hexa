/**
 * Página de Dashboard
 */

import { useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { Loading } from '../components/shared/Loading';
import { Link } from 'react-router-dom';

export const DashboardPage = () => {
    const { user, isLoading } = useAuth();

    if (isLoading) {
        return <Loading message="Cargando dashboard..." />;
    }

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
            <div className="container mx-auto px-4 py-8">
                {/* Welcome Section */}
                <div className="mb-8">
                    <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
                        ¡Bienvenido, {user?.nombre_completo}!
                    </h1>
                    <p className="text-gray-600 dark:text-gray-400">
                        Gestiona tus eventos de manera profesional
                    </p>
                </div>

                {/* Quick Actions */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {/* Catálogo */}
                    <Link to="/catalogo" className="card hover:shadow-lg transition-shadow cursor-pointer group">
                        <div className="flex items-center mb-4">
                            <div className="bg-primary-100 dark:bg-primary-900 p-3 rounded-lg group-hover:bg-primary-200 transition-colors">
                                <svg className="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                                </svg>
                            </div>
                        </div>
                        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                            Explorar Catálogo
                        </h3>
                        <p className="text-gray-600 dark:text-gray-400">
                            Descubre nuestros servicios y paquetes para eventos
                        </p>
                    </Link>

                    {/* Mis Pedidos */}
                    <Link to="/mis-pedidos" className="card hover:shadow-lg transition-shadow cursor-pointer group">
                        <div className="flex items-center mb-4">
                            <div className="bg-green-100 dark:bg-green-900 p-3 rounded-lg group-hover:bg-green-200 transition-colors">
                                <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                                </svg>
                            </div>
                        </div>
                        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                            Mis Pedidos
                        </h3>
                        <p className="text-gray-600 dark:text-gray-400">
                            Revisa y gestiona tus cotizaciones y reservas
                        </p>
                    </Link>

                    {/* Crear Pedido */}
                    <Link to="/catalogo" className="card hover:shadow-lg transition-shadow cursor-pointer group bg-gradient-to-br from-primary-50 to-primary-100 dark:from-primary-900/20 dark:to-primary-800/20 border-2 border-primary-200 dark:border-primary-700">
                        <div className="flex items-center mb-4">
                            <div className="bg-primary-600 p-3 rounded-lg group-hover:bg-primary-700 transition-colors">
                                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                                </svg>
                            </div>
                        </div>
                        <h3 className="text-xl font-semibold text-primary-900 dark:text-primary-100 mb-2">
                            Nuevo Pedido
                        </h3>
                        <p className="text-primary-700 dark:text-primary-300">
                            Comienza a planificar tu evento ahora
                        </p>
                    </Link>
                </div>

                {/* Stats Section (if admin) */}
                {user?.rol === 'ADMIN' && (
                    <div className="mt-8">
                        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                            Panel de Administración
                        </h2>
                        <Link to="/admin" className="card hover:shadow-lg transition-shadow cursor-pointer inline-block">
                            <p className="text-gray-600 dark:text-gray-400">
                                Acceder al panel de administración →
                            </p>
                        </Link>
                    </div>
                )}
            </div>
        </div>
    );
};
