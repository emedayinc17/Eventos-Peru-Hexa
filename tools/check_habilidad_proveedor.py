import pymysql

conn = pymysql.connect(
    host='localhost',
    user='app_proveedores',
    password='Proveedores_2025',
    database='ev_proveedores',
    cursorclass=pymysql.cursors.DictCursor
)

cursor = conn.cursor()

# Verificar proveedor y sus habilidades
print("=== PROVEEDOR DE PRUEBA ===\n")
cursor.execute("""
    SELECT id, nombre, email, status 
    FROM proveedor 
    WHERE id = 'cccccccc-3333-4444-5555-cccccccccccc'
""")
prov = cursor.fetchone()
if prov:
    print(f"✅ ID: {prov['id']}")
    print(f"   Nombre: {prov['nombre']}")
    print(f"   Email: {prov['email']}")
    print(f"   Status: {prov['status']}\n")
else:
    print("❌ Proveedor NO encontrado\n")

# Verificar habilidades
print("=== HABILIDADES ===\n")
cursor.execute("""
    SELECT hp.servicio_id, hp.nivel
    FROM habilidad_proveedor hp
    WHERE hp.proveedor_id = 'cccccccc-3333-4444-5555-cccccccccccc'
""")
habilidades = cursor.fetchall()
if habilidades:
    for hab in habilidades:
        print(f"  - Servicio: {hab['servicio_id']}")
        print(f"    Nivel: {hab['nivel']}\n")
else:
    print("  Sin habilidades registradas\n")

# Verificar si tiene habilidad para el servicio de prueba
servicio_prueba = 'aaaaaaaa-1111-2222-3333-aaaaaaaaaaaa'
cursor.execute("""
    SELECT * FROM habilidad_proveedor 
    WHERE proveedor_id = 'cccccccc-3333-4444-5555-cccccccccccc'
    AND servicio_id = %s
""", (servicio_prueba,))
tiene_habilidad = cursor.fetchone()

print(f"=== VALIDACIÓN ===\n")
if tiene_habilidad:
    print(f"✅ Proveedor TIENE habilidad para servicio {servicio_prueba}")
else:
    print(f"❌ Proveedor NO TIENE habilidad para servicio {servicio_prueba}")
    print(f"\n💡 Solución: Ejecutar este INSERT:")
    print(f"""
INSERT INTO ev_proveedores.habilidad_proveedor (id, proveedor_id, servicio_id, nivel)
VALUES (UUID(), 'cccccccc-3333-4444-5555-cccccccccccc', '{servicio_prueba}', 5);
""")

cursor.close()
conn.close()
