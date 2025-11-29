#!/usr/bin/env python3
"""
Fix opcion_servicio.detalles JSON stored as string instead of JSON object.
Usage: python tools\fix_opciones_detalles.py
It reads DB credentials from services/catalogo-service/.env (basic KEY=VALUE parsing).
"""
import os
import re
import pymysql
from pathlib import Path

env_path = Path(__file__).resolve().parents[1] / 'services' / 'catalogo-service' / '.env'

def read_env(p):
    data = {}
    with open(p, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                k,v = line.split('=',1)
                data[k.strip()] = v.strip().strip('"')
    return data


def main():
    if not env_path.exists():
        print('Env file not found at', env_path)
        return
    env = read_env(env_path)
    host = env.get('DB_HOST','127.0.0.1')
    port = int(env.get('DB_PORT','3306'))
    user = env.get('DB_USER','app_catalogo')
    password = env.get('DB_PASS','')
    db = env.get('DB_NAME', env.get('SCHEMA_CATALOGO','ev_catalogo'))

    print('Connecting to', host, port, 'db=', db, 'user=', user)
    conn = pymysql.connect(host=host, port=port, user=user, password=password, database=db, charset='utf8mb4')
    try:
        with conn.cursor() as cur:
            # Find rows where JSON_TYPE(detalles) = 'STRING'
            cur.execute("SELECT id, detalles FROM opcion_servicio WHERE detalles IS NOT NULL AND JSON_TYPE(detalles) = 'STRING' LIMIT 100")
            rows = cur.fetchall()
            print('Found', len(rows), 'rows with string detalles (sample up to 100)')
            for r in rows:
                print('  id=', r[0], 'detalles=', r[1])

            if rows:
                # Update statement: cast unquoted detalles to JSON
                update_sql = "UPDATE opcion_servicio SET detalles = CAST(JSON_UNQUOTE(detalles) AS JSON) WHERE detalles IS NOT NULL AND JSON_TYPE(detalles) = 'STRING'"
                print('Executing UPDATE to convert string->JSON...')
                cur.execute(update_sql)
                affected = cur.rowcount
                conn.commit()
                print('Rows updated:', affected)
            else:
                print('No rows to update.')
    finally:
        conn.close()

if __name__ == '__main__':
    main()
