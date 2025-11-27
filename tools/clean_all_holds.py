#!/usr/bin/env python3
"""Elimina TODOS los holds del proveedor de prueba para resetear disponibilidad"""
from sqlalchemy import create_engine, text

engine = create_engine('mysql+pymysql://app_proveedores:Proveedores_2025@localhost/ev_proveedores')
conn = engine.connect()

# Eliminar todos los holds
result = conn.execute(text("""
    DELETE FROM reserva_temporal 
    WHERE proveedor_id = 'cccccccc-3333-4444-5555-cccccccccccc'
"""))
conn.commit()

print(f"✅ Eliminados {result.rowcount} holds del proveedor de prueba")
print("El proveedor ahora está completamente disponible")

conn.close()
