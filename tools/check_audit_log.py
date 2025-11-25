import pymysql
import json
from datetime import datetime

def check_audit_logs():
    print("--- Checking Audit Logs ---")
    connection = pymysql.connect(
        host='localhost',
        user='app_iam',
        password='IAM_2025',
        database='ev_iam',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    try:
        with connection.cursor() as cursor:
            # Get the last 5 audit logs
            cursor.execute("""
                SELECT id, fecha_hora, actor_id, entidad, entidad_id, accion, metadata
                FROM evento_audit
                ORDER BY fecha_hora DESC
                LIMIT 5
            """)
            rows = cursor.fetchall()
            
            if not rows:
                print("WARNING: No audit logs found.")
                return

            print(f"Found {len(rows)} recent audit logs:")
            for row in rows:
                meta = row['metadata']
                if isinstance(meta, str):
                    try:
                        meta = json.loads(meta)
                    except:
                        pass
                
                print(f"[{row['fecha_hora']}] Action: {row['accion']} | Entity: {row['entidad']} | Actor: {row['actor_id']}")
                print(f"   Metadata: {meta}")
                print("-" * 40)
                
    finally:
        connection.close()

if __name__ == "__main__":
    check_audit_logs()
