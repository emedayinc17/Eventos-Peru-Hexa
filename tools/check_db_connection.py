import pymysql
import sys

def check_connection(user, password, db):
    print(f"Testing connection for user: {user} ...")
    try:
        connection = pymysql.connect(
            host='localhost',
            user=user,
            password=password,
            database=db,
            cursorclass=pymysql.cursors.DictCursor
        )
        print(f"SUCCESS: Connected to {db} as {user}")
        connection.close()
        return True
    except pymysql.err.OperationalError as e:
        print(f"FAILURE: Could not connect to {db} as {user}")
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    # Credentials from bootstrap.sql
    credentials = [
        ("app_iam", "IAM_2025", "ev_iam"),
        ("app_catalogo", "Catalogo_2025", "ev_catalogo"),
        ("app_paquetes", "Pkg_2025", "ev_paquetes"),
        ("app_proveedores", "Proveedores_2025", "ev_proveedores"),
        ("app_contratacion", "Contrata_2025", "ev_contratacion"),
        ("app_mensajeria", "Mensajeria_2025", "ev_mensajeria")
    ]

    success_count = 0
    for user, password, db in credentials:
        if check_connection(user, password, db):
            success_count += 1
        print("-" * 30)
    
    if success_count == len(credentials):
        print("All database users connected successfully.")
        sys.exit(0)
    else:
        print("Some database connections failed. Please check if bootstrap.sql was executed.")
        sys.exit(1)
