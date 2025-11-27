#!/usr/bin/env python3
"""Elimina TODAS las reservas del proveedor de prueba"""
from sqlalchemy import create_engine, text

engine = create_engine('mysql+pymysql://app_contratacion:Contrata_2025@localhost/ev_contratacion')
conn = engine.connect()

# Eliminar todas las reservas
result = conn.execute(text("""
    DELETE FROM reserva 
    WHERE proveedor_id = 'cccccccc-3333-4444-5555-cccccccccccc'
"""))
conn.commit()

print(f"✅ Eliminadas {result.rowcount} reservas del proveedor de prueba")
print("El proveedor ahora está completamente disponible")

conn.close()
