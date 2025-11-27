#!/usr/bin/env python3
"""Verifica holds activos del proveedor de prueba"""
from sqlalchemy import create_engine, text
from datetime import datetime

engine = create_engine('mysql+pymysql://app_proveedores:Proveedores_2025@localhost/ev_proveedores')
conn = engine.connect()

# Holds del proveedor de prueba
result = conn.execute(text("""
    SELECT id, proveedor_id, opcion_servicio_id, status, inicio, fin, expira_en, correlation_id
    FROM reserva_temporal 
    WHERE proveedor_id = 'cccccccc-3333-4444-5555-cccccccccccc'
    ORDER BY created_at DESC
    LIMIT 10
"""))

holds = result.mappings().all()
print(f"\n=== HOLDS DEL PROVEEDOR (Total: {len(holds)}) ===\n")

for h in holds:
    status_name = {0: "ACTIVO", 1: "CONFIRMADO", 2: "LIBERADO"}.get(h['status'], f"UNKNOWN({h['status']})")
    expirado = "EXPIRADO" if h['expira_en'] < datetime.now() else "VIGENTE"
    print(f"ID: {h['id'][:8]}...")
    print(f"  Status: {h['status']} ({status_name}) - {expirado}")
    print(f"  Rango: {h['inicio']} → {h['fin']}")
    print(f"  Expira: {h['expira_en']}")
    print(f"  Correlation: {h['correlation_id']}")
    print()

# Calendario del proveedor
result = conn.execute(text("""
    SELECT id, proveedor_id, inicio, fin
    FROM calendario_proveedor
    WHERE proveedor_id = 'cccccccc-3333-4444-5555-cccccccccccc'
    ORDER BY inicio DESC
    LIMIT 5
"""))

calendario = result.mappings().all()
print(f"=== CALENDARIO PROVEEDOR (Total: {len(calendario)}) ===\n")

for c in calendario:
    print(f"ID: {c['id'][:8]}...")
    print(f"  Rango: {c['inicio']} → {c['fin']}")
    print()

conn.close()
