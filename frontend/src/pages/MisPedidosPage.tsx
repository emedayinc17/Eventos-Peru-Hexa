/**
 * Página de Mis Pedidos
 */

import { useEffect } from 'react';
import { usePedidos } from '../hooks/usePedidos';
import { Loading } from '../components/shared/Loading';
import { ErrorAlert } from '../components/shared/ErrorAlert';
import type { Pedido } from '../types';

const getEstadoBadgeClass = (estado: string) => {
    const classes = {
        BORRADOR: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
        COTIZADO: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
        RESERVADO: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
        CONFIRMADO: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
        CANCELADO: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    };
    return classes[estado as keyof typeof classes] || classes.BORRADOR;
};

export const MisPedidosPage = () => {
    const { pedidos, isLoading, error, loadMisPedidos } = usePedidos();

    useEffect(() => {
        loadMisPedidos();
    }, []);

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('es-PE', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
        });
    };

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
            <div className="container mx-auto px-4 py-8">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
                        Mis Pedidos
                    </h1>
                    <p className="text-gray-600 dark:text-gray-400">
                        Gestiona tus cotizaciones y reservas
                    </p>
                </div>

                {/* Error */}
                {error && (
                    <div className="mb-6">
                        <ErrorAlert message={error} />
                    </div>
                )}

                {/* Loading */}
                {isLoading && <Loading message="Cargando pedidos..." />}

                {/* Pedidos List */}
                {!isLoading && pedidos.length > 0 && (
                    <div className="space-y-4">
                        {pedidos.map((pedido: Pedido) => (
                            <div key={pedido.id} className="card hover:shadow-lg transition-shadow">
                                <div className="flex items-start justify-between">
                                    {/* Info */}
                                    <div className="flex-1">
                                        <div className="flex items-center space-x-3 mb-2">
                                            <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                                                Pedido #{pedido.id.slice(0, 8)}
                                            </h3>
                                            <span
                                                className={`px-3 py-1 rounded-full text-xs font-semibold ${getEstadoBadgeClass(
                                                    pedido.estado
                                                )}`}
                                            >
                                                {pedido.estado}
                                            </span>
                                        </div>

                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                                            <div>
                                                <p className="text-sm text-gray-500 dark:text-gray-400">
                                                    Fecha de creación
                                                </p>
                                                <p className="text-gray-900 dark:text-white font-medium">
                                                    {formatDate(pedido.created_at)}
                                                </p>
                                            </div>

                                            {pedido.fecha_evento && (
                                                <div>
                                                    <p className="text-sm text-gray-500 dark:text-gray-400">
                                                        Fecha del evento
                                                    </p>
                                                    <p className="text-gray-900 dark:text-white font-medium">
                                                        {formatDate(pedido.fecha_evento)}
                                                    </p>
                                                </div>
                                            )}

                                            {pedido.lugar_evento && (
                                                <div>
                                                    <p className="text-sm text-gray-500 dark:text-gray-400">
                                                        Lugar
                                                    </p>
                                                    <p className="text-gray-900 dark:text-white font-medium">
                                                        {pedido.lugar_evento}
                                                    </p>
                                                </div>
                                            )}

                                            <div>
                                                <p className="text-sm text-gray-500 dark:text-gray-400">
                                                    Monto total
                                                </p>
                                                <p className="text-2xl font-bold text-primary-600">
                                                    S/ {pedido.monto_total.toFixed(2)}
                                                </p>
                                            </div>
                                        </div>

                                        {/* Items */}
                                        {pedido.items && pedido.items.length > 0 && (
                                            <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                                                <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                                    Items del pedido:
                                                </p>
                                                <ul className="space-y-1">
                                                    {pedido.items.map((item) => (
                                                        <li
                                                            key={item.id}
                                                            className="text-sm text-gray-600 dark:text-gray-400"
                                                        >
                                                            • {item.servicio_nombre || 'Servicio'} -{' '}
                                                            {item.opcion_nombre || 'Opción'} (x{item.cantidad}) - S/{' '}
                                                            {(item.precio_unitario * item.cantidad).toFixed(2)}
                                                        </li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}
                                    </div>

                                    {/* Actions */}
                                    <div className="ml-4">
                                        <button className="btn-primary text-sm">
                                            Ver Detalles
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* Empty State */}
                {!isLoading && pedidos.length === 0 && (
                    <div className="text-center py-12 card">
                        <svg
                            className="mx-auto h-12 w-12 text-gray-400"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                            />
                        </svg>
                        <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
                            No tienes pedidos
                        </h3>
                        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                            Comienza creando tu primer pedido desde el catálogo.
                        </p>
                        <div className="mt-6">
                            <a href="/catalogo" className="btn-primary inline-block">
                                Explorar Catálogo
                            </a>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};
