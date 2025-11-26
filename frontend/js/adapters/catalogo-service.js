const CatalogoService = {
    getPaquetes: async () => {
        const url = `${Config.API_URLS.CATALOGO}/paquetes`;
        return await HttpAdapter.get(url);
    },

    getPaqueteById: async (id) => {
        const url = `${Config.API_URLS.CATALOGO}/paquetes/${id}`;
        return await HttpAdapter.get(url);
    }
};
