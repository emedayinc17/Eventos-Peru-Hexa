import pymysql

def check_root(password):
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password=password
        )
        print(f"SUCCESS: Connected as root with password '{password}'")
        connection.close()
        return True
    except Exception as e:
        print(f"Failed with password '{password}': {e}")
        return False

passwords = ['', 'root', 'admin', '123456', 'password']
for p in passwords:
    if check_root(p):
        break
