const AuthService = {
    login: async (email, password) => {
        const url = `${Config.API_URLS.IAM}/auth/login`;
        const response = await HttpAdapter.post(url, { email, password });

        // El backend devuelve { access_token, token_type, user: {...} }
        // Si no devuelve user, deberíamos hacer un fetch a /me

        if (response.access_token) {
            // Decodificar token o obtener usuario si no viene en la respuesta
            // Para este MVP asumimos que necesitamos llamar a /me si el usuario no viene
            SessionManager.setSession(response.access_token, null); // Guardamos token temporalmente

            const user = await AuthService.getProfile();
            SessionManager.setSession(response.access_token, user); // Guardamos completo

            return user;
        }
        throw new Error('Respuesta de login inválida');
    },

    register: async (nombre, email, password) => {
        const url = `${Config.API_URLS.IAM}/auth/register`;
        return await HttpAdapter.post(url, { nombre, email, password });
    },

    getProfile: async () => {
        const url = `${Config.API_URLS.IAM}/me`;
        return await HttpAdapter.get(url);
    }
};
