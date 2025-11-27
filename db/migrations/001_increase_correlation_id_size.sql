-- Migración: Aumentar tamaño de correlation_id
-- Fecha: 2025-11-27
-- Razón: correlation_id con formato "pedido-{uuid}-item-{uuid}" excede 64 caracteres

-- Aumentar tamaño en reserva_temporal
ALTER TABLE ev_proveedores.reserva_temporal 
MODIFY COLUMN correlation_id VARCHAR(150) NULL;

-- Aumentar tamaño en pedido_evento (si existe)
ALTER TABLE ev_contratacion.pedido_evento 
MODIFY COLUMN correlation_id VARCHAR(150) NULL;

-- Aumentar tamaño en reserva (si existe)
ALTER TABLE ev_contratacion.reserva 
MODIFY COLUMN correlation_id VARCHAR(150) NULL;
