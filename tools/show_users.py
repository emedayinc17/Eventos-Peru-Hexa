import pymysql

conn = pymysql.connect(host='localhost', user='app_iam', password='IAM_2025', database='ev_iam', autocommit=True)
try:
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, email, password_hash, nombre, status, is_deleted, created_at FROM usuario WHERE email LIKE %s", ('%test%cliente%',))
        rows = cursor.fetchall()
        if not rows:
            print('No rows found matching pattern')
        else:
            for r in rows:
                print('ID:', r[0])
                print('Email:', r[1])
                print('Password Hash:', r[2])
                print('Nombre:', r[3])
                print('Status:', r[4], 'Is_deleted:', r[5])
                print('Created:', r[6])
                print('---')
finally:
    conn.close()
