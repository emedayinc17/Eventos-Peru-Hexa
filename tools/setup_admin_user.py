import pymysql
import uuid

def setup_admin():
    connection = pymysql.connect(
        host='localhost',
        user='app_iam',
        password='IAM_2025',
        database='ev_iam',
        autocommit=True
    )
    
    try:
        with connection.cursor() as cursor:
            # Check if admin exists
            cursor.execute("SELECT id FROM usuario WHERE email = 'admin@eventos.pe'")
            result = cursor.fetchone()
            
            if result:
                print("Admin user already exists. Updating password...")
                password_hash = "$bcrypt-sha256$v=2,t=2b,r=12$X74k7ddCoyDNfEk02o3gHO$mmRQnZkaSGKInBAIlnL2lfB2VnHzfvu"
                cursor.execute("UPDATE usuario SET password_hash = %s WHERE email = 'admin@eventos.pe'", (password_hash,))
                
                # Ensure role exists
                user_id = result[0]
                role_id = 'aaaa1111-1111-1111-1111-aaaaaaaaaaa1'
                
                cursor.execute("SELECT id FROM usuario_rol WHERE usuario_id = %s AND rol_id = %s", (user_id, role_id))
                if not cursor.fetchone():
                    print("Assigning ADMIN role...")
                    ur_id = str(uuid.uuid4())
                    cursor.execute("""
                        INSERT INTO usuario_rol (id, usuario_id, rol_id)
                        VALUES (%s, %s, %s)
                    """, (ur_id, user_id, role_id))
                
                print("Admin user updated.")
                return
            
            user_id = str(uuid.uuid4())
            # Hash password: Admin_2025!
            password_hash = "$bcrypt-sha256$v=2,t=2b,r=12$X74k7ddCoyDNfEk02o3gHO$mmRQnZkaSGKInBAIlnL2lfB2VnHzfvu"
            
            print(f"Creating admin user with ID: {user_id}")
            
            cursor.execute("""
                INSERT INTO usuario (id, email, password_hash, nombre, telefono, status)
                VALUES (%s, 'admin@eventos.pe', %s, 'Admin User', '+51 999 999 999', 1)
            """, (user_id, password_hash))
            
            # Assign ADMIN role
            role_id = 'aaaa1111-1111-1111-1111-aaaaaaaaaaa1'
            ur_id = str(uuid.uuid4())
            
            cursor.execute("""
                INSERT INTO usuario_rol (id, usuario_id, rol_id)
                VALUES (%s, %s, %s)
            """, (ur_id, user_id, role_id))
            
            print("Admin user created successfully.")
            
    finally:
        connection.close()

if __name__ == "__main__":
    setup_admin()
