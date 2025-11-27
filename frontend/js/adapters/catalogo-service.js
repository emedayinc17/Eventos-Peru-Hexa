const CatalogoService = {
    getTiposEvento: async () => {
        const url = `${Config.API_URLS.CATALOGO}/v1/catalogo/tipos`;
        return await HttpAdapter.get(url);
    },

    getPaquetes: async (tipoEventoId = null) => {
        let url = `${Config.API_URLS.CATALOGO}/v1/catalogo/paquetes`;
        if (tipoEventoId) {
            url += `?tipo_evento_id=${tipoEventoId}`;
        }
        return await HttpAdapter.get(url);
    },

    getById: async (id) => {
        const url = `${Config.API_URLS.CATALOGO}/v1/catalogo/paquetes/${id}`;
        return await HttpAdapter.get(url);
    },

    create: async (data) => {
        const url = `${Config.API_URLS.CATALOGO}/v1/catalogo/paquetes`;
        return await HttpAdapter.post(url, data);
    },

    update: async (id, data) => {
        const url = `${Config.API_URLS.CATALOGO}/v1/catalogo/paquetes/${id}`;
        return await HttpAdapter.put(url, data);
    },

    delete: async (id) => {
        const url = `${Config.API_URLS.CATALOGO}/v1/catalogo/paquetes/${id}`;
        return await HttpAdapter.delete(url);
    }
};
