import pymysql

conn = pymysql.connect(
    host='localhost',
    user='app_proveedores',
    password='Proveedores_2025',
    database='ev_proveedores'
)

cursor = conn.cursor()

# Verificar proveedor de prueba
print("=== PROVEEDORES DE PRUEBA ===\n")
cursor.execute("SELECT id, nombre, status FROM proveedor WHERE id = 'cccccccc-3333-4444-5555-cccccccccccc'")
prov = cursor.fetchone()
if prov:
    print(f"✅ Proveedor encontrado: {prov[1]} (Status: {prov[2]})")
else:
    print("❌ Proveedor cccccccc-3333-4444-5555-cccccccccccc NO encontrado")
    print("\n📋 Listando primeros 5 proveedores:")
    cursor.execute("SELECT id, nombre FROM proveedor LIMIT 5")
    for p in cursor.fetchall():
        print(f"  - {p[1]}: {p[0]}")

# Verificar habilidades
print("\n=== HABILIDADES ===")
cursor.execute("SELECT COUNT(*) FROM habilidad_proveedor WHERE proveedor_id = 'cccccccc-3333-4444-5555-cccccccccccc'")
hab_count = cursor.fetchone()[0]
print(f"Habilidades del proveedor: {hab_count}")

# Verificar calendario (descansos/bloqueos)
print("\n=== CALENDARIO (BLOQUEOS) ===")
cursor.execute("""
    SELECT tipo, inicio, fin 
    FROM calendario_proveedor 
    WHERE proveedor_id = 'cccccccc-3333-4444-5555-cccccccccccc'
    AND fin >= CURDATE()
""")
calendarios = cursor.fetchall()
if calendarios:
    for cal in calendarios:
        tipo_nombre = "Disponibilidad" if cal[0] == 1 else "Descanso"
        print(f"  - {tipo_nombre}: {cal[1]} a {cal[2]}")
else:
    print("  Sin bloqueos futuros")

# Verificar holds activos
print("\n=== HOLDS ACTIVOS ===")
cursor.execute("""
    SELECT id, inicio, fin, status, expira_en
    FROM reserva_temporal
    WHERE proveedor_id = 'cccccccc-3333-4444-5555-cccccccccccc'
    AND status IN (0, 1)
    AND expira_en > NOW()
""")
holds = cursor.fetchall()
if holds:
    for hold in holds:
        print(f"  - Hold {hold[0][:20]}...: {hold[1]} a {hold[2]} (Status: {hold[3]}, Expira: {hold[4]})")
else:
    print("  Sin holds activos")

cursor.close()
conn.close()
