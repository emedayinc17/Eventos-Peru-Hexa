const HttpAdapter = {
    request: async (url, method = 'GET', body = null) => {
        const { token } = SessionManager.getSession();

        const headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const config = {
            method,
            headers
        };

        if (body) {
            config.body = JSON.stringify(body);
        }

        try {
            const response = await fetch(url, config);

            // Manejo de 401 (Token expirado o inválido)
            if (response.status === 401) {
                SessionManager.clearSession();
                window.location.href = Config.ROUTES.LOGIN;
                throw new Error('Sesión expirada');
            }

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || data.message || 'Error en la petición');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    get: (url) => HttpAdapter.request(url, 'GET'),
    post: (url, body) => HttpAdapter.request(url, 'POST', body),
    put: (url, body) => HttpAdapter.request(url, 'PUT', body),
    delete: (url) => HttpAdapter.request(url, 'DELETE')
};
