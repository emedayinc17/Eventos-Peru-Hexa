const ProveedoresService = {
    getAll: async () => {
        const url = `${Config.API_URLS.PROVEEDORES}/proveedores`;
        return await HttpAdapter.get(url);
    },

    getById: async (id) => {
        const url = `${Config.API_URLS.PROVEEDORES}/proveedores/${id}`;
        return await HttpAdapter.get(url);
    },

    create: async (data) => {
        const url = `${Config.API_URLS.PROVEEDORES}/proveedores`;
        return await HttpAdapter.post(url, data);
    },

    update: async (id, data) => {
        const url = `${Config.API_URLS.PROVEEDORES}/proveedores/${id}`;
        return await HttpAdapter.put(url, data);
    },

    delete: async (id) => {
        const url = `${Config.API_URLS.PROVEEDORES}/proveedores/${id}`;
        return await HttpAdapter.delete(url);
    }
};
