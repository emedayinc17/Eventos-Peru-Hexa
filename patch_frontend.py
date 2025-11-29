#!/usr/bin/env python3
"""Script para actualizar CreateOrderWizard.vue"""

# Leer el archivo
with open('frontend/src/views/client/CreateOrderWizard.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# Reemplazar la función confirmOrder
old_function = '''const confirmOrder = async () => {
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
};'''

new_function = '''const confirmOrder = async () => {
  try {
    submitting.value = true;
    
    let orderData: any;
    
    if (draft.value.paquete_id) {
      // CASO 1 y 3: Con paquete (con o sin servicios adicionales)
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
      
      // Si hay servicios adicionales, agregarlos
      if (draft.value.servicios_adicionales && draft.value.servicios_adicionales.length > 0) {
        orderData.servicios_adicionales = draft.value.servicios_adicionales.map((servicioId: number) => ({
          opcion_servicio_id: String(servicioId),
          cantidad: 1
        }));
      }
    } else {
      // CASO 2: Sin paquete (pedido custom)
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
    
    ordersStore.clearDraft();
    showSuccessModal.value = true;
  } catch (error: any) {
    ui.showToast('Error al crear el pedido: ' + (error.response?.data?.detail || error.message), 'error', 6000);
  } finally {
    submitting.value = false;
  }
};'''

content = content.replace(old_function, new_function)

# Escribir el archivo
with open('frontend/src/views/client/CreateOrderWizard.vue', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Cambio aplicado correctamente en CreateOrderWizard.vue")
