"""
Implementación de repositorios MySQL para Proveedores
Implementan ProveedorQueryPort y HoldsCommandPort
"""
from decimal import Decimal
from typing import Optional
from datetime import datetime, date
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from ...domain.models import Proveedor, Hold
from ...domain.exceptions import (
    HoldNoEncontrado,
    HoldExpirado,
    HoldInvalidoError,
    ConflictoDisponibilidadError,
    RangoTiempoInvalido,
)


class MySQLProveedorQueryRepository:
    """
    Implementación de infraestructura del puerto ProveedorQueryPort.
    Consulta proveedores disponibles usando vistas y validaciones de conflictos.
    """

    def buscar_disponibles(
        self,
        s,  # SQLAlchemy session
        *,
        servicio_id: str,
        fecha: date,
        limit: int = 50,
        offset: int = 0
    ) -> list[Proveedor]:
        """
        Busca proveedores disponibles para un servicio en una fecha.
        Maneja fallback si no tiene permisos para ev_contratacion.reserva.
        """
        start = f"{fecha} 00:00:00"
        end = f"{fecha} 23:59:59"

        # SQL completo (con validación de ev_contratacion.reserva)
        sql_full = text("""
            SELECT
              p.id, p.nombre, p.email, p.telefono, p.rating_prom, p.status
            FROM ev_proveedores.proveedor p
            JOIN ev_proveedores.habilidad_proveedor h
              ON h.proveedor_id = p.id AND h.servicio_id = :sid
            WHERE p.is_deleted = 0 AND p.status = 1
              AND NOT EXISTS (
                SELECT 1
                FROM ev_proveedores.reserva_temporal rt
                WHERE rt.proveedor_id = p.id
                  AND rt.status IN (0,1)
                  AND rt.expira_en > NOW()
                  AND rt.inicio < :end_dt AND rt.fin > :start_dt
              )
              AND NOT EXISTS (
                SELECT 1
                FROM ev_contratacion.reserva r
                WHERE r.proveedor_id = p.id
                  AND r.status = 1
                  AND r.inicio < :end_dt AND r.fin > :start_dt
              )
              AND NOT EXISTS (
                SELECT 1
                FROM ev_proveedores.calendario_proveedor c
                WHERE c.proveedor_id = p.id
                  AND c.tipo = 2
                  AND c.inicio < :end_dt AND c.fin > :start_dt
              )
            ORDER BY p.rating_prom DESC, p.nombre ASC
            LIMIT :lim OFFSET :off
        """)

        # SQL fallback (sin ev_contratacion.reserva)
        sql_fallback = text("""
            SELECT
              p.id, p.nombre, p.email, p.telefono, p.rating_prom, p.status
            FROM ev_proveedores.proveedor p
            JOIN ev_proveedores.habilidad_proveedor h
              ON h.proveedor_id = p.id AND h.servicio_id = :sid
            WHERE p.is_deleted = 0 AND p.status = 1
              AND NOT EXISTS (
                SELECT 1
                FROM ev_proveedores.reserva_temporal rt
                WHERE rt.proveedor_id = p.id
                  AND rt.status IN (0,1)
                  AND rt.expira_en > NOW()
                  AND rt.inicio < :end_dt AND rt.fin > :start_dt
              )
              AND NOT EXISTS (
                SELECT 1
                FROM ev_proveedores.calendario_proveedor c
                WHERE c.proveedor_id = p.id
                  AND c.tipo = 2
                  AND c.inicio < :end_dt AND c.fin > :start_dt
              )
            ORDER BY p.rating_prom DESC, p.nombre ASC
            LIMIT :lim OFFSET :off
        """)

        params = {"sid": servicio_id, "start_dt": start, "end_dt": end, "lim": limit, "off": offset}

        try:
            rows = s.execute(sql_full, params).mappings().all()
        except SQLAlchemyError as e:
            # Detecta permiso denegado (MySQL error 1142)
            orig = getattr(e, "orig", None)
            if orig and hasattr(orig, "args") and len(orig.args) >= 1 and orig.args[0] == 1142:
                rows = s.execute(sql_fallback, params).mappings().all()
            else:
                raise

        return [
            Proveedor(
                id=row["id"],
                nombre=row["nombre"],
                rating_prom=Decimal(str(row["rating_prom"])),
                email=row["email"],
                telefono=row["telefono"],
                status=row["status"]
            )
            for row in rows
        ]


class MySQLHoldsRepository:
    """
    Implementación de infraestructura del puerto HoldsCommandPort.
    Gestiona holds (reservas temporales) con validaciones de conflictos.
    """

    def crear_hold(
        self,
        s,
        *,
        proveedor_id: str,
        opcion_servicio_id: str,
        inicio: datetime,
        fin: datetime,
        ttl_min: int = 30,
        correlation_id: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> Hold:
        """Crea hold con idempotencia y validaciones de conflictos"""
        
        # Validar rango
        if inicio >= fin:
            raise RangoTiempoInvalido("Fecha fin debe ser posterior a inicio")

        # IDEMPOTENCIA: verificar si ya existe
        if correlation_id:
            existing = s.execute(
                text("""
                    SELECT id, proveedor_id, opcion_servicio_id, inicio, fin, 
                           expira_en, status, correlation_id, created_by
                    FROM ev_proveedores.reserva_temporal
                    WHERE proveedor_id = :pid
                      AND correlation_id = :corr
                      AND status IN (0, 1)
                    ORDER BY created_at DESC
                    LIMIT 1
                """),
                {"pid": proveedor_id, "corr": correlation_id},
            ).mappings().first()

            if existing:
                return Hold(
                    id=existing["id"],
                    proveedor_id=existing["proveedor_id"],
                    opcion_servicio_id=existing["opcion_servicio_id"],
                    inicio=existing["inicio"],
                    fin=existing["fin"],
                    expira_en=existing["expira_en"],
                    status=existing["status"],
                    correlation_id=existing["correlation_id"],
                    created_by=existing["created_by"],
                )

        # Validar conflictos con holds
        conflict_hold = s.execute(
            text("""
                SELECT id FROM ev_proveedores.reserva_temporal
                WHERE proveedor_id = :pid
                  AND status IN (0,1)
                  AND expira_en > NOW()
                  AND inicio < :fin AND fin > :ini
                LIMIT 1
            """),
            {"pid": proveedor_id, "ini": inicio, "fin": fin},
        ).first()
        if conflict_hold:
            raise ConflictoDisponibilidadError(proveedor_id, "Hold activo existente")

        # Validar conflictos con reservas (con fallback si no hay permisos)
        try:
            conflict_res = s.execute(
                text("""
                    SELECT id FROM ev_contratacion.reserva
                    WHERE proveedor_id = :pid
                      AND status = 1
                      AND inicio < :fin AND fin > :ini
                    LIMIT 1
                """),
                {"pid": proveedor_id, "ini": inicio, "fin": fin},
            ).first()
            if conflict_res:
                raise ConflictoDisponibilidadError(proveedor_id, "Reserva confirmada existente")
        except SQLAlchemyError as e:
            orig = getattr(e, "orig", None)
            if not (orig and hasattr(orig, "args") and len(orig.args) >= 1 and orig.args[0] == 1142):
                raise

        # Validar conflictos con descansos
        conflict_desc = s.execute(
            text("""
                SELECT id FROM ev_proveedores.calendario_proveedor
                WHERE proveedor_id = :pid
                  AND tipo = 2
                  AND inicio < :fin AND fin > :ini
                LIMIT 1
            """),
            {"pid": proveedor_id, "ini": inicio, "fin": fin},
        ).first()
        if conflict_desc:
            raise ConflictoDisponibilidadError(proveedor_id, "Proveedor en descanso")

        # Crear hold
        s.execute(
            text("""
                INSERT INTO ev_proveedores.reserva_temporal
                  (id, proveedor_id, opcion_servicio_id, inicio, fin, status, 
                   expira_en, correlation_id, created_by)
                VALUES
                  (UUID(), :pid, :oid, :ini, :fin, 0, 
                   DATE_ADD(NOW(), INTERVAL :ttl MINUTE), :corr, :creator)
            """),
            {
                "pid": proveedor_id,
                "oid": opcion_servicio_id,
                "ini": inicio,
                "fin": fin,
                "ttl": ttl_min,
                "corr": correlation_id,
                "creator": created_by or "contratacion-service",
            },
        )
        s.commit()

        # Recuperar hold creado
        row = s.execute(
            text("""
                SELECT id, proveedor_id, opcion_servicio_id, inicio, fin, 
                       expira_en, status, correlation_id, created_by
                FROM ev_proveedores.reserva_temporal
                WHERE proveedor_id = :pid
                  AND correlation_id = :corr
                ORDER BY created_at DESC
                LIMIT 1
            """),
            {"pid": proveedor_id, "corr": correlation_id},
        ).mappings().first()

        return Hold(
            id=row["id"],
            proveedor_id=row["proveedor_id"],
            opcion_servicio_id=row["opcion_servicio_id"],
            inicio=row["inicio"],
            fin=row["fin"],
            expira_en=row["expira_en"],
            status=row["status"],
            correlation_id=row["correlation_id"],
            created_by=row["created_by"],
        )

    def confirmar_hold(
        self,
        s,
        *,
        hold_id: str
    ) -> Hold:
        """Confirma un hold activo (status 0 → 1)"""
        hold = s.execute(
            text("""
                SELECT id, proveedor_id, opcion_servicio_id, inicio, fin, 
                       expira_en, status, correlation_id, created_by
                FROM ev_proveedores.reserva_temporal
                WHERE id = :hid
                LIMIT 1
            """),
            {"hid": hold_id},
        ).mappings().first()

        if not hold:
            raise HoldNoEncontrado(hold_id)

        if hold["status"] != 0:
            raise HoldInvalidoError(hold_id, hold["status"], "Hold no está en estado activo (status=0)")

        if hold["expira_en"] < datetime.now():
            raise HoldExpirado(hold_id)

        s.execute(
            text("UPDATE ev_proveedores.reserva_temporal SET status = 1 WHERE id = :hid AND status = 0"),
            {"hid": hold_id},
        )
        s.commit()

        # Retornar hold actualizado
        return Hold(
            id=hold["id"],
            proveedor_id=hold["proveedor_id"],
            opcion_servicio_id=hold["opcion_servicio_id"],
            inicio=hold["inicio"],
            fin=hold["fin"],
            expira_en=hold["expira_en"],
            status=1,  # Actualizado
            correlation_id=hold["correlation_id"],
            created_by=hold["created_by"],
        )

    def liberar_hold(
        self,
        s,
        *,
        hold_id: str
    ) -> None:
        """Libera un hold (idempotente)"""
        hold = s.execute(
            text("SELECT id, status FROM ev_proveedores.reserva_temporal WHERE id = :hid LIMIT 1"),
            {"hid": hold_id},
        ).mappings().first()

        if not hold:
            raise HoldNoEncontrado(hold_id)

        # Idempotencia: si ya está liberado, no hacer nada
        if hold["status"] == 3:
            return

        if hold["status"] not in (0, 1):
            raise HoldInvalidoError(hold_id, hold["status"], "Hold no puede ser liberado desde este estado")

        s.execute(
            text("UPDATE ev_proveedores.reserva_temporal SET status = 3 WHERE id = :hid"),
            {"hid": hold_id},
        )
        s.commit()

    def obtener_hold(
        self,
        s,
        *,
        hold_id: str
    ) -> Optional[Hold]:
        """Obtiene un hold por ID"""
        row = s.execute(
            text("""
                SELECT id, proveedor_id, opcion_servicio_id, inicio, fin, 
                       expira_en, status, correlation_id, created_by
                FROM ev_proveedores.reserva_temporal
                WHERE id = :hid
                LIMIT 1
            """),
            {"hid": hold_id},
        ).mappings().first()

        if not row:
            return None

        return Hold(
            id=row["id"],
            proveedor_id=row["proveedor_id"],
            opcion_servicio_id=row["opcion_servicio_id"],
            inicio=row["inicio"],
            fin=row["fin"],
            expira_en=row["expira_en"],
            status=row["status"],
            correlation_id=row["correlation_id"],
            created_by=row["created_by"],
        )
