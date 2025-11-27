const UsuariosService = {
    getAll: async () => {
        const url = `${Config.API_URLS.IAM}/admin/users`;
        return await HttpAdapter.get(url);
    },

    getById: async (id) => {
        const url = `${Config.API_URLS.IAM}/admin/users/${id}`;
        return await HttpAdapter.get(url);
    },

    create: async (data) => {
        const url = `${Config.API_URLS.IAM}/admin/users`;
        return await HttpAdapter.post(url, data);
    },

    update: async (id, data) => {
        const url = `${Config.API_URLS.IAM}/admin/users/${id}`;
        return await HttpAdapter.patch(url, data); // IAM uses PATCH usually
    },

    delete: async (id) => {
        const url = `${Config.API_URLS.IAM}/admin/users/${id}`;
        return await HttpAdapter.delete(url);
    }
};
