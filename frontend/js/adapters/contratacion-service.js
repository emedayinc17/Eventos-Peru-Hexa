const ContratacionService = {
    getMisPedidos: async () => {
        const url = `${Config.API_URLS.CONTRATACION}/pedidos/mis-pedidos`;
        return await HttpAdapter.get(url);
    },

    crearPedido: async (pedidoData) => {
        const url = `${Config.API_URLS.CONTRATACION}/pedidos`;
        return await HttpAdapter.post(url, pedidoData);
    },

    getAllPedidos: async () => {
        const url = `${Config.API_URLS.CONTRATACION}/pedidos`;
        return await HttpAdapter.get(url);
    }
};
