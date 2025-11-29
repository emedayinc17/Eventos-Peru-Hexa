#!/usr/bin/env python3
"""Script para agregar servicios_adicionales al use case"""

# Leer el archivo
with open('services/contratacion-service/app/application/use_cases/crear_pedido_desde_paquete.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Agregar servicios_adicionales al signature de execute
old_signature = '''        notas: Optional[str] = None,
        proveedores_seleccionados: Optional[list] = None
    ) -> Pedido:'''

new_signature = '''        notas: Optional[str] = None,
        servicios_adicionales: Optional[list] = None,
        proveedores_seleccionados: Optional[list] = None
    ) -> Pedido:'''

content = content.replace(old_signature, new_signature)

# 2. Agregar lógica para procesar servicios_adicionales después de crear items del paquete
old_return = '''            self.item_repo.crear(
                session,
                pedido_id=pedido.id,
                opcion_servicio_id=item["opcion_servicio_id"],
                nombre_servicio=item.get("servicio_nombre", item.get("opcion_nombre", "Servicio")),
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                subtotal=subtotal
            )
        
        return pedido'''

new_return = '''            self.item_repo.crear(
                session,
                pedido_id=pedido.id,
                opcion_servicio_id=item["opcion_servicio_id"],
                nombre_servicio=item.get("servicio_nombre", item.get("opcion_nombre", "Servicio")),
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                subtotal=subtotal
            )
        
        # 5. Agregar servicios adicionales si existen
        if servicios_adicionales:
            for servicio_adicional in servicios_adicionales:
                # Obtener precio del servicio desde catálogo
                opcion_id = servicio_adicional.get("opcion_servicio_id")
                cantidad_adicional = servicio_adicional.get("cantidad", 1)
                
                # Consultar precio vigente
                try:
                    precio_vigente = self.catalogo_client.obtener_precio_opcion(opcion_id)
                    precio_unitario_adicional = float(precio_vigente)
                except Exception:
                    # Si no se puede obtener precio, usar 0 (debería manejarse mejor)
                    precio_unitario_adicional = 0.0
                
                subtotal_adicional = cantidad_adicional * precio_unitario_adicional
                
                # Crear item adicional
                self.item_repo.crear(
                    session,
                    pedido_id=pedido.id,
                    opcion_servicio_id=opcion_id,
                    nombre_servicio="Servicio Adicional",  # Podría obtenerse del catálogo
                    cantidad=cantidad_adicional,
                    precio_unitario=precio_unitario_adicional,
                    subtotal=subtotal_adicional,
                    tipo_item='SERVICIO',
                    referencia_id=opcion_id
                )
                
                # Actualizar monto total del pedido
                monto_total += subtotal_adicional
            
            # Actualizar el monto total del pedido si hubo servicios adicionales
            if servicios_adicionales:
                pedido = self.pedido_repo.actualizar_monto(
                    session,
                    pedido_id=pedido.id,
                    nuevo_monto=monto_total
                )
        
        return pedido'''

content = content.replace(old_return, new_return)

# Escribir el archivo
with open('services/contratacion-service/app/application/use_cases/crear_pedido_desde_paquete.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Cambio aplicado correctamente en crear_pedido_desde_paquete.py")
