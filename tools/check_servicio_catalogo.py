import pymysql

conn = pymysql.connect(
    host='localhost',
    user='app_catalogo',
    password='Catalogo_2025',
    database='ev_catalogo',
    cursorclass=pymysql.cursors.DictCursor
)

cursor = conn.cursor()

# Verificar servicio
print("=== SERVICIO DE PRUEBA ===\n")
cursor.execute("""
    SELECT id, nombre, tipo_evento_id, status 
    FROM servicio 
    WHERE id = 'aaaaaaaa-1111-2222-3333-aaaaaaaaaaaa'
""")
servicio = cursor.fetchone()
if servicio:
    print(f"✅ Servicio: {servicio['nombre']}")
    print(f"   Tipo Evento: {servicio['tipo_evento_id']}")
    print(f"   Status: {servicio['status']}\n")
else:
    print("❌ Servicio NO encontrado\n")

# Verificar opción de servicio
print("=== OPCIÓN DE SERVICIO ===\n")
cursor.execute("""
    SELECT id, servicio_id, nombre, status 
    FROM opcion_servicio 
    WHERE id = 'bbbbbbbb-2222-3333-4444-bbbbbbbbbbbb'
""")
opcion = cursor.fetchone()
if opcion:
    print(f"✅ Opción: {opcion['nombre']}")
    print(f"   Servicio ID: {opcion['servicio_id']}")
    print(f"   Status: {opcion['status']}\n")
else:
    print("❌ Opción NO encontrada\n")

# Verificar precio vigente
print("=== PRECIO VIGENTE ===\n")
cursor.execute("""
    SELECT moneda, monto, vigente_desde, vigente_hasta 
    FROM precio_servicio 
    WHERE opcion_servicio_id = 'bbbbbbbb-2222-3333-4444-bbbbbbbbbbbb'
    AND (vigente_hasta IS NULL OR vigente_hasta >= CURDATE())
    ORDER BY vigente_desde DESC
    LIMIT 1
""")
precio = cursor.fetchone()
if precio:
    print(f"✅ Precio: {precio['moneda']} {precio['monto']}")
    print(f"   Vigente desde: {precio['vigente_desde']}")
    print(f"   Vigente hasta: {precio['vigente_hasta']}\n")
else:
    print("❌ Sin precio vigente\n")

cursor.close()
conn.close()
