import pymysql

conn = pymysql.connect(
    host='localhost',
    user='app_proveedores',
    password='Proveedores_2025',
    database='ev_proveedores'
)

cursor = conn.cursor()
cursor.execute('UPDATE reserva_temporal SET status = 3 WHERE proveedor_id = "cccccccc-3333-4444-5555-cccccccccccc" AND status IN (0, 1)')
conn.commit()
print(f'✅ Liberados {cursor.rowcount} holds del proveedor de prueba')
cursor.close()
conn.close()
