import os
import pymysql
import uuid

DB_USER = os.getenv('PAQUETES_DB_USER', os.getenv('app_paquetes_user', 'app_paquetes'))
DB_PASS = os.getenv('PAQUETES_DB_PASS', os.getenv('app_paquetes_pass', 'Pkg_2025'))
DB_HOST = os.getenv('PAQUETES_DB_HOST', os.getenv('DB_HOST', 'localhost'))
DB_PORT = int(os.getenv('PAQUETES_DB_PORT', os.getenv('DB_PORT', '3306')))
DB_NAME = os.getenv('PAQUETES_DB_NAME', 'ev_paquetes')

print(f"Probando INSERT/UPDATE/DELETE en {DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

try:
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        port=DB_PORT,
        autocommit=True
    )
    with conn.cursor() as cur:
        # INSERT
        test_id = str(uuid.uuid4())
        cur.execute("INSERT INTO paquete (id, codigo, nombre, moneda, status, is_deleted, created_at) VALUES (%s, %s, %s, %s, 1, 0, NOW())", (test_id, 'TESTCODE', 'Paquete Test', 'PEN'))
        print(f"✅ INSERT realizado. ID: {test_id}")
        # UPDATE
        cur.execute("UPDATE paquete SET nombre=%s WHERE id=%s", ('Paquete Test Modificado', test_id))
        print("✅ UPDATE realizado.")
        # DELETE lógico (is_deleted)
        cur.execute("UPDATE paquete SET is_deleted=1 WHERE id=%s", (test_id,))
        print("✅ DELETE lógico realizado.")
        # Limpieza (opcional): eliminar el registro
        cur.execute("DELETE FROM paquete WHERE id=%s", (test_id,))
        print("✅ Registro eliminado físicamente.")
    conn.close()
except Exception as e:
    print("❌ Error en operaciones de escritura:", e)
    print("Revisa los privilegios de INSERT, UPDATE y DELETE para el usuario sobre la tabla paquete.")
