/**
 * Configuración de URLs de los microservicios
 * En desarrollo apuntan a localhost, en producción se pueden configurar vía variables de entorno
 */

export const API_CONFIG = {
    IAM: import.meta.env.VITE_IAM_URL || 'http://localhost:8010',
    CATALOGO: import.meta.env.VITE_CATALOGO_URL || 'http://localhost:8020',
    PROVEEDORES: import.meta.env.VITE_PROVEEDORES_URL || 'http://localhost:8030',
    CONTRATACION: import.meta.env.VITE_CONTRATACION_URL || 'http://localhost:8040',
};

export const APP_CONFIG = {
    APP_NAME: 'Eventos Perú',
    VERSION: '1.0.0',
    TOKEN_KEY: 'eventos_peru_token',
};
