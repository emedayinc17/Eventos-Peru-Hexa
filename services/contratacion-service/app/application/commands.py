from typing import Dict, Any, List, Optional
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from ev_shared.config import Settings
from ev_shared.db import session_scope

# IMPORT corregido: NUNCA uses "contratacion-service" con guion en imports
# Usa import absoluto dentro del paquete app (o relativo si prefieres).
from app.infrastructure.db.sqlalchemy.repositories import EmailOutboxSql


# ========= Helpers de cálculo =========

def _calcular_total_paquete(settings: Settings, paquete_id: str) -> Dict[str, Any]:
    sql = text("""
        SELECT paquete_id, moneda, monto_total_vigente
        FROM ev_paquetes.v_paquete_precio_vigente_total
        WHERE paquete_id = :pid
        LIMIT 1
    """)
    with session_scope(settings) as s:
        row = s.execute(sql, {"pid": paquete_id}).mappings().first()
        if not row:
            raise ValueError("PAQUETE_SIN_PRECIO_VIGENTE")
        return dict(row)


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
    tot = _calcular_total_paquete(settings, payload["paquete_id"])
    status_inicial = 1  # COTIZADO

    sql_tipo = text("""
        SELECT s.tipo_evento_id
        FROM ev_paquetes.item_paquete ip
        JOIN ev_catalogo.opcion_servicio o ON o.id = ip.opcion_servicio_id
        JOIN ev_catalogo.servicio s ON s.id = o.servicio_id
        WHERE ip.paquete_id = :pid
        LIMIT 1
    """)

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

    sql_insert_item = text("""
        INSERT INTO ev_contratacion.item_pedido_evento
            (id, pedido_id, tipo_item, referencia_id, cantidad, precio_unit, precio_total, created_at)
        VALUES (UUID(), :pedido_id, 2, :paquete_id, 1, :precio_unit, :precio_total, CURRENT_TIMESTAMP)
    """)

    with session_scope(settings) as s:
        trow = s.execute(sql_tipo, {"pid": payload["paquete_id"]}).first()
        if not trow:
            raise ValueError("PAQUETE_SIN_ITEMS")

        tipo_evento_id = trow[0]

        try:
            s.execute(sql_insert_pedido, {
                "cliente_id": cliente_id,
                "tipo_evento_id": tipo_evento_id,
                "fecha_evento": payload["fecha_evento"],
                "hora_inicio": payload["hora_inicio"],
                "hora_fin": payload.get("hora_fin"),
                "ubicacion": payload["ubicacion"],
                "monto_total": float(tot["monto_total_vigente"]),
                "moneda": tot["moneda"],
                "status": status_inicial,
                "correlation_id": payload.get("correlation_id"),
                "request_id": payload.get("request_id"),
            })
        except IntegrityError:
            row = s.execute(sql_get_by_req, {"req": payload.get("request_id")}).mappings().first()
            if row:
                return dict(row)
            raise

        prow = s.execute(sql_get_by_req, {"req": payload.get("request_id")}).mappings().first()
        pedido_id = prow["id"]

        s.execute(sql_insert_item, {
            "pedido_id": pedido_id,
            "paquete_id": payload["paquete_id"],
            "precio_unit": float(tot["monto_total_vigente"]),
            "precio_total": float(tot["monto_total_vigente"]),
        })

        return dict(prow)


def crear_pedido_custom(settings: Settings, cliente_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    calc = _calcular_items_custom(settings, [dict(x) for x in payload["items"]])
    status_inicial = 1 if calc["total"] > 0 else 0  # COTIZADO si hay total; DRAFT si no

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
                "correlation_id": payload.get("correlation_id"),
                "request_id": payload.get("request_id"),
            })
        except IntegrityError:
            row = s.execute(sql_get_by_req, {"req": payload.get("request_id")}).mappings().first()
            if row:
                return dict(row)
            raise

        prow = s.execute(sql_get_by_req, {"req": payload.get("request_id")}).mappings().first()
        pedido_id = prow["id"]

        for it in calc["items_calculados"]:
            s.execute(sql_insert_item, {
                "pedido_id": pedido_id,
                "opcion_servicio_id": it["opcion_servicio_id"],
                "cantidad": it["cantidad"],
                "precio_unit": it["precio_unit"],
                "precio_total": it["precio_total"],
            })

        return dict(prow)


def listar_mis_pedidos(settings: Settings, cliente_id: str) -> List[Dict[str, Any]]:
    sql = text("""
        SELECT * FROM ev_contratacion.v_pedido_con_cliente
        WHERE cliente_id = :uid
        ORDER BY created_at DESC
    """)
    with session_scope(settings) as s:
        rows = s.execute(sql, {"uid": cliente_id}).mappings().all()
        return [dict(r) for r in rows]


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
    ped = _get_pedido_row(settings, pedido_id)
    if not ped:
        raise ValueError("PEDIDO_NO_ENCONTRADO")

    # Estado mínimo: APROBADO (2)
    if int(ped["status"]) < 2:
        raise ValueError("ESTADO_NO_PERMITE_ASIGNACION")

    if hold_id and not _hold_valido(settings, hold_id, proveedor_id, fecha_inicio, fecha_fin):
        raise ValueError("HOLD_INVALIDO")

    if _hay_conflicto_asignacion(settings, proveedor_id, fecha_inicio, fecha_fin):
        raise ValueError("CONFLICTO_PROVEEDOR")

    # La tabla ev_contratacion.reserva exige item_pedido_id.
    # Para MVP: usamos el PRIMER item del pedido.
    sql_item = text("""
        SELECT id
          FROM ev_contratacion.item_pedido_evento
         WHERE pedido_id = :pid
         ORDER BY created_at ASC
         LIMIT 1
    """)
    with session_scope(settings) as s:
        item = s.execute(sql_item, {"pid": pedido_id}).mappings().first()
        if not item:
            raise ValueError("PEDIDO_SIN_ITEMS")

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
            "hold": hold_id,
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
