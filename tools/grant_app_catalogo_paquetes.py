import pymysql

candidates = [
    ('root',''),
    ('root','root'),
    ('root','MYSQL_ROOT_PASSWORD'),
]

for user, pwd in candidates:
    try:
        print(f"Trying connect as {user}:{pwd!r}...")
        conn = pymysql.connect(host='localhost', user=user, password=pwd, autocommit=True)
        cur = conn.cursor()
        cur.execute("SELECT USER(),CURRENT_USER()")
        print('Connected as', cur.fetchone())
        cur.execute("GRANT SELECT,INSERT,UPDATE,DELETE ON ev_paquetes.* TO 'app_catalogo'@'%' ;")
        cur.execute("FLUSH PRIVILEGES;")
        print('GRANT executed successfully')
        cur.close()
        conn.close()
        break
    except Exception as e:
        print('Failed:', e)
