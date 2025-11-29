import pymysql
import uuid

# Configuración de conexión
DB_CONFIG = {
    'host': 'localhost',
    'user': 'app_iam',
    'password': 'IAM_2025',
    'database': 'ev_iam',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

ADMIN_EMAIL = 'admin@eventos.pe'
ADMIN_ROLE_CODE = 'ADMIN'


def get_connection():
    return pymysql.connect(**DB_CONFIG)


def get_user_id(email):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM usuario WHERE email=%s", (email,))
            row = cur.fetchone()
            return row['id'] if row else None


def get_role_id(role_code):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM rol WHERE codigo=%s", (role_code,))
            row = cur.fetchone()
            return row['id'] if row else None


def has_user_role(user_id, role_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM usuario_rol WHERE usuario_id=%s AND rol_id=%s", (user_id, role_id))
            return cur.fetchone() is not None


def assign_role(user_id, role_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM usuario_rol WHERE usuario_id=%s AND rol_id=%s",
                (user_id, role_id)
            )
            row = cur.fetchone()
            if row:
                print("El usuario ya tiene el rol ADMIN asignado.")
                return
            new_id = str(uuid.uuid4())
            cur.execute(
                "INSERT INTO usuario_rol (id, usuario_id, rol_id) VALUES (%s, %s, %s)",
                (new_id, user_id, role_id)
            )
            conn.commit()
            print("Rol ADMIN asignado correctamente.")


def main():
    user_id = get_user_id(ADMIN_EMAIL)
    if not user_id:
        print(f"Usuario {ADMIN_EMAIL} no encontrado.")
        return
    role_id = get_role_id(ADMIN_ROLE_CODE)
    if not role_id:
        print("Rol ADMIN no encontrado.")
        return
    if has_user_role(user_id, role_id):
        print(f"El usuario {ADMIN_EMAIL} ya tiene el rol ADMIN.")
    else:
        assign_role(user_id, role_id)

if __name__ == "__main__":
    main()
