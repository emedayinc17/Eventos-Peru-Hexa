/**
 * INSTRUCCIONES PARA CORREGIR CreateOrderWizard.vue
 * 
 * Archivo: e:\eventos-peru-hexagonal\frontend\src\views\client\CreateOrderWizard.vue
 * Líneas: 564-588
 * 
 * REEMPLAZAR LA FUNCIÓN confirmOrder COMPLETA
 */

// ============================================
// CÓDIGO ACTUAL (LÍNEAS 564-588) - ELIMINAR
// ============================================
const confirmOrder = async () => {
    try {
        submitting.value = true;

        const orderData = {
            tipo_evento_id: draft.value.tipo_evento_id!,
            fecha_evento: draft.value.fecha_evento!,
            num_invitados: draft.value.num_invitados!,
            paquete_id: draft.value.paquete_id,
            servicios_adicionales: draft.value.servicios_adicionales,
            comentarios: draft.value.comentarios,
        };

        const createdOrder = await ordersStore.createPedido(orderData);
        createdOrderId.value = createdOrder.id;

        // Clear draft and show success
        ordersStore.clearDraft();
        showSuccessModal.value = true;
    } catch (error: any) {
        ui.showToast('Error al crear el pedido: ' + (error.response?.data?.detail || error.message), 'error', 6000);
    } finally {
        submitting.value = false;
    }
};

// ============================================
// CÓDIGO NUEVO - COPIAR Y PEGAR
// ============================================
const confirmOrder = async () => {
    try {
        submitting.value = true;

        let orderData: any;

        // Si tiene paquete, usar el endpoint de paquete
        if (draft.value.paquete_id) {
            orderData = {
                tipo_evento_id: draft.value.tipo_evento_id!,
                fecha_evento: draft.value.fecha_evento!,
                num_personas: draft.value.num_invitados!,
                hora_inicio: '10:00',
                hora_fin: '18:00',
                ubicacion: 'Por definir',
                paquete_id: draft.value.paquete_id,
                notas: draft.value.comentarios,
            };
        } else {
            // Sin paquete: crear pedido custom con items
            // Convertir servicios_adicionales a formato items
            const items = draft.value.servicios_adicionales.map((servicioId: number) => ({
                opcion_servicio_id: String(servicioId),
                cantidad: 1
            }));

            orderData = {
                tipo_evento_id: draft.value.tipo_evento_id!,
                fecha_evento: draft.value.fecha_evento!,
                num_personas: draft.value.num_invitados!,
                hora_inicio: '10:00',
                hora_fin: '18:00',
                ubicacion: 'Por definir',
                items: items,
            };
        }

        const createdOrder = await ordersStore.createPedido(orderData);
        createdOrderId.value = createdOrder.id;

        // Clear draft and show success
        ordersStore.clearDraft();
        showSuccessModal.value = true;
    } catch (error: any) {
        ui.showToast('Error al crear el pedido: ' + (error.response?.data?.detail || error.message), 'error', 6000);
    } finally {
        submitting.value = false;
    }
};

/**
 * EXPLICACIÓN:
 * 
 * 1. Si el usuario selecciona un PAQUETE:
 *    - Envía: paquete_id, num_personas, hora_inicio, hora_fin, ubicacion, notas
 *    - El backend crea automáticamente los items del paquete
 * 
 * 2. Si el usuario NO selecciona paquete (servicios a la carta):
 *    - Convierte servicios_adicionales a formato items[]
 *    - Envía: items[], num_personas, hora_inicio, hora_fin, ubicacion
 *    - El backend crea un pedido custom con esos items
 * 
 * CAMBIOS CLAVE:
 * - num_invitados → num_personas (campo correcto del backend)
 * - comentarios → notas (campo correcto del backend)
 * - Agregados: hora_inicio, hora_fin, ubicacion (campos requeridos)
 * - servicios_adicionales → items[] (solo para pedidos sin paquete)
 */
