const Config = {
    // En desarrollo local, usamos localhost. En producción (K8s), estas variables se inyectarán o se usará un configmap.
    // Para este MVP simple, detectaremos si estamos en localhost o usamos nombres de servicio.

    API_URLS: {
        IAM: window.location.hostname === 'localhost' ? 'http://localhost:8010' : '/api/iam',
        CATALOGO: window.location.hostname === 'localhost' ? 'http://localhost:8020' : '/api/catalogo',
        PROVEEDORES: window.location.hostname === 'localhost' ? 'http://localhost:8030' : '/api/proveedores',
        CONTRATACION: window.location.hostname === 'localhost' ? 'http://localhost:8040' : '/api/contratacion'
    },

    ROUTES: {
        LOGIN: '/index.html',
        DASHBOARD: '/dashboard.html',
        REGISTER: '/register.html'
    }
};

// Congelar para evitar modificaciones accidentales
Object.freeze(Config);
