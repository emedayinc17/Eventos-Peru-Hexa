#!/usr/bin/env python3
"""Verifica la configuración completa del proveedor de prueba"""
from sqlalchemy import create_engine, text

engine = create_engine('mysql+pymysql://app_proveedores:Proveedores_2025@localhost/ev_proveedores')
conn = engine.connect()

# Proveedor
result = conn.execute(text("""
    SELECT id, nombre, email, status
    FROM proveedor
    WHERE id = 'cccccccc-3333-4444-5555-cccccccccccc'
"""))
prov = result.mappings().first()
print("\n=== PROVEEDOR ===")
if prov:
    print(f"ID: {prov['id']}")
    print(f"Nombre: {prov['nombre']}")
    print(f"Email: {prov['email']}")
    print(f"Status: {prov['status']}")
else:
    print("❌ PROVEEDOR NO ENCONTRADO")

# Habilidades
result = conn.execute(text("""
    SELECT servicio_id, nivel
    FROM habilidad_proveedor
    WHERE proveedor_id = 'cccccccc-3333-4444-5555-cccccccccccc'
"""))
habilidades = result.mappings().all()
print(f"\n=== HABILIDADES (Total: {len(habilidades)}) ===")
for h in habilidades:
    print(f"  Servicio: {h['servicio_id']}, Nivel: {h['nivel']}")

# Holds activos
result = conn.execute(text("""
    SELECT COUNT(*) as total
    FROM reserva_temporal
    WHERE proveedor_id = 'cccccccc-3333-4444-5555-cccccccccccc'
      AND status IN (0,1)
      AND expira_en > NOW()
"""))
holds = result.first()[0]
print(f"\n=== HOLDS ACTIVOS: {holds} ===")

# Calendario (descansos)
result = conn.execute(text("""
    SELECT COUNT(*) as total
    FROM calendario_proveedor
    WHERE proveedor_id = 'cccccccc-3333-4444-5555-cccccccccccc'
"""))
calendario = result.first()[0]
print(f"=== CALENDARIO: {calendario} bloqueos ===")

conn.close()

# Verificar reservas en contratación
engine2 = create_engine('mysql+pymysql://app_contratacion:Contrata_2025@localhost/ev_contratacion')
conn2 = engine2.connect()

result = conn2.execute(text("""
    SELECT COUNT(*) as total
    FROM reserva
    WHERE proveedor_id = 'cccccccc-3333-4444-5555-cccccccccccc'
      AND status = 1
"""))
reservas = result.first()[0]
print(f"=== RESERVAS CONFIRMADAS: {reservas} ===\n")

conn2.close()
