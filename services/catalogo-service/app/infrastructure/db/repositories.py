"""
Implementación del repositorio MySQL para Catálogo
Implementa CatalogoQueryService usando las vistas de base de datos
"""
from decimal import Decimal
import uuid
from typing import Optional
from sqlalchemy import text, create_engine
import os
import json

from ...domain.models import (
    TipoEvento,
    Servicio,
    OpcionServicio,
    PaqueteResumen,
    PaqueteDetalle,
    ItemPaquete
)
from ...domain.exceptions import PaqueteNoEncontrado


class MySQLCatalogoQueryService:
    """
    Implementación de infraestructura del puerto CatalogoQueryService.
    Accede directamente a las vistas de MySQL (ev_catalogo.*).
    """

    def list_tipos_evento(
        self,
        s,  # SQLAlchemy session
        *,
        limit: int = 50,
        offset: int = 0
    ) -> list[TipoEvento]:
        """Lista todos los tipos de evento activos"""
        rows = s.execute(
            text("""
                SELECT id, nombre, descripcion, status
                FROM ev_catalogo.tipo_evento
                WHERE is_deleted = 0 AND status = 1
                ORDER BY created_at DESC
                LIMIT :lim OFFSET :off
            """),
            {"lim": limit, "off": offset},
        ).mappings().all()

        return [
            TipoEvento(
                id=row["id"],
                nombre=row["nombre"],
                descripcion=row["descripcion"],
                status=row["status"]
            )
            for row in rows
        ]

    def list_servicios_por_tipo(
        self,
        s,
        *,
        tipo_evento_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> list[Servicio]:
        """Lista servicios, opcionalmente filtrados por tipo de evento"""
        # NOTE: For admin UI we want to show both active and inactive services (status 1/0).
        # Previously this query filtered only `status = 1` which made services set to 0 disappear
        # from the list immediately after updating. Remove the status filter so the UI can
        # display the current `status` value and allow toggling availability.
        # Select basic servicio fields plus the most-recent opcion detalles and monto (precio vigente)
        # We use correlated subqueries to avoid returning multiple rows per servicio when there are
        # several opciones. This allows the UI to display a default category and unit price
        # without performing an N+1 request pattern from the frontend.
        sql = """
            SELECT
                s.id,
                s.nombre,
                s.descripcion,
                s.tipo_evento_id,
                s.status,
                (
                  SELECT o.detalles
                  FROM ev_catalogo.opcion_servicio o
                  WHERE o.servicio_id = s.id AND o.is_deleted = 0
                  ORDER BY o.created_at DESC
                  LIMIT 1
                ) AS opcion_detalles,
                (
                    SELECT o.categoria
                    FROM ev_catalogo.opcion_servicio o
                    WHERE o.servicio_id = s.id AND o.is_deleted = 0
                    AND o.categoria IS NOT NULL AND o.categoria != ''
                    ORDER BY o.created_at DESC
                    LIMIT 1
                ) AS opcion_categoria,
                (
                  SELECT ps.monto
                  FROM ev_catalogo.opcion_servicio o
                  JOIN ev_catalogo.precio_servicio ps ON ps.opcion_servicio_id = o.id
                  WHERE o.servicio_id = s.id AND o.is_deleted = 0
                  ORDER BY ps.vigente_desde DESC, ps.created_at DESC
                  LIMIT 1
                ) AS opcion_monto,
                (
                  SELECT o.id
                  FROM ev_catalogo.opcion_servicio o
                  WHERE o.servicio_id = s.id AND o.is_deleted = 0
                  ORDER BY o.created_at DESC
                  LIMIT 1
                ) AS opcion_id
            FROM ev_catalogo.servicio s
            WHERE s.is_deleted = 0
        """
        params = {}
        if tipo_evento_id:
            sql += " AND tipo_evento_id = :teid"
            params["teid"] = tipo_evento_id
        sql += " ORDER BY created_at DESC LIMIT :lim OFFSET :off"
        params.update({"lim": limit, "off": offset})

        rows = s.execute(text(sql), params).mappings().all()

        # Return a list of dicts containing servicio fields plus optional categoria/precio
        result = []
        for row in rows:
            # Parse detalles (may be JSON string or already a dict)
            detalles = row.get("opcion_detalles")
            try:
                if isinstance(detalles, str):
                    import json as _json
                    detalles_parsed = _json.loads(detalles) if detalles else None
                else:
                    detalles_parsed = detalles
            except Exception:
                detalles_parsed = None

            monto = row.get("opcion_monto")
            precio_unitario = None
            if monto is not None:
                try:
                    precio_unitario = float(monto)
                except Exception:
                    precio_unitario = None

            categoria = None
            # Prefer category inside detalles JSON, fallback to opcion_categoria_json (which is actually detalles)
            if detalles_parsed and isinstance(detalles_parsed, dict):
                categoria = detalles_parsed.get("categoria") or detalles_parsed.get("category")
            
            if not categoria:
                # row may include opcion_categoria selected from the opcion_servicio table
                categoria = row.get("opcion_categoria")

            result.append({
                "id": row["id"],
                "nombre": row["nombre"],
                "tipo_evento_id": row.get("tipo_evento_id"),
                "descripcion": row.get("descripcion"),
                "status": row.get("status"),
                # Optional fields for frontend convenience
                "categoria": categoria,
                "precio_unitario": precio_unitario,
                "opcion_detalles": detalles_parsed,
                "opcion_id": row.get("opcion_id"),
            })

        return result

    def list_opciones_por_servicio(
        self,
        s,
        *,
        servicio_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> list[OpcionServicio]:
        """Lista opciones de un servicio con precios vigentes"""
        rows = s.execute(
            text("""
                SELECT o.id,
                       o.servicio_id,
                       o.nombre,
                       o.detalles,
                       COALESCE(ps.moneda, 'PEN') as moneda,
                       COALESCE(ps.monto, 0) as monto,
                       o.status
                FROM ev_catalogo.opcion_servicio o
                LEFT JOIN (
                    SELECT opcion_servicio_id, moneda, monto,
                           ROW_NUMBER() OVER (PARTITION BY opcion_servicio_id ORDER BY vigente_desde DESC, created_at DESC) as rn
                    FROM ev_catalogo.precio_servicio
                    WHERE vigente_desde <= DATE_ADD(CURDATE(), INTERVAL 2 DAY)
                ) ps ON ps.opcion_servicio_id = o.id AND ps.rn = 1
                WHERE o.is_deleted = 0
                    AND o.servicio_id = :sid
                ORDER BY o.created_at DESC
                LIMIT :lim OFFSET :off
            """),
            {"sid": servicio_id, "lim": limit, "off": offset},
        ).mappings().all()

        return [
            OpcionServicio(
                id=row["id"],
                servicio_id=row["servicio_id"],
                nombre=row["nombre"],
                moneda=row["moneda"],
                monto=Decimal(str(row["monto"])),
                detalles=(json.loads(row["detalles"]) if isinstance(row["detalles"], str) else row["detalles"]),
                status=row["status"]
            )
            for row in rows
        ]

    def list_paquetes(
        self,
        s,
        *,
        tipo_evento_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> list[PaqueteResumen]:
        """Lista paquetes con monto total calculado y tipo de evento"""
        
        # Updated query to fetch from root table and join everything properly
        # Also fetches price from ev_paquetes.precio_paquete (base price)
        sql = """
            SELECT
                p.id,
                p.codigo,
                p.nombre,
                p.descripcion,
                p.status,
                COALESCE(pp.moneda, 'PEN') AS moneda,
                COALESCE(pp.monto, 0) AS monto_total,
                MAX(s.tipo_evento_id) AS tipo_evento_id,
                MAX(te.nombre) AS tipo_evento_nombre,
                GROUP_CONCAT(DISTINCT CONCAT(s.id, '::', s.nombre) SEPARATOR '||') AS servicios_concat
            FROM ev_paquetes.paquete p
            LEFT JOIN (
                SELECT paquete_id, moneda, monto
                FROM ev_paquetes.precio_paquete
                WHERE vigente_desde <= DATE_ADD(CURDATE(), INTERVAL 2 DAY)
                AND (vigente_hasta IS NULL OR vigente_hasta >= CURDATE())
                AND id IN (
                    SELECT id FROM (
                        SELECT id, ROW_NUMBER() OVER (PARTITION BY paquete_id ORDER BY vigente_desde DESC, created_at DESC) as rn
                        FROM ev_paquetes.precio_paquete
                        WHERE vigente_desde <= DATE_ADD(CURDATE(), INTERVAL 2 DAY)
                    ) t WHERE t.rn = 1
                )
            ) pp ON pp.paquete_id = p.id
            LEFT JOIN ev_paquetes.item_paquete ip ON ip.paquete_id = p.id
            LEFT JOIN ev_catalogo.opcion_servicio os ON os.id = ip.opcion_servicio_id
            LEFT JOIN ev_catalogo.servicio s ON s.id = os.servicio_id
            LEFT JOIN ev_catalogo.tipo_evento te ON te.id = s.tipo_evento_id
            WHERE p.is_deleted = 0
        """
        
        params = {"lim": limit, "off": offset}
        
        if tipo_evento_id:
            sql += " AND s.tipo_evento_id = :teid"
            params["teid"] = tipo_evento_id
            
        sql += """
            GROUP BY p.id, p.codigo, p.nombre, p.descripcion, p.status, pp.moneda, pp.monto
            ORDER BY p.created_at DESC
            LIMIT :lim OFFSET :off
        """

        try:
            rows = s.execute(text(sql), params).mappings().all()
        except Exception as e:
            import logging
            logging.getLogger("catalogo.repository").error(f"Error in list_paquetes: {e}")
            # Fallback to empty list or re-raise depending on severity. 
            # For now, let's return empty to avoid crashing the UI completely if just one query fails.
            return []

        result = []
        for row in rows:
            # Parse servicios_concat into array of {id, nombre}
            servicios_list = []
            sc = row.get("servicios_concat")
            if sc:
                try:
                    parts = sc.split('||')
                    for p in parts:
                        if '::' in p:
                            sid, sname = p.split('::', 1)
                            servicios_list.append({"id": sid, "nombre": sname})
                except Exception:
                    servicios_list = []

            result.append({
                "id": row["id"],
                "codigo": row["codigo"],
                "nombre": row["nombre"],
                "moneda": row["moneda"],
                "monto_total": Decimal(str(row["monto_total"])),
                "descripcion": row["descripcion"],
                "tipo_evento_id": row.get("tipo_evento_id"),
                "tipo_evento_nombre": row.get("tipo_evento_nombre"),
                "status": row.get("status"),
                "servicios": servicios_list,
            })

        return result

    def get_paquete_detalle(
        self,
        s,
        *,
        paquete_id: str
    ) -> Optional[PaqueteDetalle]:
        """Obtiene detalle completo de un paquete con sus items"""
        # 1. Obtener cabecera agregada
        head = s.execute(
            text("""
                SELECT
                  p.id              AS id,
                  p.codigo          AS codigo,
                  p.nombre          AS nombre,
                  p.descripcion     AS descripcion,
                  p.status          AS status,
                  COALESCE(pp.moneda, 'PEN') AS moneda,
                  COALESCE(pp.monto, 0)      AS monto_total
                FROM ev_paquetes.paquete p
                LEFT JOIN ev_paquetes.precio_paquete pp ON pp.paquete_id = p.id
                     AND pp.vigente_desde <= CURRENT_DATE()
                     AND (pp.vigente_hasta IS NULL OR pp.vigente_hasta >= CURRENT_DATE())
                WHERE p.id = :pid
                LIMIT 1
            """),
            {"pid": paquete_id},
        ).mappings().first()

        if not head:
            raise PaqueteNoEncontrado(paquete_id)

        # 2. Obtener items del paquete
        items_rows = s.execute(
            text("""
                SELECT
                    d.opcion_servicio_id,
                    d.cantidad,
                    d.moneda,
                    d.monto AS precio_unit_vigente,
                    o.nombre AS opcion_nombre,
                    o.detalles AS opcion_detalles,
                    s.id AS servicio_id,
                    s.nombre AS servicio_nombre,
                    s.descripcion AS servicio_descripcion
                FROM ev_paquetes.v_paquete_detalle d
                LEFT JOIN ev_catalogo.opcion_servicio o ON o.id = d.opcion_servicio_id
                LEFT JOIN ev_catalogo.servicio s ON s.id = o.servicio_id
                WHERE d.paquete_id = :pid
            """),
            {"pid": paquete_id},
        ).mappings().all()

        # 3. Obtener proveedores agrupados por servicio
        servicio_ids = sorted({i["servicio_id"] for i in items_rows if i.get("servicio_id")})
        proveedores_map = {}
        if servicio_ids:
            # Construir lista segura de IDs para IN
            placeholders = ",".join([f"'{sid}'" for sid in servicio_ids])
            prov_sql = f"""
                SELECT DISTINCT
                  hp.servicio_id,
                  p.id AS proveedor_id,
                  p.nombre AS proveedor_nombre,
                  p.email,
                  p.telefono,
                  p.rating_prom,
                  hp.nivel
                FROM ev_proveedores.habilidad_proveedor hp
                JOIN ev_proveedores.proveedor p ON p.id = hp.proveedor_id
                WHERE hp.servicio_id IN ({placeholders})
                  AND p.is_deleted = 0
                  AND p.status = 1
                ORDER BY p.nombre
            """
            prov_rows = s.execute(text(prov_sql)).mappings().all()
            for r in prov_rows:
                sid = r["servicio_id"]
                proveedores_map.setdefault(sid, []).append(dict(r))

        # 4. Construir items con sus proveedores
        items = [
            ItemPaquete(
                opcion_servicio_id=row["opcion_servicio_id"],
                cantidad=row["cantidad"],
                precio_unit_vigente=Decimal(str(row["precio_unit_vigente"])),
                moneda=row["moneda"],
                opcion_nombre=row["opcion_nombre"],
                    opcion_detalles=(json.loads(row["opcion_detalles"]) if isinstance(row.get("opcion_detalles"), str) else row.get("opcion_detalles")),
                servicio_id=row["servicio_id"],
                servicio_nombre=row["servicio_nombre"],
                servicio_descripcion=row["servicio_descripcion"],
                proveedores=proveedores_map.get(row["servicio_id"], [])
            )
            for row in items_rows
        ]

        # 5. Retornar paquete completo
        return PaqueteDetalle(
            id=head["id"],
            codigo=head["codigo"],
            nombre=head["nombre"],
            moneda=head["moneda"],
            monto_total=Decimal(str(head["monto_total"])),
            items=items,
            descripcion=head["descripcion"],
            status=head["status"]
        )


class MySQLCatalogoCommandRepository:
    """Repositorio de comandos para Catálogo (create/update/delete)."""

    def create_tipo(self, s, *, nombre: str, descripcion: str | None = None) -> dict:
        # Generar UUID localmente para evitar dependencias en la columna auto-inc
        new_id = str(uuid.uuid4())
        sql = """
        INSERT INTO ev_catalogo.tipo_evento (id, nombre, descripcion, status, is_deleted, created_at)
        VALUES (:id, :nombre, :descripcion, 1, 0, NOW())
        """
        s.execute(text(sql), {"id": new_id, "nombre": nombre, "descripcion": descripcion})
        return {"id": new_id, "nombre": nombre, "descripcion": descripcion, "status": 1}

    def update_tipo(self, s, *, tipo_id: str, nombre: str | None = None, descripcion: str | None = None) -> dict:
        updates = []
        params = {"id": tipo_id}
        if nombre is not None:
            updates.append("nombre = :nombre")
            params["nombre"] = nombre
        if descripcion is not None:
            updates.append("descripcion = :descripcion")
            params["descripcion"] = descripcion
        if not updates:
            # Si no hay cambios, devolver el objeto actual
            row = s.execute(
                text("SELECT id, nombre, descripcion, status FROM ev_catalogo.tipo_evento WHERE id = :id"),
                {"id": tipo_id}
            ).mappings().first()
            return dict(row) if row else {"id": tipo_id}
        
        sql = f"UPDATE ev_catalogo.tipo_evento SET {', '.join(updates)}, updated_at = NOW() WHERE id = :id"
        s.execute(text(sql), params)
        
        # Fetch and return the updated object
        row = s.execute(
            text("SELECT id, nombre, descripcion, status FROM ev_catalogo.tipo_evento WHERE id = :id"),
            {"id": tipo_id}
        ).mappings().first()
        
        return dict(row) if row else {"id": tipo_id}

    def delete_tipo(self, s, *, tipo_id: str) -> None:
        sql = "UPDATE ev_catalogo.tipo_evento SET is_deleted = 1, updated_at = NOW() WHERE id = :id"
        s.execute(text(sql), {"id": tipo_id})

    # --- Servicios ---
    def create_servicio(self, s, *, nombre: str, tipo_evento_id: str, descripcion: str | None = None) -> dict:
        new_id = str(uuid.uuid4())
        sql = """
        INSERT INTO ev_catalogo.servicio (id, nombre, descripcion, tipo_evento_id, status, is_deleted, created_at)
        VALUES (:id, :nombre, :descripcion, :tipo_evento_id, 1, 0, NOW())
        """
        s.execute(text(sql), {"id": new_id, "nombre": nombre, "descripcion": descripcion, "tipo_evento_id": tipo_evento_id})
        return {"id": new_id, "nombre": nombre, "descripcion": descripcion, "tipo_evento_id": tipo_evento_id, "status": 1}

    def update_servicio(self, s, *, servicio_id: str, nombre: str | None = None, descripcion: str | None = None, tipo_evento_id: str | None = None, status: int | None = None) -> dict:
        updates = []
        params = {"id": servicio_id}
        if nombre is not None:
            updates.append("nombre = :nombre")
            params["nombre"] = nombre
        if descripcion is not None:
            updates.append("descripcion = :descripcion")
            params["descripcion"] = descripcion
        if tipo_evento_id is not None:
            updates.append("tipo_evento_id = :tipo_evento_id")
            params["tipo_evento_id"] = tipo_evento_id
        if status is not None:
            updates.append("status = :status")
            params["status"] = int(status)
        if not updates:
            row = s.execute(
                text("SELECT id, nombre, descripcion, tipo_evento_id, status FROM ev_catalogo.servicio WHERE id = :id"),
                {"id": servicio_id}
            ).mappings().first()
            return dict(row) if row else {"id": servicio_id}
            
        sql = f"UPDATE ev_catalogo.servicio SET {', '.join(updates)}, updated_at = NOW() WHERE id = :id"
        s.execute(text(sql), params)
        
        row = s.execute(
            text("SELECT id, nombre, descripcion, tipo_evento_id, status FROM ev_catalogo.servicio WHERE id = :id"),
            {"id": servicio_id}
        ).mappings().first()
        return dict(row) if row else {"id": servicio_id}

    def delete_servicio(self, s, *, servicio_id: str) -> None:
        sql = "UPDATE ev_catalogo.servicio SET is_deleted = 1, updated_at = NOW() WHERE id = :id"
        s.execute(text(sql), {"id": servicio_id})

    # --- Opciones ---
    def create_opcion(self, s, *, servicio_id: str, nombre: str, moneda: str, monto: float, detalles: str | None = None) -> dict:
        import json
        new_id = str(uuid.uuid4())
        
        # Serializar detalles si es dict/list
        detalles_json = None
        if detalles is not None:
            if isinstance(detalles, (dict, list)):
                detalles_json = json.dumps(detalles)
            else:
                detalles_json = detalles
        
        sql = """
        INSERT INTO ev_catalogo.opcion_servicio (id, servicio_id, nombre, detalles, status, is_deleted, created_at)
        VALUES (:id, :servicio_id, :nombre, :detalles, 1, 0, NOW())
        """
        s.execute(text(sql), {"id": new_id, "servicio_id": servicio_id, "nombre": nombre, "detalles": detalles_json})
        # Insertar precio inicial en tabla de precios
        s.execute(
            text("""
                INSERT INTO ev_catalogo.precio_servicio 
                (id, opcion_servicio_id, moneda, monto, vigente_desde, created_at) 
                VALUES (:id, :opcion_id, :moneda, :monto, CURDATE(), NOW())
            """), 
            {"id": str(uuid.uuid4()), "opcion_id": new_id, "moneda": moneda, "monto": monto}
        )
        return {"id": new_id, "nombre": nombre, "servicio_id": servicio_id, "moneda": moneda, "monto": monto, "detalles": detalles, "status": 1}

    def update_opcion(self, s, *, opcion_id: str, nombre: str | None = None, moneda: str | None = None, monto: float | None = None, detalles: str | None = None) -> dict:
        import json
        updates = []
        params = {"id": opcion_id}
        if nombre is not None:
            updates.append("nombre = :nombre")
            params["nombre"] = nombre
        if detalles is not None:
            # Serializar detalles si es dict/list
            if isinstance(detalles, (dict, list)):
                params["detalles"] = json.dumps(detalles)
            else:
                params["detalles"] = detalles
            updates.append("detalles = :detalles")
        if updates:
            sql = f"UPDATE ev_catalogo.opcion_servicio SET {', '.join(updates)}, updated_at = NOW() WHERE id = :id"
            s.execute(text(sql), params)
        # Si cambia el precio, crear una nueva fila de precio (registro histórico)
        if monto is not None and moneda is not None:
            s.execute(
                text("""
                    INSERT INTO ev_catalogo.precio_servicio 
                    (id, opcion_servicio_id, moneda, monto, vigente_desde, created_at) 
                    VALUES (:id, :opcion_id, :moneda, :monto, CURDATE(), NOW())
                """), 
                {"id": str(uuid.uuid4()), "opcion_id": opcion_id, "moneda": moneda, "monto": monto}
            )
            
        # Fetch updated object
        row = s.execute(
            text("SELECT id, servicio_id, nombre, detalles, status FROM ev_catalogo.opcion_servicio WHERE id = :id"),
            {"id": opcion_id}
        ).mappings().first()
        
        result = dict(row) if row else {"id": opcion_id}
        
        # Get current price
        price_row = s.execute(
            text("SELECT moneda, monto FROM ev_catalogo.precio_servicio WHERE opcion_servicio_id = :id ORDER BY created_at DESC LIMIT 1"),
            {"id": opcion_id}
        ).mappings().first()
        
        if price_row:
            result.update(dict(price_row))
            
        return result

    def delete_opcion(self, s, *, opcion_id: str) -> None:
        sql = "UPDATE ev_catalogo.opcion_servicio SET is_deleted = 1, updated_at = NOW() WHERE id = :id"
        s.execute(text(sql), {"id": opcion_id})

    # --- Paquetes (básico create) ---
    def create_paquete(self, s, *, codigo: str, nombre: str, items: list, moneda: str = "PEN", descripcion: str | None = None, monto: float | None = None) -> dict:
        # Use the dedicated paquetes DB account for writes into ev_paquetes to avoid permission errors
        pid = str(uuid.uuid4())
        paq_user = os.getenv('PAQUETES_DB_USER', os.getenv('app_paquetes_user', 'app_paquetes'))
        paq_pass = os.getenv('PAQUETES_DB_PASS', os.getenv('app_paquetes_pass', 'Pkg_2025'))
        paq_host = os.getenv('PAQUETES_DB_HOST', os.getenv('DB_HOST', 'localhost'))
        paq_port = int(os.getenv('PAQUETES_DB_PORT', os.getenv('DB_PORT', '3306')))
        paq_db = os.getenv('PAQUETES_DB_NAME', 'ev_paquetes')
        engine_url = f"mysql+pymysql://{paq_user}:{paq_pass}@{paq_host}:{paq_port}/{paq_db}"
        engine = create_engine(engine_url)
        try:
            with engine.begin() as conn:
                conn.execute(text("INSERT INTO ev_paquetes.paquete (id, codigo, nombre, descripcion, moneda, status, is_deleted, created_at) VALUES (:id, :codigo, :nombre, :descripcion, :moneda, 1, 0, NOW())"), {"id": pid, "codigo": codigo, "nombre": nombre, "descripcion": descripcion, "moneda": moneda})
                for it in items:
                    conn.execute(text("INSERT INTO ev_paquetes.item_paquete (id, paquete_id, opcion_servicio_id, cantidad, created_at) VALUES (:iid, :pid, :oid, :cant, NOW())"), {"iid": str(uuid.uuid4()), "pid": pid, "oid": it["opcion_servicio_id"], "cant": it.get("cantidad", 1)})
                
                # Insert price if provided
                if monto is not None:
                    conn.execute(text("INSERT INTO ev_paquetes.precio_paquete (id, paquete_id, moneda, monto, vigente_desde, created_at) VALUES (:id, :pid, :moneda, :monto, CURDATE(), NOW())"), {"id": str(uuid.uuid4()), "pid": pid, "moneda": moneda, "monto": monto})
        finally:
            engine.dispose()

        return {"id": pid, "codigo": codigo, "nombre": nombre, "descripcion": descripcion, "moneda": moneda, "items": items, "status": 1, "monto": monto}

    def update_paquete(self, s, *, paquete_id: str, nombre: str | None = None, items: list | None = None, moneda: str | None = None, descripcion: str | None = None, monto: float | None = None) -> dict:
        try:
            # Use the dedicated paquetes DB account for writes into ev_paquetes
            paq_user = os.getenv('PAQUETES_DB_USER', os.getenv('app_paquetes_user', 'app_paquetes'))
            paq_pass = os.getenv('PAQUETES_DB_PASS', os.getenv('app_paquetes_pass', 'Pkg_2025'))
            paq_host = os.getenv('PAQUETES_DB_HOST', os.getenv('DB_HOST', 'localhost'))
            paq_port = int(os.getenv('PAQUETES_DB_PORT', os.getenv('DB_PORT', '3306')))
            paq_db = os.getenv('PAQUETES_DB_NAME', 'ev_paquetes')
            engine_url = f"mysql+pymysql://{paq_user}:{paq_pass}@{paq_host}:{paq_port}/{paq_db}"
            engine = create_engine(engine_url)
            
            with engine.begin() as conn:
                updates = []
                params = {"id": paquete_id}
                if nombre:
                    updates.append("nombre = :nombre")
                    params["nombre"] = nombre
                if descripcion:
                    updates.append("descripcion = :descripcion")
                    params["descripcion"] = descripcion
                if moneda:
                    updates.append("moneda = :moneda")
                    params["moneda"] = moneda
                
                if updates:
                    sql = f"UPDATE ev_paquetes.paquete SET {', '.join(updates)}, updated_at = NOW() WHERE id = :id"
                    conn.execute(text(sql), params)

                if monto is not None:
                    m_curr = moneda if moneda else 'PEN'
                    # Delete existing prices for today and future to ensure this new price takes precedence
                    conn.execute(text("DELETE FROM ev_paquetes.precio_paquete WHERE paquete_id = :pid AND vigente_desde >= CURDATE()"), {"pid": paquete_id})
                    
                    sql_price = """
                        INSERT INTO ev_paquetes.precio_paquete (id, paquete_id, moneda, monto, vigente_desde, created_at) 
                        VALUES (:id, :pid, :moneda, :monto, CURDATE(), NOW())
                    """
                    conn.execute(text(sql_price), {"id": str(uuid.uuid4()), "pid": paquete_id, "moneda": m_curr, "monto": monto})

                if items is not None:
                    conn.execute(text("DELETE FROM ev_paquetes.item_paquete WHERE paquete_id = :pid"), {"pid": paquete_id})
                    for it in items:
                        conn.execute(text("INSERT INTO ev_paquetes.item_paquete (id, paquete_id, opcion_servicio_id, cantidad, created_at) VALUES (:iid, :pid, :oid, :cant, NOW())"), {"iid": str(uuid.uuid4()), "pid": paquete_id, "oid": it["opcion_servicio_id"], "cant": it.get("cantidad", 1)})
        finally:
            engine.dispose()

        return {"id": paquete_id}

    def delete_paquete(self, s, *, paquete_id: str) -> None:
        try:
            # Use the dedicated paquetes DB account for writes into ev_paquetes
            paq_user = os.getenv('PAQUETES_DB_USER', os.getenv('app_paquetes_user', 'app_paquetes'))
            paq_pass = os.getenv('PAQUETES_DB_PASS', os.getenv('app_paquetes_pass', 'Pkg_2025'))
            paq_host = os.getenv('PAQUETES_DB_HOST', os.getenv('DB_HOST', 'localhost'))
            paq_port = int(os.getenv('PAQUETES_DB_PORT', os.getenv('DB_PORT', '3306')))
            paq_db = os.getenv('PAQUETES_DB_NAME', 'ev_paquetes')
            engine_url = f"mysql+pymysql://{paq_user}:{paq_pass}@{paq_host}:{paq_port}/{paq_db}"
            engine = create_engine(engine_url)
            
            with engine.begin() as conn:
                conn.execute(text("UPDATE ev_paquetes.paquete SET is_deleted = 1, updated_at = NOW() WHERE id = :id"), {"id": paquete_id})
            
            engine.dispose()
        except Exception as e:
            with open("e:\\eventos-peru-hexagonal\\last_error_delete.txt", "w") as f:
                f.write(str(e))
            raise e
