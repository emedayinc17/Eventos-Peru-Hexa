#!/usr/bin/env python3
"""Verifica reservas del proveedor de prueba en contratación"""
from sqlalchemy import create_engine, text

# Credenciales del servicio de contratación
engine = create_engine('mysql+pymysql://app_contratacion:Contrata_2025@localhost/ev_contratacion')
conn = engine.connect()

# Reservas del proveedor de prueba
result = conn.execute(text("""
    SELECT id, item_pedido_id, proveedor_id, status, inicio, fin, hold_id
    FROM reserva
    WHERE proveedor_id = 'cccccccc-3333-4444-5555-cccccccccccc'
    ORDER BY created_at DESC
    LIMIT 10
"""))

reservas = result.mappings().all()
print(f"\n=== RESERVAS DEL PROVEEDOR (Total: {len(reservas)}) ===\n")

for r in reservas:
    status_name = {0: "PENDIENTE", 1: "CONFIRMADA", 2: "CANCELADA"}.get(r['status'], f"UNKNOWN({r['status']})")
    print(f"ID: {r['id'][:8]}...")
    print(f"  Item: {r['item_pedido_id'][:8]}...")
    print(f"  Status: {r['status']} ({status_name})")
    print(f"  Rango: {r['inicio']} → {r['fin']}")
    print(f"  Hold ID: {r['hold_id']}")
    print()

conn.close()
