import pymysql
from passlib.hash import bcrypt_sha256

USERS = [
    ("admin@eventos.pe", "Evoluti0n"),
    ("test.cliente@eventos.pe", "test123"),
    ("demo@eventos.pe", "test123"),
]

def reset_passwords():
    conn = pymysql.connect(host='localhost', user='app_iam', password='IAM_2025', database='ev_iam', autocommit=True)
    try:
        with conn.cursor() as cursor:
            for email, plain in USERS:
                hashed = bcrypt_sha256.hash(plain)
                print (f"Resetting password for {email} to {hashed}")
                cursor.execute("SELECT id FROM usuario WHERE email = %s", (email,))
                row = cursor.fetchone()
                if row:
                    cursor.execute("UPDATE usuario SET password_hash = %s WHERE email = %s", (hashed, email))
                    print(f"Updated password for {email}")
                else:
                    print(f"User {email} not found in DB. Skipping (no insert).")
    finally:
        conn.close()

if __name__ == '__main__':
    reset_passwords()
