import pymysql

conn = pymysql.connect(
    host='localhost',
    user='app_iam',
    password='IAM_2025',
    database='ev_iam'
)

cursor = conn.cursor()
cursor.execute("SELECT email FROM usuario WHERE id != 'ee111111-1111-4111-8111-aaaaaaaaaaa1' ORDER BY RAND() LIMIT 1")
result = cursor.fetchone()
print(f"Cliente aleatorio: {result[0]}")
cursor.close()
conn.close()
