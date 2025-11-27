import pymysql

conn = pymysql.connect(
    host='localhost',
    user='app_proveedores',
    password='Proveedores_2025',
    database='ev_proveedores'
)

cursor = conn.cursor()

# Verificar holds con correlation_id que empiecen con "pedido-"
print("=== HOLDS ACTIVOS CON CORRELATION_ID ===\n")
cursor.execute("""
    SELECT id, proveedor_id, correlation_id, status, expira_en, created_at
    FROM reserva_temporal
    WHERE correlation_id LIKE 'pedido-%'
    AND status IN (0, 1)
    ORDER BY created_at DESC
    LIMIT 20
""")
holds = cursor.fetchall()
if holds:
    for h in holds:
        print(f"  - {h[0][:20]}... ({h[1][:20]}...)")
        print(f"    Correlation: {h[2]}")
        print(f"    Status: {h[3]}, Expira: {h[4]}, Creado: {h[5]}\n")
else:
    print("  Sin holds activos con correlation_id pedido-*")

# Total de holds
cursor.execute("SELECT COUNT(*) FROM reserva_temporal WHERE status IN (0, 1)")
total = cursor.fetchone()[0]
print(f"\n📊 Total holds activos: {total}")

cursor.close()
conn.close()
