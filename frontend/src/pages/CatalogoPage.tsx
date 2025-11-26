/**
 * Página de Catálogo
 */

import { useEffect } from 'react';
import { useCatalogo } from '../hooks/useCatalogo';
import { Loading } from '../components/shared/Loading';
import { ErrorAlert } from '../components/shared/ErrorAlert';
import type { Paquete } from '../types';
import { useNavigate } from 'react-router-dom';

export const CatalogoPage = () => {
    const { paquetes, isLoading, error, loadPaquetes } = useCatalogo();
    const navigate = useNavigate();

    useEffect(() => {
        loadPaquetes();
    }, []);

    const handleSelectPaquete = (paquete: Paquete) => {
        // Navegar a página de detalle del paquete
        navigate(`/paquete/${paquete.id}`);
    };

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
            <div className="container mx-auto px-4 py-8">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
                        Catálogo de Servicios
                    </h1>
                    <p className="text-gray-600 dark:text-gray-400">
                        Explora nuestros paquetes y servicios para tu evento
                    </p>
                </div>

                {/* Error */}
                {error && (
                    <div className="mb-6">
                        <ErrorAlert message={error} />
                    </div>
                )}

                {/* Loading */}
                {isLoading && <Loading message="Cargando catálogo..." />}

                {/* Paquetes Grid */}
                {!isLoading && paquetes.length > 0 && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {paquetes.map((paquete) => (
                            <div
                                key={paquete.id}
                                className="card hover:shadow-xl transition-all cursor-pointer group"
                                onClick={() => handleSelectPaquete(paquete)}
                            >
                                {/* Badge de estado */}
                                <div className="flex items-center justify-between mb-4">
                                    <span
                                        className={`px-3 py-1 rounded-full text-xs font-semibold ${paquete.activo
                                                ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                                                : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                                            }`}
                                    >
                                        {paquete.activo ? 'Disponible' : 'No disponible'}
                                    </span>
                                </div>

                                {/* Nombre */}
                                <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2 group-hover:text-primary-600 transition-colors">
                                    {paquete.nombre}
                                </h3>

                                {/* Descripción */}
                                <p className="text-gray-600 dark:text-gray-400 mb-4 line-clamp-3">
                                    {paquete.descripcion}
                                </p>

                                {/* Precio */}
                                <div className="mt-auto pt-4 border-t border-gray-200 dark:border-gray-700">
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm text-gray-500 dark:text-gray-400">
                                            Precio total
                                        </span>
                                        <span className="text-2xl font-bold text-primary-600">
                                            S/ {paquete.monto_total.toFixed(2)}
                                        </span>
                                    </div>
                                </div>

                                {/* CTA */}
                                <button className="w-full mt-4 btn-primary">
                                    Ver Detalles
                                </button>
                            </div>
                        ))}
                    </div>
                )}

                {/* Empty State */}
                {!isLoading && paquetes.length === 0 && (
                    <div className="text-center py-12">
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
                                d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
                            />
                        </svg>
                        <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
                            No hay paquetes disponibles
                        </h3>
                        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                            Por favor, vuelve más tarde.
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
};
