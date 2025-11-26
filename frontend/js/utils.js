const SessionManager = {
    TOKEN_KEY: 'eventos_peru_token',
    USER_KEY: 'eventos_peru_user',

    setSession: (token, user) => {
        localStorage.setItem(SessionManager.TOKEN_KEY, token);
        localStorage.setItem(SessionManager.USER_KEY, JSON.stringify(user));
    },

    getSession: () => {
        const token = localStorage.getItem(SessionManager.TOKEN_KEY);
        const userStr = localStorage.getItem(SessionManager.USER_KEY);
        return {
            token,
            user: userStr ? JSON.parse(userStr) : null
        };
    },

    clearSession: () => {
        localStorage.removeItem(SessionManager.TOKEN_KEY);
        localStorage.removeItem(SessionManager.USER_KEY);
    },

    isAuthenticated: () => {
        return !!localStorage.getItem(SessionManager.TOKEN_KEY);
    },

    // Redirigir si no está autenticado (Middleware simple)
    requireAuth: () => {
        if (!SessionManager.isAuthenticated()) {
            window.location.href = Config.ROUTES.LOGIN;
        }
    },

    // Redirigir si ya está autenticado (para login/register)
    redirectIfAuthenticated: () => {
        if (SessionManager.isAuthenticated()) {
            window.location.href = Config.ROUTES.DASHBOARD;
        }
    }
};

const UI = {
    showLoading: (elementId) => {
        const el = document.getElementById(elementId);
        if (el) el.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Cargando...</span></div>';
    },

    showError: (elementId, message) => {
        const el = document.getElementById(elementId);
        if (el) {
            el.innerHTML = `<div class="alert alert-danger alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>`;
            el.classList.remove('d-none');
        }
    },

    hideAlert: (elementId) => {
        const el = document.getElementById(elementId);
        if (el) el.classList.add('d-none');
    }
};
