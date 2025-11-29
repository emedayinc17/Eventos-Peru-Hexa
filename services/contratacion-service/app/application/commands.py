from typing import Dict, Any, List, Optional
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, OperationalError
from ev_shared.config import Settings
from ev_shared.db import session_scope
import datetime
# IMPORT corregido: NUNCA uses "contratacion-service" con guion en imports
# Usa import absoluto dentro del paquete app (o relativo si prefieres).
from app.infrastructure.db.sqlalchemy.repositories import EmailOutboxSql
from app.infrastructure.http.proveedores_client import ProveedoresClient


# ========= Rollback de holds =========

def _rollback_holds(hold_ids: List[str], proveedores_client: ProveedoresClient) -> None:
    """Libera todos los holds creados en caso de error (best-effort)."""
    for hold_id in hold_ids:
        try:
            proveedores_client.liberar_hold(hold_id)
            print(f"🔄 [ROLLBACK] Hold {hold_id} liberado exitosamente")
        except Exception as e:
            # Loggear pero no lanzar - queremos intentar liberar todos
            print(f"⚠️ [ROLLBACK] Error al liberar hold {hold_id}: {e}")


# ========= Helpers de cálculo =========

def _calcular_total_paquete(settings: Settings, paquete_id: str) -> Dict[str, Any]:
    sql = text("""
        SELECT paquete_id, moneda, monto_total_vigente
        FROM ev_paquetes.v_paquete_precio_vigente_total
        WHERE paquete_id = :pid
        LIMIT 1
    """)
    
    print(f"🔍 [DEBUG _calcular_total_paquete] Ejecutando consulta para paquete: {paquete_id}")
    
    try:
        with session_scope(settings) as s:
            result = s.execute(sql, {"pid": paquete_id})
            print(f"🔍 [DEBUG] Resultado raw: {result}")
            
            row = result.mappings().first()
            print(f"🔍 [DEBUG] Fila obtenida: {row}")
            
            if not row:
                print(f"❌ [ERROR] No se encontró precio para paquete: {paquete_id}")
                raise ValueError("PAQUETE_SIN_PRECIO_VIGENTE")
            
            print(f"✅ [DEBUG] Precio encontrado: {dict(row)}")
            return dict(row)
            
    except Exception as e:
        print(f"💥 [ERROR _calcular_total_paquete] Error en consulta: {e}")
        raise


def _calcular_items_custom(settings: Settings, items: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not items:
        raise ValueError("ITEMS_VACIOS")

    ids = [it["opcion_servicio_id"] for it in items]
    placeholders = ",".join([f":id{i}" for i in range(len(ids))])

    sql = text(f"""
        SELECT opcion_id AS opcion_servicio_id, moneda, monto
        FROM ev_catalogo.v_opcion_con_precio_vigente
        WHERE opcion_id IN ({placeholders})
    """)
    params = {f"id{i}": ids[i] for i in range(len(ids))}

    with session_scope(settings) as s:
        rows = s.execute(sql, params).mappings().all()
        if not rows or len(rows) != len(ids):
            raise ValueError("OPCION_SIN_PRECIO_VIGENTE")
        by_id = {r["opcion_servicio_id"]: dict(r) for r in rows}

    moneda = rows[0]["moneda"]
    items_calc: List[Dict[str, Any]] = []
    total = 0.0

    for it in items:
        op = by_id[it["opcion_servicio_id"]]
        precio_unit = float(op["monto"])
        cantidad = int(it.get("cantidad", 1))
        subtotal = precio_unit * cantidad
        total += subtotal
        items_calc.append({
            "opcion_servicio_id": it["opcion_servicio_id"],
            "cantidad": cantidad,
            "precio_unit": precio_unit,
            "precio_total": subtotal
        })

    return {"moneda": moneda, "total": total, "items_calculados": items_calc}


# ========= Casos de uso (Cliente) =========

def crear_pedido_desde_paquete(settings: Settings, cliente_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    print(f"🔍 [DEBUG crear_pedido_desde_paquete] Iniciando - Cliente: {cliente_id}")
    print(f"🔍 [DEBUG] Payload completo: {payload}")
    
    proveedores_client = ProveedoresClient(settings)
    hold_ids_creados = []
    
    try:
        # 1. Calcular total del paquete
        print(f"🔍 [DEBUG] Calculando total para paquete: {payload['paquete_id']}")
        tot = _calcular_total_paquete(settings, payload["paquete_id"])
        print(f"🔍 [DEBUG] Total calculado: {tot}")
        
        # Si hay proveedores seleccionados, cambiar a COTIZADO; si no, DRAFT
        proveedores_seleccionados = payload.get("proveedores_seleccionados", [])
        status_inicial = 1 if proveedores_seleccionados else 0  # COTIZADO si hay proveedores, DRAFT si no

        # 2. Obtener items del paquete y tipo de evento
        sql_items_paquete = text("""
            SELECT ip.opcion_servicio_id, ip.cantidad, s.tipo_evento_id
            FROM ev_paquetes.item_paquete ip
            JOIN ev_catalogo.opcion_servicio o ON o.id = ip.opcion_servicio_id
            JOIN ev_catalogo.servicio s ON s.id = o.servicio_id
            WHERE ip.paquete_id = :pid
        """)
        
        print(f"🔍 [DEBUG] Obteniendo items del paquete...")
        with session_scope(settings) as s:
            items_rows = s.execute(sql_items_paquete, {"pid": payload["paquete_id"]}).mappings().all()
            print(f"🔍 [DEBUG] Items encontrados: {len(items_rows)}")
            
            if not items_rows:
                raise ValueError("PAQUETE_SIN_ITEMS")

            tipo_evento_id = items_rows[0]["tipo_evento_id"]
            print(f"🔍 [DEBUG] Tipo evento ID: {tipo_evento_id}")
        
        # 3. CREAR HOLDS para proveedores seleccionados (si los hay)
        if proveedores_seleccionados:
            correlation_id = payload.get("correlation_id") or payload.get("request_id") or f"pedido-{datetime.datetime.now().timestamp()}"
            print(f"🔍 [DEBUG] Creando holds para {len(proveedores_seleccionados)} proveedores - correlation_id: {correlation_id}")
            
            for idx, prov_sel in enumerate(proveedores_seleccionados):
                # Normalizar inicio/fin a ISO strings para el client HTTP
                inicio_val = payload["fecha_evento"]
                fin_val = payload.get("fecha_fin") or payload["fecha_evento"]
                if hasattr(inicio_val, "isoformat"):
                    inicio_val = inicio_val.isoformat()
                else:
                    inicio_val = str(inicio_val)
                if hasattr(fin_val, "isoformat"):
                    fin_val = fin_val.isoformat()
                else:
                    fin_val = str(fin_val)

                hold_payload = {
                    "proveedor_id": prov_sel["proveedor_id"],
                    "opcion_servicio_id": prov_sel["opcion_servicio_id"],
                    "inicio": inicio_val,
                    "fin": fin_val,
                    "ttl_min": 30,
                    "correlation_id": f"{correlation_id}-item-{idx}",
                    "created_by": "contratacion-service"
                }
                
                try:
                    print(f"🔍 [DEBUG] Creando hold para proveedor {prov_sel['proveedor_id']} - opción {prov_sel['opcion_servicio_id']}...")
                    hold_creado = proveedores_client.crear_hold(hold_payload)
                    hold_ids_creados.append(hold_creado["id"])
                    print(f"✅ [DEBUG] Hold creado: {hold_creado['id']}")
                except ValueError as e:
                    print(f"❌ [ERROR] Fallo al crear hold: {e}")
                    # ROLLBACK: liberar todos los holds ya creados
                    _rollback_holds(hold_ids_creados, proveedores_client)
                    raise ValueError(f"NO_SE_PUDO_CREAR_HOLD: {e}")
                except Exception as e:
                    print(f"💥 [ERROR] Error inesperado creando hold: {e}")
                    _rollback_holds(hold_ids_creados, proveedores_client)
                    raise
        else:
            print(f"⚠️ [DEBUG] Sin proveedores seleccionados - pedido en DRAFT (admin asignará después)")
            correlation_id = payload.get("correlation_id") or payload.get("request_id")

        # 4. Preparar datos para inserción del pedido
        insert_data = {
            "cliente_id": cliente_id,
            "tipo_evento_id": tipo_evento_id,
            "fecha_evento": payload["fecha_evento"],
            "hora_inicio": payload["hora_inicio"],
            "hora_fin": payload.get("hora_fin"),
            "ubicacion": payload["ubicacion"],
            "monto_total": float(tot["monto_total_vigente"]),
            "moneda": tot["moneda"],
            "status": status_inicial,
            "correlation_id": correlation_id,
            "request_id": payload.get("request_id"),
        }
        
        print(f"🔍 [DEBUG] Datos para inserción: {insert_data}")

        sql_insert_pedido = text("""
            INSERT INTO ev_contratacion.pedido_evento
                (id, cliente_id, tipo_evento_id, fecha_evento, hora_inicio, hora_fin, ubicacion,
                 monto_total, moneda, status, correlation_id, request_id, created_at)
            VALUES (UUID(), :cliente_id, :tipo_evento_id, :fecha_evento, :hora_inicio, :hora_fin, :ubicacion,
                    :monto_total, :moneda, :status, :correlation_id, :request_id, CURRENT_TIMESTAMP)
        """)

        sql_get_by_req = text("""
            SELECT * FROM ev_contratacion.pedido_evento WHERE request_id=:req LIMIT 1
        """)

        sql_get_latest_by_cliente = text("""
            SELECT * FROM ev_contratacion.pedido_evento WHERE cliente_id = :cid ORDER BY created_at DESC LIMIT 1
        """)

        sql_insert_item = text("""
            INSERT INTO ev_contratacion.item_pedido_evento
                (id, pedido_id, tipo_item, referencia_id, cantidad, precio_unit, precio_total, created_at)
            VALUES (UUID(), :pedido_id, 2, :paquete_id, 1, :precio_unit, :precio_total, CURRENT_TIMESTAMP)
        """)

        # 5. Ejecutar en transacción
        with session_scope(settings) as s:
            try:
                print(f"🔍 [DEBUG] Insertando pedido...")
                result = s.execute(sql_insert_pedido, insert_data)
                print(f"🔍 [DEBUG] Resultado inserción pedido: {result.rowcount} filas")
                
            except IntegrityError as e:
                print(f"🔍 [ERROR] IntegrityError: {e}")
                # Si hay duplicado, liberar holds y retornar el existente
                _rollback_holds(hold_ids_creados, proveedores_client)
                if payload.get("request_id"):
                    row = s.execute(sql_get_by_req, {"req": payload.get("request_id")}).mappings().first()
                    if row:
                        print(f"🔍 [DEBUG] Pedido duplicado encontrado: {dict(row)}")
                        return dict(row)
                raise
            except Exception as e:
                print(f"💥 [ERROR] Error al insertar pedido: {e}")
                _rollback_holds(hold_ids_creados, proveedores_client)
                raise

            # Obtener el pedido insertado (por request_id si se envió, sino el último pedido del cliente)
            print(f"🔍 [DEBUG] Obteniendo pedido creado...")
            if payload.get("request_id"):
                prow = s.execute(sql_get_by_req, {"req": payload.get("request_id")}).mappings().first()
            else:
                prow = s.execute(sql_get_latest_by_cliente, {"cid": cliente_id}).mappings().first()
            if not prow:
                _rollback_holds(hold_ids_creados, proveedores_client)
                raise ValueError("NO_SE_PUDO_RECUPERAR_PEDIDO_CREADO")
                
            pedido_id = prow["id"]
            print(f"🔍 [DEBUG] Pedido ID creado: {pedido_id}")

            # Insertar items individuales por opción_servicio (tipo 'SERVICIO')
            print(f"🔍 [DEBUG] Insertando items por opción de servicio...")
            try:
                for item_row in items_rows:
                    opcion_id = item_row["opcion_servicio_id"]
                    cantidad = item_row.get("cantidad") or 1

                    # Obtener nombre de la opción
                    name_row = s.execute(
                        text("SELECT nombre FROM ev_catalogo.opcion_servicio WHERE id = :oid LIMIT 1"),
                        {"oid": opcion_id},
                    ).mappings().first()
                    nombre_servicio = name_row["nombre"] if name_row else None

                    # Obtener precio vigente de la opción
                    price_row = s.execute(
                        text("SELECT monto FROM ev_catalogo.v_opcion_con_precio_vigente WHERE opcion_id = :oid LIMIT 1"),
                        {"oid": opcion_id},
                    ).mappings().first()
                    precio_unit = float(price_row["monto"]) if price_row and price_row["monto"] is not None else 0.0
                    subtotal = cantidad * precio_unit

                    insert_item_sql = text("""
                        INSERT INTO ev_contratacion.item_pedido_evento
                          (id, pedido_id, opcion_servicio_id, nombre_servicio, cantidad, precio_unitario, subtotal, tipo_item, referencia_id, created_at)
                        VALUES (UUID(), :pedido_id, :opcion_id, :nombre_servicio, :cantidad, :precio_unitario, :subtotal, 'SERVICIO', :ref_id, CURRENT_TIMESTAMP)
                    """)

                    s.execute(insert_item_sql, {
                        "pedido_id": pedido_id,
                        "opcion_id": opcion_id,
                        "nombre_servicio": nombre_servicio,
                        "cantidad": cantidad,
                        "precio_unitario": precio_unit,
                        "subtotal": subtotal,
                        "ref_id": opcion_id,
                    })

                print(f"🔍 [DEBUG] Items insertados para pedido: {pedido_id}")
            except Exception as e:
                print(f"💥 [ERROR] Error al insertar items: {e}")
                _rollback_holds(hold_ids_creados, proveedores_client)
                raise

            print(f"✅ [DEBUG] Pedido creado exitosamente con {len(hold_ids_creados)} holds")
            # Preparamos resultado base y salimos de la transacción (commit)
            result = dict(prow)
            result["holds_creados"] = hold_ids_creados

            # Intento final de rellenar campos relacionados sobre el resultado base
            try:
                _fill_missing_related_fields(settings, result)
            except Exception as e:
                print(f"⚠️ [WARN] Fallback rellenado sobre resultado base falló: {e}")

        # Después del commit, intentamos leer la vista desde una nueva sesión
        try:
            with session_scope(settings) as s2:
                vp = s2.execute(text("SELECT * FROM ev_contratacion.v_pedido_con_cliente WHERE id = :pid LIMIT 1"), {"pid": pedido_id}).mappings().first()
                if vp:
                    print(f"🔍 [DEBUG] Vista v_pedido_con_cliente encontrada post-commit para pedido {pedido_id}")
                    data = dict(vp)
                    # Convierte timedeltas a time si aplica
                    if "hora_inicio" in data:
                        data["hora_inicio"] = _convert_timedelta_to_time(data["hora_inicio"])
                    if "hora_fin" in data:
                        data["hora_fin"] = _convert_timedelta_to_time(data["hora_fin"])
                    try:
                        _fill_missing_related_fields(settings, data)
                    except Exception as e:
                        print(f"⚠️ [WARN] Fallback rellenado falló (post-commit): {e}")
                    data["holds_creados"] = hold_ids_creados
                    return data
                else:
                    print(f"⚠️ [WARN] Vista v_pedido_con_cliente NO devolvió filas post-commit para pedido {pedido_id}")
        except Exception as e:
            print(f"⚠️ [WARN] No se pudo leer vista post-commit: {e}")

        return result

    except ValueError as e:
        print(f"❌ [ERROR] ValueError en crear_pedido_desde_paquete: {e}")
        raise
    except Exception as e:
        print(f"💥 [ERROR] Exception inesperada en crear_pedido_desde_paquete: {e}")
        import traceback
        traceback.print_exc()
        raise


def crear_pedido_custom(settings: Settings, cliente_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    proveedores_client = ProveedoresClient(settings)
    hold_ids_creados = []
    
    try:
        calc = _calcular_items_custom(settings, [dict(x) for x in payload["items"]])
        status_inicial = 1 if calc["total"] > 0 else 0  # COTIZADO si hay total; DRAFT si no

        # 1. CREAR HOLDS para cada item custom (OPCIONAL - solo si viene proveedor_id)
        proveedor_id = payload.get("proveedor_id")
        
        if proveedor_id:
            correlation_id = payload.get("correlation_id") or payload.get("request_id") or f"pedido-custom-{datetime.datetime.now().timestamp()}"
            print(f"🔍 [DEBUG crear_pedido_custom] Creando holds con correlation_id: {correlation_id} para proveedor: {proveedor_id}")
            
                for idx, item in enumerate(calc["items_calculados"]):
                # Normalizar inicio/fin a ISO strings para el client HTTP
                inicio_val = payload["fecha_evento"]
                fin_val = payload.get("fecha_fin") or payload["fecha_evento"]
                if hasattr(inicio_val, "isoformat"):
                    inicio_val = inicio_val.isoformat()
                else:
                    inicio_val = str(inicio_val)
                if hasattr(fin_val, "isoformat"):
                    fin_val = fin_val.isoformat()
                else:
                    fin_val = str(fin_val)

                hold_payload = {
                    "proveedor_id": proveedor_id,
                    "opcion_servicio_id": item["opcion_servicio_id"],
                    "inicio": inicio_val,
                    "fin": fin_val,
                    "ttl_min": 30,
                    "correlation_id": f"{correlation_id}-item-{idx}",
                    "created_by": "contratacion-service"
                }
                
                try:
                    print(f"🔍 [DEBUG] Creando hold para opción {item['opcion_servicio_id']}...")
                    hold_creado = proveedores_client.crear_hold(hold_payload)
                    hold_ids_creados.append(hold_creado["id"])
                    print(f"✅ [DEBUG] Hold creado: {hold_creado['id']}")
                except ValueError as e:
                    print(f"❌ [ERROR] Fallo al crear hold: {e}")
                    _rollback_holds(hold_ids_creados, proveedores_client)
                    raise ValueError(f"NO_SE_PUDO_CREAR_HOLD: {e}")
                except Exception as e:
                    print(f"💥 [ERROR] Error inesperado creando hold: {e}")
                    _rollback_holds(hold_ids_creados, proveedores_client)
                    raise
        else:
            print(f"⚠️ [DEBUG] Sin proveedor_id - pedido sin holds (admin asignará después)")
            correlation_id = payload.get("correlation_id") or payload.get("request_id")

        # 2. Crear pedido en BD
        sql_insert_pedido = text("""
            INSERT INTO ev_contratacion.pedido_evento
                (id, cliente_id, tipo_evento_id, fecha_evento, hora_inicio, hora_fin, ubicacion,
                 monto_total, moneda, status, correlation_id, request_id, created_at)
            VALUES (UUID(), :cliente_id, :tipo_evento_id, :fecha_evento, :hora_inicio, :hora_fin, :ubicacion,
                    :monto_total, :moneda, :status, :correlation_id, :request_id, CURRENT_TIMESTAMP)
        """)

        sql_get_by_req = text("""
            SELECT * FROM ev_contratacion.pedido_evento WHERE request_id=:req LIMIT 1
        """)

        sql_get_latest_by_cliente = text("""
            SELECT * FROM ev_contratacion.pedido_evento WHERE cliente_id = :cid ORDER BY created_at DESC LIMIT 1
        """)

        sql_insert_item = text("""
            INSERT INTO ev_contratacion.item_pedido_evento
                (id, pedido_id, tipo_item, referencia_id, cantidad, precio_unit, precio_total, created_at)
            VALUES (UUID(), :pedido_id, 1, :opcion_servicio_id, :cantidad, :precio_unit, :precio_total, CURRENT_TIMESTAMP)
        """)

        with session_scope(settings) as s:
            try:
                s.execute(sql_insert_pedido, {
                    "cliente_id": cliente_id,
                    "tipo_evento_id": payload["tipo_evento_id"],
                    "fecha_evento": payload["fecha_evento"],
                    "hora_inicio": payload["hora_inicio"],
                    "hora_fin": payload.get("hora_fin"),
                    "ubicacion": payload["ubicacion"],
                    "monto_total": float(calc["total"]),
                    "moneda": calc["moneda"],
                    "status": status_inicial,
                    "correlation_id": correlation_id,
                    "request_id": payload.get("request_id"),
                })
            except IntegrityError:
                _rollback_holds(hold_ids_creados, proveedores_client)
                row = s.execute(sql_get_by_req, {"req": payload.get("request_id")}).mappings().first()
                if row:
                    return dict(row)
                raise
            except Exception as e:
                _rollback_holds(hold_ids_creados, proveedores_client)
                raise

            if payload.get("request_id"):
                prow = s.execute(sql_get_by_req, {"req": payload.get("request_id")}).mappings().first()
            else:
                prow = s.execute(sql_get_latest_by_cliente, {"cid": cliente_id}).mappings().first()
            if not prow:
                _rollback_holds(hold_ids_creados, proveedores_client)
                raise ValueError("NO_SE_PUDO_RECUPERAR_PEDIDO_CREADO")
            
            pedido_id = prow["id"]

            try:
                for it in calc["items_calculados"]:
                    s.execute(sql_insert_item, {
                        "pedido_id": pedido_id,
                        "opcion_servicio_id": it["opcion_servicio_id"],
                        "cantidad": it["cantidad"],
                        "precio_unit": it["precio_unit"],
                        "precio_total": it["precio_total"],
                    })
            except Exception as e:
                _rollback_holds(hold_ids_creados, proveedores_client)
                raise

            result = dict(prow)
            result["holds_creados"] = hold_ids_creados

        # Post-commit: intentar leer la vista desde una nueva sesión para incluir campos relacionados
        try:
            with session_scope(settings) as s2:
                vp = s2.execute(text("SELECT * FROM ev_contratacion.v_pedido_con_cliente WHERE id = :pid LIMIT 1"), {"pid": pedido_id}).mappings().first()
                if vp:
                    data = dict(vp)
                    if "hora_inicio" in data:
                        data["hora_inicio"] = _convert_timedelta_to_time(data["hora_inicio"])
                    if "hora_fin" in data:
                        data["hora_fin"] = _convert_timedelta_to_time(data["hora_fin"])
                    try:
                        _fill_missing_related_fields(settings, data)
                    except Exception as e:
                        print(f"⚠️ [WARN] Fallback rellenado falló (post-commit custom): {e}")
                    data["holds_creados"] = hold_ids_creados
                    return data
        except Exception as e:
            print(f"⚠️ [WARN] No se pudo leer vista post-commit (custom): {e}")

        return result
            
    except Exception as e:
        # Último catch-all para asegurar rollback
        _rollback_holds(hold_ids_creados, proveedores_client)
        raise


def listar_mis_pedidos(settings: Settings, cliente_id: str) -> List[Dict[str, Any]]:
    sql = text("""
        SELECT * FROM ev_contratacion.v_pedido_con_cliente
        WHERE cliente_id = :uid
        ORDER BY created_at DESC
    """)
    with session_scope(settings) as s:
        rows = s.execute(sql, {"uid": cliente_id}).mappings().all()
        result = []
        for r in rows:
            data = dict(r)
            # Convierte timedeltas a time
            if "hora_inicio" in data:
                data["hora_inicio"] = _convert_timedelta_to_time(data["hora_inicio"])
            if "hora_fin" in data:
                data["hora_fin"] = _convert_timedelta_to_time(data["hora_fin"])
            result.append(data)
        return result

def listar_todos_pedidos_admin(settings: Settings, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Lista TODOS los pedidos del sistema (solo para ADMIN)
    """
    sql = text("""
        SELECT * FROM ev_contratacion.v_pedido_con_cliente
        ORDER BY created_at DESC
        LIMIT :lim OFFSET :off
    """)
    with session_scope(settings) as s:
        rows = s.execute(sql, {"lim": limit, "off": offset}).mappings().all()
        result = []
        for r in rows:
            data = dict(r)
            # Convierte timedeltas a time
            if "hora_inicio" in data:
                data["hora_inicio"] = _convert_timedelta_to_time(data["hora_inicio"])
            if "hora_fin" in data:
                data["hora_fin"] = _convert_timedelta_to_time(data["hora_fin"])
            result.append(data)
        return result

def admin_obtener_pedido(settings: Settings, pedido_id: str) -> Dict[str, Any]:
    """
    Obtiene cualquier pedido del sistema (solo ADMIN)
    """
    sql_pedido = text("""
        SELECT * FROM ev_contratacion.v_pedido_con_cliente
        WHERE id = :pid
        LIMIT 1
    """)
    # Ampliamos la consulta de items para incluir datos legibles del catálogo
    # (opción/servicio/paquete) y datos de reserva/proveedor cuando existan.
    sql_items = text("""
        SELECT
          i.id,
          i.pedido_id,
          i.tipo_item,
          i.referencia_id,
          i.cantidad,
          i.precio_unit,
          i.precio_total,
          i.created_at,
          -- Opcional: si es item tipo 1 (opción de servicio) obtener opción y servicio
          o.nombre AS opcion_nombre,
          o.detalles AS opcion_detalles,
          s.id AS servicio_id,
          s.nombre AS servicio_nombre,
          s.descripcion AS servicio_descripcion,
          -- Si es paquete (tipo 2) obtener nombre del paquete
          pck.nombre AS paquete_nombre,
          -- Reserva (si existe) y proveedor asociado
          r.id AS reserva_id,
          r.proveedor_id AS proveedor_id,
          pr.nombre AS proveedor_nombre,
          pr.email AS proveedor_email
        FROM ev_contratacion.item_pedido_evento i
        LEFT JOIN ev_catalogo.opcion_servicio o
          ON (i.tipo_item = 1 AND o.id = i.referencia_id)
        LEFT JOIN ev_catalogo.servicio s
          ON o.servicio_id = s.id
        LEFT JOIN ev_paquetes.paquete pck
          ON (i.tipo_item = 2 AND pck.id = i.referencia_id)
        LEFT JOIN ev_contratacion.reserva r
          ON r.item_pedido_id = i.id
        LEFT JOIN ev_proveedores.proveedor pr
          ON pr.id = r.proveedor_id
        WHERE i.pedido_id = :pid
        ORDER BY i.created_at ASC
    """)

    with session_scope(settings) as s:
        p = s.execute(sql_pedido, {"pid": pedido_id}).mappings().first()
        if not p:
            raise ValueError("PEDIDO_NO_ENCONTRADO")

        # Intentamos la consulta completa (incluye JOIN a proveedores). Si falla por permisos,
        # caemos a una consulta simplificada que omite la tabla de proveedores.
        try:
            rows = s.execute(sql_items, {"pid": pedido_id}).mappings().all()
        except OperationalError as oe:
            # Posible falta de permisos para leer ev_proveedores.proveedor (Error 1142).
            print(f"⚠️ [WARN] No se pudo ejecutar consulta completa de items (posible permiso denegado): {oe}")
            sql_items_simple = text("""
                SELECT
                  i.id,
                  i.pedido_id,
                  i.tipo_item,
                  i.referencia_id,
                  i.cantidad,
                  i.precio_unit,
                  i.precio_total,
                  i.created_at,
                  o.nombre AS opcion_nombre,
                  o.detalles AS opcion_detalles,
                  s.id AS servicio_id,
                  s.nombre AS servicio_nombre,
                  s.descripcion AS servicio_descripcion,
                  pck.nombre AS paquete_nombre
                FROM ev_contratacion.item_pedido_evento i
                LEFT JOIN ev_catalogo.opcion_servicio o
                  ON (i.tipo_item = 1 AND o.id = i.referencia_id)
                LEFT JOIN ev_catalogo.servicio s
                  ON o.servicio_id = s.id
                LEFT JOIN ev_paquetes.paquete pck
                  ON (i.tipo_item = 2 AND pck.id = i.referencia_id)
                WHERE i.pedido_id = :pid
                ORDER BY i.created_at ASC
            """)
            rows = s.execute(sql_items_simple, {"pid": pedido_id}).mappings().all()

        data = dict(p)

        # Convierte timedeltas a time
        if "hora_inicio" in data:
            data["hora_inicio"] = _convert_timedelta_to_time(data["hora_inicio"])
        if "hora_fin" in data:
            data["hora_fin"] = _convert_timedelta_to_time(data["hora_fin"])

        # Mapear items y construir lista de proveedores únicos
        items = []
        proveedores_map = {}
        for r in rows:
            it = dict(r)
            # Normalizar nombres para compatibilidad con frontend (valores ya vienen en las columnas)
            if it.get("opcion_nombre"):
                it["opcion_nombre"] = it.get("opcion_nombre")
            if it.get("servicio_nombre"):
                it["servicio_nombre"] = it.get("servicio_nombre")
            if it.get("paquete_nombre"):
                it["paquete_nombre"] = it.get("paquete_nombre")

            # Si hay proveedor asociado, añadir a map
            prov_id = it.get("proveedor_id")
            prov_nombre = it.get("proveedor_nombre")
            prov_email = it.get("proveedor_email")
            if prov_id:
                proveedores_map[str(prov_id)] = {
                    "id": prov_id,
                    "nombre": prov_nombre,
                    "email": prov_email,
                }

            items.append(it)

        data["items"] = items
        # Lista de proveedores (únicos) relacionados con el pedido
        data["proveedores"] = list(proveedores_map.values())
        return data
        
def _convert_timedelta_to_time(td):
    """Convierte un datetime.timedelta a datetime.time."""
    import datetime
    if not isinstance(td, datetime.timedelta):
        return td # Si ya es time o str, lo devolvemos
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    return datetime.time(hour=hours, minute=minutes, second=seconds)


def _fill_missing_related_fields(settings: Settings, data: Dict[str, Any]) -> None:
    """Rellena campos relacionados faltantes en el diccionario `data`.

    - intenta obtener `tipo_evento_nombre` desde `ev_catalogo.tipo_evento` si falta
    - intenta obtener `cliente_email` y `cliente_nombre` desde `ev_iam.usuario` si faltan
    Fallos en estas consultas no deberían lanzar errores hacia el caller (se atrapan internamente).
    """
    try:
        with session_scope(settings) as s:
            # tipo_evento_nombre
            te_id = data.get("tipo_evento_id")
            if te_id and not data.get("tipo_evento_nombre"):
                try:
                    row = s.execute(text("SELECT nombre FROM ev_catalogo.tipo_evento WHERE id = :tid LIMIT 1"), {"tid": te_id}).mappings().first()
                    if row and row.get("nombre"):
                        data["tipo_evento_nombre"] = row.get("nombre")
                    else:
                        # Dejar cadena vacía si no existe
                        data.setdefault("tipo_evento_nombre", "")
                except Exception as e:
                    print(f"⚠️ [WARN] No se pudo obtener tipo_evento_nombre: {e}")
                    data.setdefault("tipo_evento_nombre", "")

            # cliente_nombre / cliente_email
            cid = data.get("cliente_id")
            if cid and (not data.get("cliente_nombre") or not data.get("cliente_email")):
                try:
                    # Intentamos leer directamente; podría fallar por permisos (1142)
                    row = s.execute(text("SELECT id, email, nombre FROM ev_iam.usuario WHERE id = :uid LIMIT 1"), {"uid": cid}).mappings().first()
                    if row:
                        if not data.get("cliente_email"):
                            data["cliente_email"] = row.get("email") or data.get("cliente_email")
                        if not data.get("cliente_nombre"):
                            data["cliente_nombre"] = row.get("nombre") or data.get("cliente_nombre")
                except OperationalError as oe:
                    # Propagar información de permiso en logs, no lanzar.
                    print(f"⚠️ [WARN] No tiene permiso para leer ev_iam.usuario: {oe}")
                except Exception as e:
                    print(f"⚠️ [WARN] Error al leer ev_iam.usuario: {e}")

    except Exception as e:
        # No queremos romper el flujo principal por errores auxiliares
        print(f"⚠️ [WARN] Falla general en _fill_missing_related_fields: {e}")

def obtener_pedido(settings: Settings, cliente_id: str, pedido_id: str) -> Dict[str, Any]:
    sql_pedido = text("""
        SELECT * FROM ev_contratacion.v_pedido_con_cliente
        WHERE id = :pid AND cliente_id = :uid
        LIMIT 1
    """)
    sql_items = text("""
        SELECT id, pedido_id, tipo_item, referencia_id, cantidad, precio_unit, precio_total, created_at
        FROM ev_contratacion.item_pedido_evento
        WHERE pedido_id = :pid
        ORDER BY created_at ASC
    """)
    with session_scope(settings) as s:
        p = s.execute(sql_pedido, {"pid": pedido_id, "uid": cliente_id}).mappings().first()
        if not p:
            raise ValueError("PEDIDO_NO_ENCONTRADO")
        items = s.execute(sql_items, {"pid": pedido_id}).mappings().all()
        data = dict(p)
        # Convierte timedeltas a time
        if "hora_inicio" in data:
            data["hora_inicio"] = _convert_timedelta_to_time(data["hora_inicio"])
        if "hora_fin" in data:
            data["hora_fin"] = _convert_timedelta_to_time(data["hora_fin"])
        data["items"] = [dict(i) for i in items]
        return data
    

def enviar_resumen_pedido(settings: Settings, cliente_id: str, pedido_id: str, to_email: str) -> Dict[str, Any]:
    ped = obtener_pedido(settings, cliente_id, pedido_id)
    body = f"""
    Resumen de pedido #{ped['id']}
    Fecha: {ped['fecha_evento']} - {ped['hora_inicio']}
    Ubicación: {ped['ubicacion']}
    Total: {ped['moneda']} {ped['monto_total']}
    """
    out = EmailOutboxSql(settings).enqueue(
        to_email=to_email,
        subject=f"Resumen de pedido {ped['id']}",
        body=body,
        template="resumen_pedido",
        payload_json={"pedido_id": ped["id"], "cliente_email": ped.get("cliente_email")},
        correlation_id=ped.get("correlation_id"),
        created_by=cliente_id
    )
    return {"outbox_id": out["id"], "status": "PEND"}


# ========= Admin helpers =========

def _get_pedido_row(settings: Settings, pedido_id: str) -> Optional[Dict[str, Any]]:
    sql = text("SELECT * FROM ev_contratacion.pedido_evento WHERE id=:id LIMIT 1")
    with session_scope(settings) as s:
        row = s.execute(sql, {"id": pedido_id}).mappings().first()
        return dict(row) if row else None


def _recalcular_total_pedido(settings: Settings, pedido_id: str) -> Dict[str, Any]:
    sql_sum = text("""
        SELECT COALESCE(SUM(precio_total),0) AS total
        FROM ev_contratacion.item_pedido_evento
        WHERE pedido_id = :pid
    """)
    sql_upd = text("""
        UPDATE ev_contratacion.pedido_evento
           SET monto_total = :total
         WHERE id = :pid
         LIMIT 1
    """)
    with session_scope(settings) as s:
        total = s.execute(sql_sum, {"pid": pedido_id}).scalar() or 0.0
        s.execute(sql_upd, {"pid": pedido_id, "total": float(total)})
        row = s.execute(text("SELECT * FROM ev_contratacion.pedido_evento WHERE id=:id LIMIT 1"),
                        {"id": pedido_id}).mappings().first()
        out = dict(row) if row else {"id": pedido_id, "monto_total": float(total)}
    return out


# ========= Admin: cambio de estado =========

_ALLOWED = {
    0: {1, 5},  # DRAFT -> COTIZADO / CANCELADO
    1: {2, 5},  # COTIZADO -> APROBADO / CANCELADO
    2: {3, 5},  # APROBADO -> ASIGNADO / CANCELADO
    3: {4, 5},  # ASIGNADO -> CERRADO / CANCELADO
    4: set(),   # CERRADO
    5: set(),   # CANCELADO
}

def admin_cambiar_estado(settings: Settings, pedido_id: str, nuevo_estado: int) -> Dict[str, Any]:
    ped = _get_pedido_row(settings, pedido_id)
    if not ped:
        raise ValueError("PEDIDO_NO_ENCONTRADO")

    actual = int(ped["status"])
    if nuevo_estado not in _ALLOWED.get(actual, set()):
        raise ValueError(f"TRANSICION_INVALIDA:{actual}->{nuevo_estado}")

    if nuevo_estado >= 2 and float(ped.get("monto_total", 0)) <= 0:
        raise ValueError("TOTAL_INVALIDO")

    with session_scope(settings) as s:
        s.execute(text("""
            UPDATE ev_contratacion.pedido_evento
               SET status=:st
             WHERE id=:id
             LIMIT 1
        """), {"st": int(nuevo_estado), "id": pedido_id})
        row = s.execute(text("SELECT * FROM ev_contratacion.pedido_evento WHERE id=:id LIMIT 1"),
                        {"id": pedido_id}).mappings().first()
        return dict(row)


# ========= Admin: agregar / eliminar ítems =========

def admin_agregar_items(settings: Settings, pedido_id: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not items:
        raise ValueError("ITEMS_VACIOS")
    ped = _get_pedido_row(settings, pedido_id)
    if not ped:
        raise ValueError("PEDIDO_NO_ENCONTRADO")

    ids = [it["opcion_servicio_id"] for it in items]
    placeholders = ",".join([f":id{i}" for i in range(len(ids))])

    sql_precio = text(f"""
        SELECT opcion_id AS opcion_servicio_id, moneda, monto
        FROM ev_catalogo.v_opcion_con_precio_vigente
        WHERE opcion_id IN ({placeholders})
    """)
    params = {f"id{i}": ids[i] for i in range(len(ids))}

    with session_scope(settings) as s:
        rows = s.execute(sql_precio, params).mappings().all()
        if not rows or len(rows) != len(ids):
            raise ValueError("OPCION_SIN_PRECIO_VIGENTE")
        by_id = {r["opcion_servicio_id"]: dict(r) for r in rows}

    sql_ins = text("""
        INSERT INTO ev_contratacion.item_pedido_evento
            (id, pedido_id, tipo_item, referencia_id, cantidad, precio_unit, precio_total, created_at)
        VALUES (UUID(), :pid, 1, :ref, :cant, :unit, :tot, CURRENT_TIMESTAMP)
    """)

    with session_scope(settings) as s:
        for it in items:
            ref = it["opcion_servicio_id"]
            cant = int(it.get("cantidad", 1))
            unit = float(by_id[ref]["monto"])
            tot  = unit * cant
            s.execute(sql_ins, {"pid": pedido_id, "ref": ref, "cant": cant, "unit": unit, "tot": tot})

    return _recalcular_total_pedido(settings, pedido_id)


def admin_eliminar_items(settings: Settings, pedido_id: str, item_ids: List[str]) -> Dict[str, Any]:
    if not item_ids:
        raise ValueError("ITEM_IDS_VACIOS")
    ped = _get_pedido_row(settings, pedido_id)
    if not ped:
        raise ValueError("PEDIDO_NO_ENCONTRADO")
    # Permite DELETE cuando status esté entre 0 y 2
    if int(ped["status"]) not in (0, 1, 2):
        raise ValueError("NO_PERMITE_ELIMINAR_EN_ESTE_ESTADO")

    placeholders = ",".join([f":id{i}" for i in range(len(item_ids))])
    params = {f"id{i}": item_ids[i] for i in range(len(item_ids))}
    params["pid"] = pedido_id

    sql_del = text(f"""
        DELETE FROM ev_contratacion.item_pedido_evento
         WHERE pedido_id = :pid
           AND id IN ({placeholders})
    """)

    with session_scope(settings) as s:
        s.execute(sql_del, params)

    return _recalcular_total_pedido(settings, pedido_id)


# ========= Admin: asignar proveedor =========

def _hay_conflicto_asignacion(settings: Settings, proveedor_id: str, inicio: str, fin: str) -> bool:
    """
    Conflicto con reservas CONFIRMADAS en contratación.
    Tabla y columnas reales: ev_contratacion.reserva (inicio, fin, status=1)
    """
    sql_conf = text("""
        SELECT 1
          FROM ev_contratacion.reserva
         WHERE proveedor_id = :prov
           AND status IN (1)              -- 1=CONFIRMADA
           AND NOT (:fin <= inicio OR :ini >= fin)
         LIMIT 1
    """)
    with session_scope(settings) as s:
        r = s.execute(sql_conf, {"prov": proveedor_id, "ini": inicio, "fin": fin}).first()
        return bool(r)


def _hold_valido(settings: Settings, hold_id: str, proveedor_id: str, inicio: str, fin: str) -> bool:
    """
    Valida un hold activo/confirmado que no haya expirado y solape.
    Tabla real: ev_proveedores.reserva_temporal (inicio, fin, expira_en, status)
    """
    sql = text("""
        SELECT 1
          FROM ev_proveedores.reserva_temporal
         WHERE id = :hid
           AND proveedor_id = :prov
           AND status IN (0,1)            -- 0=hold activo, 1=confirmada (tabla proveedores)
           AND expira_en > NOW()
           AND NOT (:fin <= inicio OR :ini >= fin)
         LIMIT 1
    """)
    with session_scope(settings) as s:
        r = s.execute(sql, {"hid": hold_id, "prov": proveedor_id, "ini": inicio, "fin": fin}).first()
        return bool(r)


def admin_asignar_proveedor(settings: Settings, pedido_id: str,
                            proveedor_id: str, fecha_inicio: str, fecha_fin: str,
                            hold_id: Optional[str] = None) -> Dict[str, Any]:
    from ..infrastructure.http.proveedores_client import ProveedoresClient
    proveedores = ProveedoresClient(settings)
    
    ped = _get_pedido_row(settings, pedido_id)
    if not ped:
        raise ValueError("PEDIDO_NO_ENCONTRADO")

    # Estado mínimo: APROBADO (2)
    if int(ped["status"]) < 2:
        raise ValueError("ESTADO_NO_PERMITE_ASIGNACION")

    # La tabla ev_contratacion.reserva exige item_pedido_id.
    # Para MVP: usamos el PRIMER item del pedido.
    sql_item = text("""
        SELECT id, referencia_id, tipo_item
        FROM ev_contratacion.item_pedido_evento
        WHERE pedido_id = :pid
        ORDER BY created_at ASC
        LIMIT 1
    """)
    
    with session_scope(settings) as s:
        item = s.execute(sql_item, {"pid": pedido_id}).mappings().first()
        if not item:
            raise ValueError("PEDIDO_SIN_ITEMS")

        # Obtener opcion_servicio_id (si es paquete, tomar primer item del paquete)
        if item["tipo_item"] == 2:  # Paquete
            opcion_id = s.execute(
                text("SELECT opcion_servicio_id FROM ev_paquetes.item_paquete WHERE paquete_id = :pid LIMIT 1"),
                {"pid": item["referencia_id"]}
            ).scalar()
        else:  # Opción directa
            opcion_id = item["referencia_id"]

        # FLUJO: Crear o validar hold
        hold_final_id = hold_id
        
        if hold_id:
            # Validar hold existente
            hold_data = proveedores.obtener_hold(hold_id)
            if not hold_data:
                raise ValueError("HOLD_INVALIDO")
            
            from datetime import datetime
            expira_str = hold_data["expira_en"]
            # Parsear fecha (puede venir con o sin 'Z')
            if isinstance(expira_str, str):
                expira_str = expira_str.replace("Z", "").replace("+00:00", "")
                expira_dt = datetime.fromisoformat(expira_str)
            else:
                expira_dt = expira_str
                
            if expira_dt < datetime.now():
                raise ValueError("HOLD_EXPIRADO")
            
            # Confirmar hold
            try:
                proveedores.confirmar_hold(hold_id)
            except ValueError as e:
                if "HOLD_EXPIRADO" in str(e):
                    raise ValueError("HOLD_EXPIRADO")
                raise
        else:
            # Crear nuevo hold
            hold_payload = {
                "proveedor_id": proveedor_id,
                "opcion_servicio_id": opcion_id,
                "inicio": fecha_inicio,
                "fin": fecha_fin,
                "ttl_min": 30,
                "correlation_id": f"{pedido_id}-asignacion",
                "created_by": "contratacion-service"
            }
            
            try:
                hold_creado = proveedores.crear_hold(hold_payload)
                hold_final_id = hold_creado["id"]
                # Confirmar inmediatamente
                proveedores.confirmar_hold(hold_final_id)
            except ValueError as e:
                if "PROVEEDOR_NO_DISPONIBLE" in str(e):
                    raise ValueError("CONFLICTO_PROVEEDOR")
                raise

        sql_ins = text("""
            INSERT INTO ev_contratacion.reserva
                (id, item_pedido_id, proveedor_id, inicio, fin, status, hold_id, created_at)
            VALUES (UUID(), :item_id, :prov, :ini, :fin, 1, :hold, CURRENT_TIMESTAMP)
        """)
        s.execute(sql_ins, {
            "item_id": item["id"],
            "prov": proveedor_id,
            "ini": fecha_inicio,
            "fin": fecha_fin,
            "hold": hold_final_id,
        })

        s.execute(text("""
            UPDATE ev_contratacion.pedido_evento
               SET status = 3            -- ASIGNADO
             WHERE id = :pid
             LIMIT 1
        """), {"pid": pedido_id})

        row = s.execute(text("SELECT * FROM ev_contratacion.pedido_evento WHERE id=:id LIMIT 1"),
                        {"id": pedido_id}).mappings().first()
        return dict(row)
