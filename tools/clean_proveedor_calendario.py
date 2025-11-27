import pymysql

conn = pymysql.connect(
    host='localhost',
    user='app_proveedores',
    password='Proveedores_2025',
    database='ev_proveedores'
)

cursor = conn.cursor()
cursor.execute('DELETE FROM calendario_proveedor WHERE proveedor_id = "cccccccc-3333-4444-5555-cccccccccccc"')
conn.commit()
print(f'✅ Eliminados {cursor.rowcount} registros de calendario del proveedor de prueba')
print('El proveedor ahora está completamente disponible sin restricciones')
cursor.close()
conn.close()
