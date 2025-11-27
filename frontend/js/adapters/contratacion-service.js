const ContratacionService = {
    getMisPedidos: async () => {
        const url = `${Config.API_URLS.CONTRATACION}/pedidos/mios`;
        const response = await HttpAdapter.get(url);
        // Backend returns { items: [...] }
        return response.items || response;
    },

    crearPedido: async (pedidoData) => {
        const url = `${Config.API_URLS.CONTRATACION}/pedidos`;
        return await HttpAdapter.post(url, pedidoData);
    },

    getAllPedidos: async () => {
        const url = `${Config.API_URLS.CONTRATACION}/admin/pedidos`;
        const response = await HttpAdapter.get(url);
        // Backend returns { items: [...], total: ... }
        return response.items || response;
    },

    getDetallePedido: async (pedidoId) => {
        const url = `${Config.API_URLS.CONTRATACION}/pedidos/${pedidoId}`;
        return await HttpAdapter.get(url);
    }
};
