import os
import pymysql

# Configuración desde variables de entorno (ajusta si es necesario)
DB_USER = os.getenv('PAQUETES_DB_USER', os.getenv('app_paquetes_user', 'app_paquetes'))
DB_PASS = os.getenv('PAQUETES_DB_PASS', os.getenv('app_paquetes_pass', 'Pkg_2025'))
DB_HOST = os.getenv('PAQUETES_DB_HOST', os.getenv('DB_HOST', 'localhost'))
DB_PORT = int(os.getenv('PAQUETES_DB_PORT', os.getenv('DB_PORT', '3306')))
DB_NAME = os.getenv('PAQUETES_DB_NAME', 'ev_paquetes')

print(f"Probando conexión a MySQL: {DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

try:
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        port=DB_PORT,
        connect_timeout=5
    )
    print("✅ Conexión exitosa.")
    with conn.cursor() as cur:
        cur.execute("SHOW TABLES;")
        tables = cur.fetchall()
        print(f"Tablas en {DB_NAME}:", tables)
        # Probar un SELECT simple
        cur.execute("SELECT COUNT(*) FROM paquete;")
        count = cur.fetchone()
        print(f"Registros en paquete: {count[0]}")
    conn.close()
except Exception as e:
    print("❌ Error de conexión o permisos:", e)
    print("Revisa usuario, contraseña, host, puerto y privilegios sobre el schema y tablas.")
