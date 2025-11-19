/* ============================================================
   MASSIVE TEST DATA - SOA EVENTOS PERU (MVP++)
   Generates 150-200 records per table with realistic random data
   Password for admin@eventos.pe: Evoluti0n (hashed)
   ============================================================ */

START TRANSACTION;

-- Date/time helpers
SET @today := CURRENT_DATE();
SET @now := NOW();
SET @next_sat := DATE_ADD(@today, INTERVAL (6 - WEEKDAY(@today)) DAY);
SET @evt_date_1 := DATE_ADD(@next_sat, INTERVAL 7 DAY);
SET @evt_date_2 := DATE_ADD(@next_sat, INTERVAL 14 DAY);
SET @evt_date_3 := DATE_ADD(@next_sat, INTERVAL 21 DAY);

-- Counter for deterministic UUIDs
SET @counter := 0;

/* ============================================================
   1) IAM - Massive Users (1 ADMIN + 150 CLIENTS)
   ============================================================ */

-- Roles (once only)
INSERT IGNORE INTO ev_iam.rol (id, codigo, nombre, descripcion, status) VALUES
 ('aaaa1111-1111-1111-1111-aaaaaaaaaaa1','ADMIN','Administrador','Administrative access (MVP)',1),
 ('aaaa1111-1111-1111-1111-aaaaaaaaaaa2','CLIENTE','Cliente','End user who contracts events',1);

-- Single administrator with password: Evoluti0n
INSERT IGNORE INTO ev_iam.usuario (id, email, password_hash, nombre, telefono, status) VALUES
 ('ee111111-1111-4111-8111-aaaaaaaaaaa1','admin@eventos.pe','$2b$12$T9QvT2JrJQmA2y7cKk1oMOOYqUj8K0e4R2rRj3Wm3mX8xWl3.1m5C','Admin Eventos','+51 900 111 000',1);

-- Generate 150 clients automatically
INSERT IGNORE INTO ev_iam.usuario (id, email, password_hash, nombre, telefono, status)
SELECT 
    CONCAT('ee', LPAD(@counter := @counter + 1, 6, '0'), '-', SUBSTRING(MD5(RAND()), 1, 4), '-', SUBSTRING(MD5(RAND()), 1, 4), '-', SUBSTRING(MD5(RAND()), 1, 4), '-', SUBSTRING(MD5(RAND()), 1, 12)),
    CONCAT(
        ELT(1 + FLOOR(RAND() * 20), 'juan', 'maria', 'carlos', 'ana', 'luis', 'rosa', 'jose', 'carmen', 'miguel', 'elena', 'fernando', 'patricia', 'roberto', 'lucia', 'jorge', 'sofia', 'ricardo', 'claudia', 'pedro', 'daniela'),
        '.',
        ELT(1 + FLOOR(RAND() * 20), 'garcia', 'rodriguez', 'lopez', 'martinez', 'perez', 'gonzalez', 'hernandez', 'ramirez', 'torres', 'flores', 'vargas', 'castillo', 'romero', 'alvarez', 'mendoza', 'silva', 'rojas', 'delgado', 'castro', 'ortiz'),
        FLOOR(RAND() * 1000),
        '@eventos.pe'
    ),
    '$2b$12$T9QvT2JrJQmA2y7cKk1oMOOYqUj8K0e4R2rRj3Wm3mX8xWl3.1m5C',
    CONCAT(
        ELT(1 + FLOOR(RAND() * 20), 'Juan', 'Maria', 'Carlos', 'Ana', 'Luis', 'Rosa', 'Jose', 'Carmen', 'Miguel', 'Elena', 'Fernando', 'Patricia', 'Roberto', 'Lucia', 'Jorge', 'Sofia', 'Ricardo', 'Claudia', 'Pedro', 'Daniela'),
        ' ',
        ELT(1 + FLOOR(RAND() * 20), 'Garcia', 'Rodriguez', 'Lopez', 'Martinez', 'Perez', 'Gonzalez', 'Hernandez', 'Ramirez', 'Torres', 'Flores', 'Vargas', 'Castillo', 'Romero', 'Alvarez', 'Mendoza', 'Silva', 'Rojas', 'Delgado', 'Castro', 'Ortiz')
    ),
    CONCAT('+51 9', LPAD(FLOOR(RAND() * 100000000), 8, '0')),
    1
FROM 
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10) a,
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10) b,
    (SELECT 1 UNION SELECT 2 UNION SELECT 3) c
LIMIT 150;

-- Assign roles to clients
INSERT IGNORE INTO ev_iam.usuario_rol (id, usuario_id, rol_id)
SELECT 
    UUID(),
    u.id,
    'aaaa1111-1111-1111-1111-aaaaaaaaaaa2'
FROM ev_iam.usuario u
WHERE u.id != 'ee111111-1111-4111-8111-aaaaaaaaaaa1';

-- Assign ADMIN role (only one)
INSERT IGNORE INTO ev_iam.usuario_rol (id, usuario_id, rol_id) 
VALUES ('ur-admin-0001', 'ee111111-1111-4111-8111-aaaaaaaaaaa1', 'aaaa1111-1111-1111-1111-aaaaaaaaaaa1');

/* ============================================================
   2) CATALOG - Massive Services and Options
   ============================================================ */

-- Additional event types
INSERT IGNORE INTO ev_catalogo.tipo_evento (id, nombre, descripcion, status) VALUES
 ('44444444-1111-1111-1111-111111111111','Quinceanero','15th birthday parties',1),
 ('55555555-1111-1111-1111-111111111111','Concierto','Musical mass events',1),
 ('66666666-1111-1111-1111-111111111111','Conferencia','Corporate events',1),
 ('77777777-1111-1111-1111-111111111111','Graduacion','Graduation ceremonies',1),
 ('88888888-1111-1111-1111-111111111111','Aniversario','Anniversary celebrations',1);

-- Massive services (30 services)
INSERT IGNORE INTO ev_catalogo.servicio (id, nombre, descripcion, tipo_evento_id, status, created_by)
SELECT 
    UUID(),
    CONCAT(
        ELT(1 + FLOOR(RAND() * 15), 'Premium ', 'Standard ', 'Economic ', 'Luxury ', 'Basic ', 'Complete ', 'Special ', 'Customized ', 'Professional ', 'Express ', 'Deluxe ', 'Gold ', 'Platinum ', 'VIP ', 'Standard '),
        ELT(1 + FLOOR(RAND() * 20), 'Catering', 'Lighting', 'Sound', 'Decoration', 'Photography', 'Video', 'Animation', 'Furniture', 'Florist', 'Security', 'Coordination', 'Transport', 'Entertainment', 'Beverages', 'Desserts', 'Venue', 'Music', 'Ambiance', 'Logistics', 'Staff')
    ),
    CONCAT('Quality service for ', ELT(1 + FLOOR(RAND() * 8), 'social', 'corporate', 'family', 'music', 'sports', 'cultural', 'educational', 'charity'), ' events'),
    ELT(1 + FLOOR(RAND() * 8), '11111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222', '33333333-3333-3333-3333-333333333333', '44444444-1111-1111-1111-111111111111', '55555555-1111-1111-1111-111111111111', '66666666-1111-1111-1111-111111111111', '77777777-1111-1111-1111-111111111111', '88888888-1111-1111-1111-111111111111'),
    1,
    'ee111111-1111-4111-8111-aaaaaaaaaaa1'
FROM 
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10) a,
    (SELECT 1 UNION SELECT 2 UNION SELECT 3) b
LIMIT 30;

-- Service options (80 options)
INSERT IGNORE INTO ev_catalogo.opcion_servicio (id, servicio_id, nombre, detalles, status, created_by)
SELECT 
    UUID(),
    (SELECT id FROM ev_catalogo.servicio ORDER BY RAND() LIMIT 1),
    CONCAT(
        ELT(1 + FLOOR(RAND() * 10), 'Package ', 'Service ', 'Solution ', 'Kit ', 'Set ', 'Combo ', 'Plan ', 'Program ', 'Offer ', 'Proposal '),
        ELT(1 + FLOOR(RAND() * 15), 'Basic', 'Complete', 'Premium', 'Standard', 'Deluxe', 'Gold', 'Platinum', 'VIP', 'Express', 'Customized', 'Family', 'Business', 'Economic', 'Luxury', 'Special'),
        ' - ',
        FLOOR(50 + RAND() * 500),
        ' people'
    ),
    JSON_OBJECT(
        'capacity', FLOOR(50 + RAND() * 500),
        'duration_hours', FLOOR(2 + RAND() * 10),
        'staff', FLOOR(1 + RAND() * 10),
        'equipment', ELT(1 + FLOOR(RAND() * 5), 'basic', 'standard', 'premium', 'complete', 'professional')
    ),
    1,
    'ee111111-1111-4111-8111-aaaaaaaaaaa1'
FROM 
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10) a,
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8) b
LIMIT 80;

-- Historical and current prices
INSERT IGNORE INTO ev_catalogo.precio_servicio (id, opcion_servicio_id, moneda, monto, vigente_desde, vigente_hasta, created_by)
SELECT 
    UUID(),
    os.id,
    'PEN',
    ROUND(100 + (RAND() * 4900), 2),
    DATE_SUB(@today, INTERVAL FLOOR(30 + RAND() * 60) DAY),
    DATE_SUB(@today, INTERVAL 1 DAY),
    'ee111111-1111-4111-8111-aaaaaaaaaaa1'
FROM ev_catalogo.opcion_servicio os;

INSERT IGNORE INTO ev_catalogo.precio_servicio (id, opcion_servicio_id, moneda, monto, vigente_desde, vigente_hasta, created_by)
SELECT 
    UUID(),
    os.id,
    'PEN',
    ROUND(100 + (RAND() * 4900), 2),
    @today,
    NULL,
    'ee111111-1111-4111-8111-aaaaaaaaaaa1'
FROM ev_catalogo.opcion_servicio os;

/* ============================================================
   3) PACKAGES - Massive Packages
   ============================================================ */

-- Packages (15 packages)
INSERT IGNORE INTO ev_paquetes.paquete (id, codigo, nombre, descripcion, status, created_by)
SELECT 
    UUID(),
    CONCAT('PKG-', UPPER(SUBSTRING(MD5(RAND()), 1, 6)), '-', @counter := @counter + 1),
    CONCAT(
        ELT(1 + FLOOR(RAND() * 8), 'Package ', 'Combo ', 'Solution ', 'Kit ', 'Set ', 'Plan ', 'Program ', 'Offer '),
        ELT(1 + FLOOR(RAND() * 12), 'Complete Party', 'Business Event', 'Family Celebration', 'Dream Wedding', 'Magical Quinceanero', 'Premium Concert', 'Professional Conference', 'Elegant Graduation', 'Special Anniversary', 'Executive Corporate', 'Premium Social', 'Unique Customized')
    ),
    CONCAT('Complete description for ', ELT(1 + FLOOR(RAND() * 12), 'unforgettable parties', 'corporate events', 'family celebrations', 'perfect weddings', 'magical quinceaneros', 'spectacular concerts', 'professional conferences', 'elegant graduations', 'special anniversaries', 'executive events', 'social occasions', 'unique moments')),
    1,
    'ee111111-1111-4111-8111-aaaaaaaaaaa1'
FROM 
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10 UNION SELECT 11 UNION SELECT 12 UNION SELECT 13 UNION SELECT 14 UNION SELECT 15) a
LIMIT 15;

-- Package items (3-6 options per package)
INSERT IGNORE INTO ev_paquetes.item_paquete (id, paquete_id, opcion_servicio_id, cantidad)
SELECT 
    UUID(),
    p.id,
    (SELECT id FROM ev_catalogo.opcion_servicio ORDER BY RAND() LIMIT 1),
    FLOOR(1 + RAND() * 3)
FROM ev_paquetes.paquete p,
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6) items
WHERE RAND() > 0.3
LIMIT 80;

-- Package prices
INSERT IGNORE INTO ev_paquetes.precio_paquete (id, paquete_id, moneda, monto, vigente_desde, vigente_hasta, created_by)
SELECT 
    UUID(),
    p.id,
    'PEN',
    ROUND(500 + (RAND() * 5000), 2),
    @today,
    NULL,
    'ee111111-1111-4111-8111-aaaaaaaaaaa1'
FROM ev_paquetes.paquete p;

/* ============================================================
   4) PROVIDERS - Massive Providers
   ============================================================ */

-- Providers (50 providers)
INSERT IGNORE INTO ev_proveedores.proveedor (id, nombre, email, telefono, rating_prom, status, created_by)
SELECT 
    UUID(),
    CONCAT(
        ELT(1 + FLOOR(RAND() * 15), 'Services ', 'Solutions ', 'Experts in ', 'Professionals ', 'Quality ', 'Premium ', 'Elite ', 'Master ', 'Pro ', 'Super ', 'Mega ', 'Ultra ', 'Global ', 'National ', 'Local '),
        ELT(1 + FLOOR(RAND() * 20), 'Events', 'Catering', 'Sound', 'Lighting', 'Decoration', 'Photography', 'Video', 'Animation', 'Logistics', 'Coordination', 'Entertainment', 'Music', 'Dances', 'Flowers', 'Furniture', 'Security', 'Transport', 'Technology', 'Production', 'Artistic'),
        ' ',
        ELT(1 + FLOOR(RAND() * 8), 'SAC', 'EIRL', 'SA', 'Ltd.', 'Group', 'Corp', 'Peru', 'Latam')
    ),
    CONCAT(
        LOWER(REPLACE(ELT(1 + FLOOR(RAND() * 15), 'Services', 'Solutions', 'Experts', 'Professionals', 'Quality', 'Premium', 'Elite', 'Master', 'Pro', 'Super', 'Mega', 'Ultra', 'Global', 'National', 'Local'), ' ', '')),
        '.',
        LOWER(REPLACE(ELT(1 + FLOOR(RAND() * 20), 'Events', 'Catering', 'Sound', 'Lighting', 'Decoration', 'Photography', 'Video', 'Animation', 'Logistics', 'Coordination', 'Entertainment', 'Music', 'Dances', 'Flowers', 'Furniture', 'Security', 'Transport', 'Technology', 'Production', 'Artistic'), ' ', '')),
        FLOOR(RAND() * 1000),
        '@provider.pe'
    ),
    CONCAT('+51 1', LPAD(FLOOR(RAND() * 10000000), 7, '0')),
    ROUND(3.0 + (RAND() * 2.0), 1),
    1,
    'ee111111-1111-4111-8111-aaaaaaaaaaa1'
FROM 
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10) a,
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) b
LIMIT 50;

-- Provider skills
INSERT IGNORE INTO ev_proveedores.habilidad_proveedor (id, proveedor_id, servicio_id, nivel)
SELECT 
    UUID(),
    p.id,
    (SELECT id FROM ev_catalogo.servicio ORDER BY RAND() LIMIT 1),
    FLOOR(3 + RAND() * 3)
FROM ev_proveedores.proveedor p,
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) skills
WHERE RAND() > 0.2
LIMIT 150;

-- Provider calendar
INSERT IGNORE INTO ev_proveedores.calendario_proveedor (id, proveedor_id, inicio, fin, tipo, created_by)
SELECT 
    UUID(),
    p.id,
    DATE_ADD(@today, INTERVAL FLOOR(1 + RAND() * 30) DAY),
    DATE_ADD(@today, INTERVAL FLOOR(2 + RAND() * 30) DAY),
    1,
    'ee111111-1111-4111-8111-aaaaaaaaaaa1'
FROM ev_proveedores.proveedor p,
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) days
WHERE RAND() > 0.3
LIMIT 200;

/* ============================================================
   5) ORDERS - Massive Orders (120 orders)
   ============================================================ */

-- Orders
INSERT IGNORE INTO ev_contratacion.pedido_evento (id, cliente_id, tipo_evento_id, fecha_evento, hora_inicio, hora_fin, ubicacion, moneda, status, correlation_id, request_id, created_by)
SELECT 
    UUID(),
    (SELECT id FROM ev_iam.usuario WHERE id != 'ee111111-1111-4111-8111-aaaaaaaaaaa1' ORDER BY RAND() LIMIT 1),
    (SELECT id FROM ev_catalogo.tipo_evento ORDER BY RAND() LIMIT 1),
    DATE_ADD(@today, INTERVAL FLOOR(5 + RAND() * 60) DAY),
    CONCAT(LPAD(FLOOR(10 + RAND() * 10), 2, '0'), ':00:00'),
    CONCAT(LPAD(FLOOR(18 + RAND() * 6), 2, '0'), ':00:00'),
    ELT(1 + FLOOR(RAND() * 8), 'Lima Centro', 'Miraflores', 'San Isidro', 'La Molina', 'Surco', 'Barranco', 'Callao', 'Provinces'),
    'PEN',
    FLOOR(RAND() * 3),
    CONCAT('corr-', SUBSTRING(MD5(RAND()), 1, 12)),
    CONCAT('req-', SUBSTRING(MD5(RAND()), 1, 12)),
    (SELECT id FROM ev_iam.usuario WHERE id != 'ee111111-1111-4111-8111-aaaaaaaaaaa1' ORDER BY RAND() LIMIT 1)
FROM 
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10) a,
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10) b,
    (SELECT 1 UNION SELECT 2) c
LIMIT 120;

-- Order items
INSERT IGNORE INTO ev_contratacion.item_pedido_evento (id, pedido_id, tipo_item, referencia_id, cantidad, precio_unit, precio_total, created_by)
SELECT 
    UUID(),
    p.id,
    CASE WHEN RAND() > 0.2 THEN 1 ELSE 2 END,
    CASE 
        WHEN RAND() > 0.2 THEN (SELECT id FROM ev_catalogo.opcion_servicio ORDER BY RAND() LIMIT 1)
        ELSE (SELECT id FROM ev_paquetes.paquete ORDER BY RAND() LIMIT 1)
    END,
    FLOOR(1 + RAND() * 3),
    ROUND(100 + (RAND() * 2000), 2),
    ROUND((100 + (RAND() * 2000)) * (1 + RAND() * 2), 2),
    p.cliente_id
FROM ev_contratacion.pedido_evento p,
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4) items
WHERE RAND() > 0.1
LIMIT 300;

-- Update order total amounts
UPDATE ev_contratacion.pedido_evento pe
JOIN (
    SELECT pedido_id, COALESCE(SUM(precio_total), 0) as total
    FROM ev_contratacion.item_pedido_evento
    GROUP BY pedido_id
) t ON pe.id = t.pedido_id
SET pe.monto_total = t.total;

/* ============================================================
   6) TEMPORARY RESERVATIONS (HOLDS)
   ============================================================ */

INSERT IGNORE INTO ev_proveedores.reserva_temporal (id, proveedor_id, opcion_servicio_id, inicio, fin, status, expira_en, correlation_id, created_by)
SELECT 
    UUID(),
    (SELECT id FROM ev_proveedores.proveedor ORDER BY RAND() LIMIT 1),
    (SELECT id FROM ev_catalogo.opcion_servicio ORDER BY RAND() LIMIT 1),
    DATE_ADD(@today, INTERVAL FLOOR(1 + RAND() * 30) DAY),
    DATE_ADD(@today, INTERVAL FLOOR(2 + RAND() * 30) DAY),
    FLOOR(RAND() * 2),
    DATE_ADD(@now, INTERVAL FLOOR(10 + RAND() * 120) MINUTE),
    CONCAT('corr-', SUBSTRING(MD5(RAND()), 1, 16)),
    (SELECT id FROM ev_iam.usuario WHERE id != 'ee111111-1111-4111-8111-aaaaaaaaaaa1' ORDER BY RAND() LIMIT 1)
FROM 
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10) a,
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) b
LIMIT 50;

/* ============================================================
   7) CONFIRMED RESERVATIONS
   ============================================================ */

INSERT IGNORE INTO ev_contratacion.reserva (id, item_pedido_id, proveedor_id, inicio, fin, status, hold_id, created_by)
SELECT 
    UUID(),
    ipe.id,
    (SELECT id FROM ev_proveedores.proveedor ORDER BY RAND() LIMIT 1),
    DATE_ADD(pe.fecha_evento, INTERVAL FLOOR(RAND() * 5) DAY),
    DATE_ADD(pe.fecha_evento, INTERVAL FLOOR(1 + RAND() * 5) DAY),
    1,
    NULL,
    pe.cliente_id
FROM ev_contratacion.item_pedido_evento ipe
JOIN ev_contratacion.pedido_evento pe ON ipe.pedido_id = pe.id
WHERE pe.status = 1
LIMIT 100;

/* ============================================================
   8) AUDIT
   ============================================================ */

INSERT IGNORE INTO ev_iam.evento_audit (id, fecha_hora, actor_id, entidad, entidad_id, accion, metadata)
SELECT 
    UUID(),
    DATE_SUB(@now, INTERVAL FLOOR(RAND() * 30) DAY),
    (SELECT id FROM ev_iam.usuario ORDER BY RAND() LIMIT 1),
    ELT(1 + FLOOR(RAND() * 5), 'pedido_evento', 'usuario', 'servicio', 'proveedor', 'reserva'),
    UUID(),
    ELT(1 + FLOOR(RAND() * 6), 'CREAR', 'ACTUALIZAR', 'CONSULTAR', 'ELIMINAR', 'CONFIRMAR', 'CANCELAR'),
    JSON_OBJECT(
        'ip', CONCAT('192.168.', FLOOR(RAND() * 255), '.', FLOOR(RAND() * 255)),
        'user_agent', ELT(1 + FLOOR(RAND() * 5), 'Chrome', 'Firefox', 'Safari', 'Edge', 'Mobile')
    )
FROM 
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10) a,
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10) b
LIMIT 100;

COMMIT;

/* ============================================================
   9) VERIFICATION QUERIES
   ============================================================ */

-- Record counts per table
SELECT 
    'Users' as table_name, COUNT(*) as total FROM ev_iam.usuario
UNION ALL SELECT 'Services', COUNT(*) FROM ev_catalogo.servicio
UNION ALL SELECT 'Options', COUNT(*) FROM ev_catalogo.opcion_servicio
UNION ALL SELECT 'Providers', COUNT(*) FROM ev_proveedores.proveedor
UNION ALL SELECT 'Orders', COUNT(*) FROM ev_contratacion.pedido_evento
UNION ALL SELECT 'Packages', COUNT(*) FROM ev_paquetes.paquete
UNION ALL SELECT 'Reservations', COUNT(*) FROM ev_contratacion.reserva
UNION ALL SELECT 'Holds', COUNT(*) FROM ev_proveedores.reserva_temporal;

-- Verify only one admin exists
SELECT rol.nombre, COUNT(*) as quantity
FROM ev_iam.usuario_rol ur
JOIN ev_iam.rol rol ON ur.rol_id = rol.id
GROUP BY rol.nombre;

-- Show some example orders
SELECT id, status, monto_total, fecha_evento 
FROM ev_contratacion.pedido_evento 
ORDER BY created_at DESC 
LIMIT 10;