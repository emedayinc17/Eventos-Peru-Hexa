"""
Implementación del repositorio MySQL para Catálogo
Implementa CatalogoQueryService usando las vistas de base de datos
"""
from decimal import Decimal
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
        limit: int = 50,
        offset: int = 0
    ) -> list[PaqueteResumen]:
        """Lista paquetes con monto total calculado"""
        rows = s.execute(
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
                GROUP BY d.paquete_id
                ORDER BY codigo ASC
                LIMIT :lim OFFSET :off
            """),
            {"lim": limit, "off": offset},
        ).mappings().all()

        return [
            PaqueteResumen(
                id=row["id"],
                codigo=row["codigo"],
                nombre=row["nombre"],
                moneda=row["moneda"],
                monto_total=Decimal(str(row["monto_total"])),
                descripcion=row["descripcion"],
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
