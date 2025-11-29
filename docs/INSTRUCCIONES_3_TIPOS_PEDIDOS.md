# ============================================
# INSTRUCCIONES PARA SOPORTAR 3 TIPOS DE PEDIDOS
# ============================================

## CAMBIOS NECESARIOS:

### 1. BACKEND - Schema (schemas.py)
### Archivo: services/contratacion-service/app/entrypoints/fastapi/schemas.py
### Línea 14-25

# ANTES:
class CrearPedidoDesdePaquete(BaseModel):
    paquete_id: str
    tipo_evento_id: str
    fecha_evento: date
    hora_inicio: str  # HH:MM format
    hora_fin: Optional[str] = None  # HH:MM format
    num_personas: int = Field(ge=1)
    ubicacion: str
    notas: Optional[str] = None
    proveedores_seleccionados: Optional[List[ProveedorSeleccionado]] = None
    request_id: Optional[str] = None
    correlation_id: Optional[str] = None

# DESPUÉS (agregar línea 23):
class CrearPedidoDesdePaquete(BaseModel):
    paquete_id: str
    tipo_evento_id: str
    fecha_evento: date
    hora_inicio: str  # HH:MM format
    hora_fin: Optional[str] = None  # HH:MM format
    num_personas: int = Field(ge=1)
    ubicacion: str
    notas: Optional[str] = None
    servicios_adicionales: Optional[List['ItemCustom']] = None  # NUEVO
    proveedores_seleccionados: Optional[List[ProveedorSeleccionado]] = None
    request_id: Optional[str] = None
    correlation_id: Optional[str] = None


### 2. BACKEND - Use Case (crear_pedido_desde_paquete.py)
### Archivo: services/contratacion-service/app/application/use_cases/crear_pedido_desde_paquete.py
### Buscar la función execute() y agregar lógica para servicios_adicionales

# Después de crear los items del paquete (alrededor de línea 80-90), AGREGAR:

        # NUEVO: Agregar servicios adicionales si existen
        if servicios_adicionales:
            for servicio_adicional in servicios_adicionales:
                # Obtener precio del servicio
                precio_servicio = self.catalogo_client.obtener_precio_opcion(
                    servicio_adicional['opcion_servicio_id']
                )
                
                # Crear item adicional
                item_adicional = self.item_repo.crear(
                    session,
                    pedido_id=pedido.id,
                    opcion_servicio_id=servicio_adicional['opcion_servicio_id'],
                    nombre_servicio=f"Servicio Adicional",  # Obtener nombre real del catálogo
                    cantidad=servicio_adicional.get('cantidad', 1),
                    precio_unitario=precio_servicio,
                    subtotal=precio_servicio * servicio_adicional.get('cantidad', 1),
                    tipo_item='SERVICIO',
                    referencia_id=servicio_adicional['opcion_servicio_id'],
                )
                
                # Actualizar monto total
                monto_total += item_adicional.subtotal


### 3. BACKEND - Router (router.py)
### Archivo: services/contratacion-service/app/entrypoints/fastapi/router.py
### Buscar la función crear_pedido() y pasar servicios_adicionales al use case

# En la sección donde se crea el pedido desde paquete (alrededor de línea 50-70):

# ANTES:
        params = {
            "cliente_id": cliente_id,
            "paquete_id": payload.paquete_id,
            "tipo_evento_id": payload.tipo_evento_id,
            "num_personas": payload.num_personas,
            "fecha_evento": fecha_dt,
            "hora_inicio": payload.hora_inicio,
            "hora_fin": payload.hora_fin,
            "ubicacion": payload.ubicacion,
            "notas": payload.notas,
            "proveedores_seleccionados": proveedores,
        }

# DESPUÉS (agregar servicios_adicionales):
        # Convertir servicios_adicionales a dict si existe
        servicios_adicionales = None
        if payload.servicios_adicionales:
            servicios_adicionales = [s.dict() for s in payload.servicios_adicionales]
        
        params = {
            "cliente_id": cliente_id,
            "paquete_id": payload.paquete_id,
            "tipo_evento_id": payload.tipo_evento_id,
            "num_personas": payload.num_personas,
            "fecha_evento": fecha_dt,
            "hora_inicio": payload.hora_inicio,
            "hora_fin": payload.hora_fin,
            "ubicacion": payload.ubicacion,
            "notas": payload.notas,
            "servicios_adicionales": servicios_adicionales,  # NUEVO
            "proveedores_seleccionados": proveedores,
        }


### 4. FRONTEND - CreateOrderWizard.vue
### Archivo: frontend/src/views/client/CreateOrderWizard.vue
### Líneas 564-588

# REEMPLAZAR la función confirmOrder completa con:

const confirmOrder = async () => {
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
};


## RESUMEN DE LOS 3 CASOS:

1. **Pedido con Paquete**: 
   - `paquete_id` presente
   - `servicios_adicionales` vacío o null
   - Backend crea items del paquete

2. **Pedido Custom (sin paquete)**:
   - `paquete_id` null
   - `items[]` con servicios seleccionados
   - Backend crea items custom

3. **Pedido con Paquete + Extras**:
   - `paquete_id` presente
   - `servicios_adicionales[]` con servicios extras
   - Backend crea items del paquete + items adicionales
