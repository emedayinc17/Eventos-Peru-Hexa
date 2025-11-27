import pymysql

# Conexión con credenciales de bootstrap.sql (NO CAMBIAR)
conn = pymysql.connect(
    host='localhost',
    user='app_iam',
    password='IAM_2025',
    database='ev_iam'
)

cursor = conn.cursor()

# Obtener hash de demo@eventos.pe
cursor.execute("SELECT email, password_hash FROM usuario WHERE email IN ('admin@eventos.pe', 'demo@eventos.pe')")
users = cursor.fetchall()

print("=== HASHES DE CONTRASEÑAS ===\n")
for email, hash_val in users:
    print(f"{email}:")
    print(f"  Hash completo: {hash_val}")
    print(f"  Longitud: {len(hash_val)}")
    print(f"  Formato: {'bcrypt-sha256' if hash_val.startswith('$bcrypt-sha256') else 'bcrypt' if hash_val.startswith('$2b') else 'otro'}")
    print()

cursor.close()
conn.close()

# Verificar hash esperado
expected_hash = "$bcrypt-sha256$v=2,t=2b,r=12$0mZ35JSikYcRUxPds2IKK.$G/4eI2JPqTURMzE34fgCa2qNRYdlnSC"
print(f"Hash esperado (Evoluti0n):\n  {expected_hash}\n")
