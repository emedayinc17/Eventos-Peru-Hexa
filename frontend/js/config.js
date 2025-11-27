const Config = {
    // En desarrollo local, usamos localhost. En producción (K8s), estas variables se inyectarán o se usará un configmap.
    // Para este MVP simple, detectaremos si estamos en localhost o usamos nombres de servicio.

    API_URLS: {
        IAM: (window.location.hostname === 'localhost' || window.location.protocol === 'file:') ? 'http://localhost:8010/iam' : '/api/iam',
        CATALOGO: (window.location.hostname === 'localhost' || window.location.protocol === 'file:') ? 'http://localhost:8020/catalogo' : '/api/catalogo',
        PROVEEDORES: (window.location.hostname === 'localhost' || window.location.protocol === 'file:') ? 'http://localhost:8030/proveedores/v1' : '/api/proveedores/v1',
        CONTRATACION: (window.location.hostname === 'localhost' || window.location.protocol === 'file:') ? 'http://localhost:8040/contratacion' : '/api/contratacion'
    },

    ROUTES: {
        LOGIN: '/index.html',
        DASHBOARD: '/dashboard.html',
        REGISTER: '/register.html'
    }
};

// Congelar para evitar modificaciones accidentales
Object.freeze(Config);
