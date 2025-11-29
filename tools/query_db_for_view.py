#!/usr/bin/env python3
"""
Query local MySQL to inspect the created pedido and related rows.

Usage:
  python tools/query_db_for_view.py

The script connects as `app_contratacion`@localhost using password `Contrata_2025`
and database `ev_contratacion` (as in project seeds). It will:
  1) Find the latest pedido for cliente_id = 'user-test-01'
  2) SELECT * FROM ev_contratacion.v_pedido_con_cliente WHERE id = <pedido_id>
  3) SELECT id,email,nombre FROM ev_iam.usuario WHERE id = <cliente_id>
  4) SELECT id,nombre FROM ev_catalogo.tipo_evento WHERE id = <tipo_evento_id>

Prints a JSON object with results for inspection.
"""
import sys
import json
import traceback

try:
    import pymysql
except Exception:
    print("ERROR: missing dependency 'pymysql'. Install with:\n  pip install pymysql", file=sys.stderr)
    sys.exit(2)

def connect(host='127.0.0.1', user='app_contratacion', password='Contrata_2025', db='ev_contratacion', port=3306):
    return pymysql.connect(host=host, user=user, password=password, db=db, port=port, cursorclass=pymysql.cursors.DictCursor)

def run():
    out = {"ok": False, "errors": [], "results": {}}
    try:
        conn = connect()
    except Exception as e:
        out["errors"].append(f"DB connect error: {e}")
        print(json.dumps(out, indent=2, ensure_ascii=False, default=str))
        return 1

    try:
        with conn.cursor() as cur:
            # 0) Find latest pedido for test user
            cur.execute("SELECT id, cliente_id, tipo_evento_id, request_id, created_at FROM ev_contratacion.pedido_evento WHERE cliente_id = %s ORDER BY created_at DESC LIMIT 1", ('user-test-01',))
            pedido = cur.fetchone()
            out["results"]["pedido_row"] = pedido

            if not pedido:
                out["errors"].append("No pedido found for cliente_id 'user-test-01'.")
                print(json.dumps(out, indent=2, ensure_ascii=False))
                return 0

            pid = pedido["id"]
            cid = pedido["cliente_id"]
            teid = pedido.get("tipo_evento_id")

            # 1) View
            q1 = "SELECT * FROM ev_contratacion.v_pedido_con_cliente WHERE id = %s LIMIT 1"
            cur.execute(q1, (pid,))
            view_row = cur.fetchone()
            out["results"]["v_pedido_con_cliente"] = view_row

            # 2) Usuario (intento, pero si hay error de permisos no abortamos)
            q2 = "SELECT id, email, nombre FROM ev_iam.usuario WHERE id = %s LIMIT 1"
            try:
                cur.execute(q2, (cid,))
                user_row = cur.fetchone()
            except Exception as e:
                user_row = None
                out["errors"].append(str(e))
            out["results"]["ev_iam.usuario"] = user_row

            # 3) Tipo evento (if present)
            if teid:
                try:
                    q3 = "SELECT id, nombre FROM ev_catalogo.tipo_evento WHERE id = %s LIMIT 1"
                    cur.execute(q3, (teid,))
                    te_row = cur.fetchone()
                except Exception as e:
                    te_row = None
                    out["errors"].append(str(e))
            else:
                te_row = None
            out["results"]["tipo_evento"] = te_row

            out["ok"] = True

    except Exception as e:
        tb = traceback.format_exc()
        out["errors"].append(str(e))
        out["errors"].append(tb)
    finally:
        try:
            conn.close()
        except Exception:
            pass

    print(json.dumps(out, indent=2, ensure_ascii=False, default=str))
    return 0

if __name__ == '__main__':
    sys.exit(run())
