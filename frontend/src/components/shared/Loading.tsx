/**
 * Componente de carga (spinner)
 */

export const Loading = ({ message = 'Cargando...' }: { message?: string }) => {
    return (
        <div className="flex flex-col items-center justify-center min-h-[400px]">
            <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-primary-600"></div>
            <p className="mt-4 text-gray-600 dark:text-gray-400">{message}</p>
        </div>
    );
};
