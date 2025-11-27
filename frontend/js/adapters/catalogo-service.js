const CatalogoService = {
    getPaquetes: async () => {
        const url = `${Config.API_URLS.CATALOGO}/paquetes`;
        return await HttpAdapter.get(url);
    },

    getTiposEvento: async () => {
        const url = `${Config.API_URLS.CATALOGO}/tipos`;
        return await HttpAdapter.get(url);
    },

    getById: async (id) => {
        const url = `${Config.API_URLS.CATALOGO}/paquetes/${id}`;
        return await HttpAdapter.get(url);
    },

    create: async (data) => {
        const url = `${Config.API_URLS.CATALOGO}/paquetes`;
        return await HttpAdapter.post(url, data);
    },

    update: async (id, data) => {
        const url = `${Config.API_URLS.CATALOGO}/paquetes/${id}`;
        return await HttpAdapter.put(url, data);
    },

    delete: async (id) => {
        const url = `${Config.API_URLS.CATALOGO}/paquetes/${id}`;
        return await HttpAdapter.delete(url);
    }
};
