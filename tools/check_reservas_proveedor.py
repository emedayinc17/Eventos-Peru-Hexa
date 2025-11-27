import pymysql

conn = pymysql.connect(
    host='localhost',
    user='app_contratacion',
    password='Contrata_2025',
    database='ev_contratacion'
)

cursor = conn.cursor()

# Verificar reservas del proveedor
print("=== RESERVAS DEL PROVEEDOR cccccccc-3333-4444-5555-cccccccccccc ===\n")
cursor.execute("""
    SELECT id, inicio, fin, status, hold_id
    FROM reserva
    WHERE proveedor_id = 'cccccccc-3333-4444-5555-cccccccccccc'
    AND fin >= CURDATE()
    AND status = 1
""")
reservas = cursor.fetchall()
if reservas:
    for r in reservas:
        print(f"  - Reserva {r[0][:20]}...: {r[1]} a {r[2]} (Status: {r[3]}, Hold: {r[4][:20] if r[4] else 'None'}...)")
else:
    print("  Sin reservas confirmadas futuras")

cursor.close()
conn.close()
