#!/usr/bin/env python3
"""Script para agregar servicios_adicionales al router"""

# Leer el archivo
with open('services/contratacion-service/app/entrypoints/fastapi/router.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Buscar y reemplazar la sección de params para paquete
old_params = '''        # Convertir proveedores_seleccionados a dict si existe
        proveedores = None
        if payload.proveedores_seleccionados:
            proveedores = [p.dict() for p in payload.proveedores_seleccionados]
        
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
            # Note: use case doesn't accept request_id/correlation_id
        }'''

new_params = '''        # Convertir proveedores_seleccionados a dict si existe
        proveedores = None
        if payload.proveedores_seleccionados:
            proveedores = [p.dict() for p in payload.proveedores_seleccionados]
        
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
            "servicios_adicionales": servicios_adicionales,
            "proveedores_seleccionados": proveedores,
            # Note: use case doesn't accept request_id/correlation_id
        }'''

content = content.replace(old_params, new_params)

# Escribir el archivo
with open('services/contratacion-service/app/entrypoints/fastapi/router.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Cambio aplicado correctamente en router.py")
