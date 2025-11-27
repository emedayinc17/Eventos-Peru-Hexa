import pymysql

conn = pymysql.connect(
    host='localhost',
    user='app_iam',
    password='IAM_2025',
    database='ev_iam',
    cursorclass=pymysql.cursors.DictCursor
)

cursor = conn.cursor()

# Verificar usuarios clave
print("=== USUARIOS EN BD ===\n")
cursor.execute("SELECT id, email, nombre FROM usuario WHERE email IN ('admin@eventos.pe', 'demo@eventos.pe')")
users = cursor.fetchall()

if users:
    for user in users:
        print(f"✅ {user['email']} - {user['nombre']} (ID: {user['id'][:20]}...)")
else:
    print("❌ No se encontraron usuarios admin o demo")

# Contar total
cursor.execute("SELECT COUNT(*) as total FROM usuario")
total = cursor.fetchone()
print(f"\n📊 Total usuarios en BD: {total['total']}")

# Verificar roles de demo
print("\n=== ROLES DE demo@eventos.pe ===")
cursor.execute("""
    SELECT r.nombre, r.codigo 
    FROM usuario u
    JOIN usuario_rol ur ON u.id = ur.usuario_id
    JOIN rol r ON ur.rol_id = r.id
    WHERE u.email = 'demo@eventos.pe'
""")
roles = cursor.fetchall()
if roles:
    for role in roles:
        print(f"✅ Rol: {role['nombre']} ({role['codigo']})")
else:
    print("❌ demo@eventos.pe no tiene roles asignados")

cursor.close()
conn.close()
