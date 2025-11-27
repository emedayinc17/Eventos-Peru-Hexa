"""
Implementación del repositorio MySQL para Catálogo
Implementa CatalogoQueryService usando las vistas de base de datos
"""
from decimal import Decimal
import uuid
from typing import Optional
from sqlalchemy import text

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
        sql = """
            SELECT id, nombre, descripcion, tipo_evento_id, status
            FROM ev_catalogo.servicio
            WHERE is_deleted = 0 AND status = 1
        """
        params = {}
        if tipo_evento_id:
            sql += " AND tipo_evento_id = :teid"
            params["teid"] = tipo_evento_id
        sql += " ORDER BY created_at DESC LIMIT :lim OFFSET :off"
        params.update({"lim": limit, "off": offset})

        rows = s.execute(text(sql), params).mappings().all()

        return [
            Servicio(
                id=row["id"],
                nombre=row["nombre"],
                tipo_evento_id=row["tipo_evento_id"],
                descripcion=row["descripcion"],
                status=row["status"]
            )
            for row in rows
        ]

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
                       v.moneda,
                       v.monto,
                       o.status
                FROM ev_catalogo.opcion_servicio o
                JOIN ev_catalogo.v_opcion_con_precio_vigente v
                  ON v.opcion_id = o.id
                WHERE o.is_deleted = 0
                  AND o.status = 1
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
                detalles=row["detalles"],
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
        
        sql = """
            SELECT
                d.paquete_id      AS id,
                MIN(d.codigo)     AS codigo,
                MIN(d.nombre)     AS nombre,
                MIN(d.descripcion) AS descripcion,
                MIN(d.status)     AS status,
                MIN(d.moneda)     AS moneda,
                SUM(d.cantidad * d.monto) AS monto_total,
                MIN(s.tipo_evento_id) AS tipo_evento_id,
                MIN(te.nombre) AS tipo_evento_nombre
            FROM ev_paquetes.v_paquete_detalle d
            LEFT JOIN ev_catalogo.opcion_servicio o ON o.id = d.opcion_servicio_id
            LEFT JOIN ev_catalogo.servicio s ON s.id = o.servicio_id
            LEFT JOIN ev_catalogo.tipo_evento te ON te.id = s.tipo_evento_id
        """
        
        params = {"lim": limit, "off": offset}
        
        if tipo_evento_id:
            sql += " WHERE s.tipo_evento_id = :teid"
            params["teid"] = tipo_evento_id
            
        sql += """
            GROUP BY d.paquete_id
            ORDER BY codigo ASC
            LIMIT :lim OFFSET :off
        """

        rows = s.execute(text(sql), params).mappings().all()

        return [
            PaqueteResumen(
                id=row["id"],
                codigo=row["codigo"],
                nombre=row["nombre"],
                moneda=row["moneda"],
                monto_total=Decimal(str(row["monto_total"])),
                descripcion=row["descripcion"],
                tipo_evento_id=row["tipo_evento_id"],
                tipo_evento_nombre=row["tipo_evento_nombre"],
                status=row["status"]
            )
            for row in rows
        ]

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
                  d.paquete_id      AS id,
                  MIN(d.codigo)     AS codigo,
                  MIN(d.nombre)     AS nombre,
                  MIN(d.descripcion) AS descripcion,
                  MIN(d.status)     AS status,
                  MIN(d.moneda)     AS moneda,
                  SUM(d.cantidad * d.monto) AS monto_total
                FROM ev_paquetes.v_paquete_detalle d
                WHERE d.paquete_id = :pid
                GROUP BY d.paquete_id
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
                opcion_detalles=row["opcion_detalles"],
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
        return {"id": new_id, "nombre": nombre}

    def update_tipo(self, s, *, tipo_id: str, nombre: str | None = None, descripcion: str | None = None) -> None:
        updates = []
        params = {"id": tipo_id}
        if nombre is not None:
            updates.append("nombre = :nombre")
            params["nombre"] = nombre
        if descripcion is not None:
            updates.append("descripcion = :descripcion")
            params["descripcion"] = descripcion
        if not updates:
            return
        sql = f"UPDATE ev_catalogo.tipo_evento SET {', '.join(updates)}, updated_at = NOW() WHERE id = :id"
        s.execute(text(sql), params)

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
        return {"id": new_id, "nombre": nombre}

    def update_servicio(self, s, *, servicio_id: str, nombre: str | None = None, descripcion: str | None = None, tipo_evento_id: str | None = None) -> None:
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
        if not updates:
            return
        sql = f"UPDATE ev_catalogo.servicio SET {', '.join(updates)}, updated_at = NOW() WHERE id = :id"
        s.execute(text(sql), params)

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
        return {"id": new_id, "nombre": nombre}

    def update_opcion(self, s, *, opcion_id: str, nombre: str | None = None, moneda: str | None = None, monto: float | None = None, detalles: str | None = None) -> None:
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

    def delete_opcion(self, s, *, opcion_id: str) -> None:
        sql = "UPDATE ev_catalogo.opcion_servicio SET is_deleted = 1, updated_at = NOW() WHERE id = :id"
        s.execute(text(sql), {"id": opcion_id})

    # --- Paquetes (básico create) ---
    def create_paquete(self, s, *, codigo: str, nombre: str, items: list, moneda: str = "PEN") -> dict:
        pid = str(uuid.uuid4())
        sql = "INSERT INTO ev_paquetes.paquete (id, codigo, nombre, moneda, status, is_deleted, created_at) VALUES (:id, :codigo, :nombre, :moneda, 1, 0, NOW())"
        s.execute(text(sql), {"id": pid, "codigo": codigo, "nombre": nombre, "moneda": moneda})
        # Insert items
        for it in items:
            s.execute(text("INSERT INTO ev_paquetes.item_paquete (paquete_id, opcion_servicio_id, cantidad, created_at) VALUES (:pid, :oid, :cant, NOW())"), {"pid": pid, "oid": it["opcion_servicio_id"], "cant": it.get("cantidad", 1)})
        return {"id": pid, "codigo": codigo}

    def update_paquete(self, s, *, paquete_id: str, nombre: str | None = None, items: list | None = None, moneda: str | None = None) -> dict:
        # Update basic fields
        params = {"id": paquete_id}
        updates = []
        if nombre is not None:
            updates.append("nombre = :nombre")
            params["nombre"] = nombre
        if moneda is not None:
            updates.append("moneda = :moneda")
            params["moneda"] = moneda
        if updates:
            sql = f"UPDATE ev_paquetes.paquete SET {', '.join(updates)}, updated_at = NOW() WHERE id = :id"
            s.execute(text(sql), params)
        # If items provided, delete existing items and insert new ones (simple replace)
        if items is not None:
            s.execute(text("DELETE FROM ev_paquetes.item_paquete WHERE paquete_id = :pid"), {"pid": paquete_id})
            for it in items:
                s.execute(text("INSERT INTO ev_paquetes.item_paquete (paquete_id, opcion_servicio_id, cantidad, created_at) VALUES (:pid, :oid, :cant, NOW())"), {"pid": paquete_id, "oid": it["opcion_servicio_id"], "cant": it.get("cantidad", 1)})
        return {"id": paquete_id}

    def delete_paquete(self, s, *, paquete_id: str) -> None:
        sql = "UPDATE ev_paquetes.paquete SET is_deleted = 1, updated_at = NOW() WHERE id = :id"
        s.execute(text(sql), {"id": paquete_id})
