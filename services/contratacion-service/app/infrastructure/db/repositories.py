"""
Repositorios de Contratación - Implementación MySQL (Hexagonal Architecture)
Implementa los ports del dominio usando SQLAlchemy Core
"""
from typing import Any, List, Optional
from datetime import datetime
from decimal import Decimal
from sqlalchemy import text

from ...domain.models import Pedido, ItemPedido, Reserva
from ...domain.exceptions import (
    PedidoNoEncontrado,
    ItemPedidoNoEncontrado,
    ReservaNoEncontrada,
    TransicionEstadoInvalida,
)


class MySQLPedidoRepository:
    """Repositorio MySQL para Pedidos"""
    
    def crear(
        self,
        session: Any,
        cliente_id: str,
        tipo_evento_id: str,
        paquete_id: Optional[str],
        fecha_evento: datetime,
        hora_inicio: str,
        hora_fin: str,
        num_personas: int,
        ubicacion: str,
        monto_total: Decimal,
        notas: Optional[str] = None,
    ) -> Pedido:
        """Crea un nuevo pedido"""
        import uuid
        new_id = str(uuid.uuid4())
        
        # Note: pedido_evento NO tiene paquete_id ni num_personas según bosstrap_remaste.sql
        # Se deriva de item_pedido_evento cuando sea necesario
        session.execute(
            text("""
                INSERT INTO ev_contratacion.pedido_evento (
                    id, cliente_id, tipo_evento_id, fecha_evento,
                    hora_inicio, hora_fin, num_personas, ubicacion, status,
                    monto_total, created_at, updated_at
                ) VALUES (
                    :id, :cliente_id, :tipo_evento_id, :fecha_evento,
                    :hora_inicio, :hora_fin, :num_personas, :ubicacion, 0,
                    :monto_total, NOW(), NOW()
                )
            """),
            {
                "id": new_id,
                "cliente_id": cliente_id,
                "tipo_evento_id": tipo_evento_id,
                "fecha_evento": fecha_evento,
                "hora_inicio": hora_inicio,
                "hora_fin": hora_fin,
                "num_personas": num_personas,
                "ubicacion": ubicacion,
                "monto_total": monto_total,
            },
        )
        session.commit()
        
        return self.obtener_por_id(session, new_id)

    def obtener_por_id(self, session: Any, pedido_id: str) -> Optional[Pedido]:
        """Obtiene un pedido por su ID"""
        # Derivar paquete_id desde item_pedido_evento
        row = session.execute(
            text("""
                SELECT
                  pe.id,
                  pe.cliente_id,
                  pe.tipo_evento_id,
                  te.nombre AS tipo_evento_nombre,
                  (SELECT i.referencia_id FROM ev_contratacion.item_pedido_evento i
                     WHERE i.pedido_id = pe.id AND i.tipo_item = 'PAQUETE' LIMIT 1) AS paquete_id,
                  pe.fecha_evento,
                  pe.hora_inicio,
                  pe.hora_fin,
                  pe.num_personas,
                  pe.ubicacion,
                  pe.status,
                  pe.monto_total,
                  pe.moneda,
                  pe.created_at,
                  pe.updated_at
                FROM ev_contratacion.pedido_evento pe
                LEFT JOIN ev_catalogo.tipo_evento te ON te.id = pe.tipo_evento_id
                WHERE pe.id = :pedido_id
                LIMIT 1
            """),
            {"pedido_id": pedido_id},
        ).mappings().first()
        
        if not row:
            return None
        
        return Pedido(
            id=row["id"],
            cliente_id=row["cliente_id"],
            tipo_evento_id=row["tipo_evento_id"],
            paquete_id=row["paquete_id"],
            fecha_evento=row["fecha_evento"],
            hora_inicio=str(row["hora_inicio"]),
            hora_fin=str(row["hora_fin"]) if row["hora_fin"] else None,
            num_personas=row["num_personas"],
            ubicacion=row["ubicacion"],
            status=row["status"],
            monto_total=row["monto_total"],
            moneda=row["moneda"],
            notas=None,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            cliente_nombre=None,
            cliente_email=None,
            tipo_evento_nombre=row["tipo_evento_nombre"],
        )
    
    def listar_por_cliente(
        self,
        session: Any,
        cliente_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Pedido]:
        """Lista pedidos de un cliente específico"""
        rows = session.execute(
            text("""
                SELECT
                  pe.id,
                  pe.cliente_id,
                  pe.tipo_evento_id,
                  (SELECT i.referencia_id FROM ev_contratacion.item_pedido_evento i
                     WHERE i.pedido_id = pe.id AND i.tipo_item = 'PAQUETE' LIMIT 1) AS paquete_id,
                  pe.fecha_evento,
                  pe.hora_inicio,
                  pe.hora_fin,
                  pe.num_personas,
                  pe.ubicacion,
                  pe.status,
                  pe.monto_total,
                  pe.moneda,
                  pe.created_at,
                  pe.updated_at
                FROM ev_contratacion.pedido_evento pe
                WHERE pe.cliente_id = :cliente_id
                ORDER BY pe.created_at DESC
                LIMIT :limit OFFSET :offset
            """),
            {"cliente_id": cliente_id, "limit": limit, "offset": offset},
        ).mappings().all()
        
        return [
            Pedido(
                id=row["id"],
                cliente_id=row["cliente_id"],
                tipo_evento_id=row["tipo_evento_id"],
                paquete_id=row["paquete_id"],
                fecha_evento=row["fecha_evento"],
                hora_inicio=str(row["hora_inicio"]),
                hora_fin=str(row["hora_fin"]) if row["hora_fin"] else None,
                num_personas=row["num_personas"],
                ubicacion=row["ubicacion"],
                status=row["status"],
                monto_total=row["monto_total"],
                moneda=row["moneda"],
                notas=None,
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                cliente_nombre=None,  # Not available without cross-schema JOIN
                cliente_email=None,   # Not available without cross-schema JOIN
                tipo_evento_nombre=None,  # Not available without cross-schema JOIN
            )
            for row in rows
        ]
    
    def listar_todos(
        self,
        session: Any,
        *,
        status: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Pedido]:
        """Lista todos los pedidos (admin) con filtros opcionales"""
        if status is not None:
            rows = session.execute(
                text("""
                    SELECT
                      pe.id,
                      pe.cliente_id,
                      pe.tipo_evento_id,
                      (SELECT i.referencia_id FROM ev_contratacion.item_pedido_evento i
                         WHERE i.pedido_id = pe.id AND i.tipo_item = 'PAQUETE' LIMIT 1) AS paquete_id,
                      pe.fecha_evento,
                      pe.hora_inicio,
                      pe.hora_fin,
                      pe.num_personas,
                      pe.ubicacion,
                      pe.status,
                      pe.monto_total,
                      pe.moneda,
                      pe.created_at,
                      pe.updated_at
                    FROM ev_contratacion.pedido_evento pe
                    WHERE pe.status = :status
                    ORDER BY pe.created_at DESC
                    LIMIT :limit OFFSET :offset
                """),
                {"status": status, "limit": limit, "offset": offset},
            ).mappings().all()
        else:
            rows = session.execute(
                text("""
                    SELECT
                      pe.id,
                      pe.cliente_id,
                      pe.tipo_evento_id,
                      (SELECT i.referencia_id FROM ev_contratacion.item_pedido_evento i
                         WHERE i.pedido_id = pe.id AND i.tipo_item = 'PAQUETE' LIMIT 1) AS paquete_id,
                      pe.fecha_evento,
                      pe.hora_inicio,
                      pe.hora_fin,
                      pe.num_personas,
                      pe.ubicacion,
                      pe.status,
                      pe.monto_total,
                      pe.moneda,
                      pe.created_at,
                      pe.updated_at
                    FROM ev_contratacion.pedido_evento pe
                    ORDER BY pe.created_at DESC
                    LIMIT :limit OFFSET :offset
                """),
                {"limit": limit, "offset": offset},
            ).mappings().all()
        
        return [
            Pedido(
                id=row["id"],
                cliente_id=row["cliente_id"],
                tipo_evento_id=row["tipo_evento_id"],
                paquete_id=row["paquete_id"],
                fecha_evento=row["fecha_evento"],
                hora_inicio=str(row["hora_inicio"]),
                hora_fin=str(row["hora_fin"]) if row["hora_fin"] else None,
                num_personas=row["num_personas"],
                ubicacion=row["ubicacion"],
                status=row["status"],
                monto_total=row["monto_total"],
                moneda=row["moneda"],
                notas=None,
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                cliente_nombre=None,  # Not available without cross-schema JOIN
                cliente_email=None,   # Not available without cross-schema JOIN
                tipo_evento_nombre=None,  # Not available without cross-schema JOIN
            )
            for row in rows
        ]
    
    def actualizar_estado(
        self,
        session: Any,
        pedido_id: str,
        nuevo_estado: int
    ) -> Pedido:
        """Actualiza el estado de un pedido"""
        pedido = self.obtener_por_id(session, pedido_id)
        if not pedido:
            raise PedidoNoEncontrado(pedido_id)
        
        if not pedido.puede_transicionar_a(nuevo_estado):
            raise TransicionEstadoInvalida(pedido.status, nuevo_estado)
        
        session.execute(
            text("""
                UPDATE ev_contratacion.pedido_evento
                SET status = :nuevo_estado, updated_at = NOW()
                WHERE id = :pedido_id
            """),
            {"pedido_id": pedido_id, "nuevo_estado": nuevo_estado},
        )
        session.commit()
        
        return self.obtener_por_id(session, pedido_id)
    
    def actualizar_monto(
        self,
        session: Any,
        pedido_id: str,
        nuevo_monto: float
    ) -> Pedido:
        """Actualiza el monto total del pedido"""
        session.execute(
            text("""
                UPDATE ev_contratacion.pedido_evento
                SET monto_total = :nuevo_monto, updated_at = NOW()
                WHERE id = :pedido_id
            """),
            {"pedido_id": pedido_id, "nuevo_monto": nuevo_monto},
        )
        session.commit()
        
        return self.obtener_por_id(session, pedido_id)


class MySQLItemPedidoRepository:
    """Repositorio MySQL para Items de Pedido"""
    
    def crear(
        self,
        session: Any,
        *,
        pedido_id: str,
        opcion_servicio_id: str,
        nombre_servicio: str,
        cantidad: int,
        precio_unitario: float,
        subtotal: float,
        tipo_item: str = 'SERVICIO',  # 'SERVICIO' o 'PAQUETE' según bosstrap_remaste.sql
        referencia_id: Optional[str] = None,
    ) -> ItemPedido:
        """Crea un nuevo item de pedido"""
        import uuid
        new_id = str(uuid.uuid4())
        
        # referencia_id: para SERVICIO usa opcion_servicio_id, para PAQUETE usa paquete_id
        ref_id = referencia_id or opcion_servicio_id
        
        session.execute(
            text("""
                INSERT INTO ev_contratacion.item_pedido_evento (
                    id, pedido_id, opcion_servicio_id, nombre_servicio,
                    cantidad, precio_unitario, subtotal, tipo_item, referencia_id,
                    created_at
                ) VALUES (
                    :id, :pedido_id, :opcion_servicio_id, :nombre_servicio,
                    :cantidad, :precio_unitario, :subtotal, :tipo_item, :referencia_id,
                    NOW()
                )
            """),
            {
                "id": new_id,
                "pedido_id": pedido_id,
                "opcion_servicio_id": opcion_servicio_id,
                "nombre_servicio": nombre_servicio,
                "cantidad": cantidad,
                "precio_unitario": precio_unitario,
                "subtotal": subtotal,
                "tipo_item": tipo_item,
                "referencia_id": ref_id,
            },
        )
        session.commit()
        
        # Recuperar item creado
        row = session.execute(
            text("""
                SELECT id, pedido_id, opcion_servicio_id, nombre_servicio,
                       cantidad, precio_unitario, subtotal, created_at
                FROM ev_contratacion.item_pedido_evento
                WHERE id = :item_id
                LIMIT 1
            """),
            {"item_id": new_id},
        ).mappings().first()
        
        return ItemPedido(
            id=row["id"],
            pedido_id=row["pedido_id"],
            opcion_servicio_id=row["opcion_servicio_id"],
            nombre_servicio=row["nombre_servicio"],
            cantidad=row["cantidad"],
            precio_unitario=Decimal(str(row["precio_unitario"])),
            subtotal=Decimal(str(row["subtotal"])),
        )
    
    def listar_por_pedido(
        self,
        session: Any,
        pedido_id: str
    ) -> List[ItemPedido]:
        """Lista items de un pedido"""
        rows = session.execute(
            text("""
                SELECT id, pedido_id, opcion_servicio_id, nombre_servicio,
                       cantidad, precio_unitario, subtotal, created_at
                FROM ev_contratacion.item_pedido_evento
                WHERE pedido_id = :pedido_id
                ORDER BY created_at
            """),
            {"pedido_id": pedido_id},
        ).mappings().all()
        
        # Enriquecer items con proveedor si existe reserva
        # Nota: Esto debería hacerse idealmente en una vista o servicio de dominio,
        # pero para mantenerlo simple en el repo por ahora:
        items = []
        for row in rows:
            # Buscar proveedor asociado en reservas (query N+1 simple, optimizable luego)
            prov_row = session.execute(
                text("""
                    SELECT p.id, p.nombre, p.email, p.telefono
                    FROM ev_contratacion.reserva r
                    JOIN ev_proveedores.proveedor p ON p.id = r.proveedor_id
                    WHERE r.item_pedido_id = :item_id AND r.status != 2 -- No cancelado
                    LIMIT 1
                """),
                {"item_id": row["id"]}
            ).mappings().first()

            item = ItemPedido(
                id=row["id"],
                pedido_id=row["pedido_id"],
                opcion_servicio_id=row["opcion_servicio_id"],
                nombre_servicio=row["nombre_servicio"],
                cantidad=row["cantidad"],
                precio_unitario=Decimal(str(row["precio_unitario"])),
                subtotal=Decimal(str(row["subtotal"])),
            )
            
            if prov_row:
                # Inyectamos proveedor como atributo dinámico para que el frontend lo reciba
                # (El modelo Pydantic/Dataclass debe soportarlo o ser flexible)
                setattr(item, 'proveedor', dict(prov_row))
            
            items.append(item)
            
        return items
    
    def obtener_por_id(
        self,
        session: Any,
        item_id: str
    ) -> Optional[ItemPedido]:
        """Obtiene un item por su ID"""
        row = session.execute(
            text("""
                SELECT id, pedido_id, opcion_servicio_id, nombre_servicio,
                       cantidad, precio_unitario, subtotal, created_at
                FROM ev_contratacion.item_pedido_evento
                WHERE id = :item_id
                LIMIT 1
            """),
            {"item_id": item_id},
        ).mappings().first()
        
        if not row:
            return None
        
        return ItemPedido(
            id=row["id"],
            pedido_id=row["pedido_id"],
            opcion_servicio_id=row["opcion_servicio_id"],
            nombre_servicio=row["nombre_servicio"],
            cantidad=row["cantidad"],
            precio_unitario=Decimal(str(row["precio_unitario"])),
            subtotal=Decimal(str(row["subtotal"])),
        )
    
    def eliminar(
        self,
        session: Any,
        item_id: str
    ) -> None:
        """Elimina un item de pedido"""
        session.execute(
            text("""
                DELETE FROM ev_contratacion.item_pedido_evento
                WHERE id = :item_id
            """),
            {"item_id": item_id},
        )
        session.commit()


class MySQLReservaRepository:
    """Repositorio MySQL para Reservas"""
    
    def crear(
        self,
        session: Any,
        *,
        pedido_id: str,
        item_pedido_id: str,
        proveedor_id: str,
        opcion_servicio_id: str,
        inicio: datetime,
        fin: datetime,
        status: int,
        monto: Decimal,
        hold_id: Optional[str] = None,
        notas: Optional[str] = None
    ) -> Reserva:
        """Crea una nueva reserva"""
        import uuid
        new_id = str(uuid.uuid4())
        
        session.execute(
            text("""
                INSERT INTO ev_contratacion.reserva (
                    id, item_pedido_id, proveedor_id, inicio, fin,
                    status, hold_id, created_at
                ) VALUES (
                    :id, :item_pedido_id, :proveedor_id, :inicio, :fin,
                    :status, :hold_id, NOW()
                )
            """),
            {
                "id": new_id,
                "item_pedido_id": item_pedido_id,
                "proveedor_id": proveedor_id,
                "inicio": inicio,
                "fin": fin,
                "status": status,
                "hold_id": hold_id,
            },
        )
        session.commit()
        
        return Reserva(
            id=new_id,
            pedido_id=pedido_id,
            item_pedido_id=item_pedido_id,
            proveedor_id=proveedor_id,
            opcion_servicio_id=opcion_servicio_id,
            inicio=inicio,
            fin=fin,
            status=status,
            monto=monto,
            hold_id=hold_id,
            notas=notas,
            created_at=datetime.now(),
        )
    
    def listar_por_pedido(
        self,
        session: Any,
        pedido_id: str
    ) -> List[Reserva]:
        """Lista reservas de un pedido"""
        rows = session.execute(
            text("""
                SELECT r.id, r.item_pedido_id, r.proveedor_id, r.inicio, r.fin,
                       r.status, r.hold_id, r.created_at,
                       i.pedido_id, i.opcion_servicio_id
                FROM ev_contratacion.reserva r
                JOIN ev_contratacion.item_pedido_evento i ON i.id = r.item_pedido_id
                WHERE i.pedido_id = :pedido_id
                ORDER BY r.created_at
            """),
            {"pedido_id": pedido_id},
        ).mappings().all()
        
        return [
            Reserva(
                id=row["id"],
                pedido_id=row["pedido_id"],
                item_pedido_id=row["item_pedido_id"],
                proveedor_id=row["proveedor_id"],
                opcion_servicio_id=row["opcion_servicio_id"],
                inicio=row["inicio"],
                fin=row["fin"],
                status=row["status"],
                monto=Decimal("0"),  # Monto no está en la tabla según schema
                hold_id=row["hold_id"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def obtener_por_item(
        self,
        session: Any,
        item_pedido_id: str
    ) -> Optional[Reserva]:
        """Obtiene una reserva por el id del item (si existe)"""
        row = session.execute(
            text("""
                SELECT r.id, r.item_pedido_id, r.proveedor_id, r.inicio, r.fin,
                       r.status, r.hold_id, r.created_at,
                       i.pedido_id, i.opcion_servicio_id
                FROM ev_contratacion.reserva r
                JOIN ev_contratacion.item_pedido_evento i ON i.id = r.item_pedido_id
                WHERE r.item_pedido_id = :item_id
                LIMIT 1
            """),
            {"item_id": item_pedido_id},
        ).mappings().first()

        if not row:
            return None

        return Reserva(
            id=row["id"],
            pedido_id=row["pedido_id"],
            item_pedido_id=row["item_pedido_id"],
            proveedor_id=row["proveedor_id"],
            opcion_servicio_id=row["opcion_servicio_id"],
            inicio=row["inicio"],
            fin=row["fin"],
            status=row["status"],
            monto=Decimal("0"),
            hold_id=row["hold_id"],
            created_at=row["created_at"],
        )
