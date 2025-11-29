-- (Eliminado: ALTER TABLE para 'moneda', la definición está en bootstrap.sql)
/*
  script3.sql — Complementary deterministic seeds for E2E testing
  Inserts deterministic records to cover flows:
  - tipos de evento, servicios, opciones, precios
  - paquetes, items, precio_paquete
  - proveedores, habilidades, calendario
  - usuarios (clientes), roles assignment
  - pedidos de ejemplo + items
  - holds (reserva_temporal) y reservas confirmadas

  Use: run manually against your local DB after backing up.
  Example:
    mysql -u app_api -p'Api_2025!' -h 127.0.0.1 < db/script3.sql
*/

START TRANSACTION;

SET @SYS_ADMIN = 'ee111111-1111-4111-8111-aaaaaaaaaaa1';
-- Demo user (exists in bootstrap.sql)
SET @DEMO_USER = 'aaaa2222-2222-2222-2222-aaaaaaaaaaa2';

-- === Extra deterministic seeds for robust E2E ===
-- All new records are idempotent and cross-linked for relational coverage

-- =============================================
-- 1. Asegurar que cada servicio tenga al menos una opción y precio vigente
-- =============================================
INSERT IGNORE INTO ev_catalogo.opcion_servicio (id, servicio_id, nombre, detalles, status, created_by, tipo_evento_id, categoria)
SELECT UUID(), s.id, CONCAT(s.nombre, ' - opción auto'), JSON_OBJECT('auto',true), 1, @SYS_ADMIN, s.tipo_evento_id, s.categoria
FROM ev_catalogo.servicio s
LEFT JOIN ev_catalogo.opcion_servicio o ON o.servicio_id = s.id
WHERE o.id IS NULL;

-- Para cada opción sin precio vigente, crear un precio por defecto
INSERT IGNORE INTO ev_catalogo.precio_servicio (id, opcion_servicio_id, moneda, monto, vigente_desde, vigente_hasta, created_by)
SELECT UUID(), o.id, 'PEN', 1000.00, CURRENT_DATE(), NULL, @SYS_ADMIN
FROM ev_catalogo.opcion_servicio o
LEFT JOIN ev_catalogo.precio_servicio p ON p.opcion_servicio_id = o.id AND (p.vigente_hasta IS NULL OR p.vigente_hasta >= CURRENT_DATE())
WHERE p.id IS NULL;

-- =============================================
-- 2. (Opcional) Verificación rápida
-- SELECT s.id, s.nombre, o.id AS opcion_id, p.id AS precio_id, p.monto
-- FROM ev_catalogo.servicio s
-- LEFT JOIN ev_catalogo.opcion_servicio o ON o.servicio_id = s.id
-- LEFT JOIN ev_catalogo.precio_servicio p ON p.opcion_servicio_id = o.id AND (p.vigente_hasta IS NULL OR p.vigente_hasta >= CURRENT_DATE())
-- WHERE s.status = 1;


/* ============================================================
   1) Tipos de evento (asegura existencia)
   ============================================================ */
INSERT IGNORE INTO ev_catalogo.tipo_evento (id, nombre, descripcion, status) VALUES
('11111111-1111-1111-1111-111111111111','Matrimonio','Bodas y recepciones',1),
('22222222-2222-2222-2222-222222222222','Cumpleaños','Fiestas de cumpleaños',1),
('33333333-3333-3333-3333-333333333333','Corporativo','Eventos empresariales',1),
('44444444-1111-1111-1111-111111111111','Quinceañeros','Fiestas de 15 años',1),
('55555555-1111-1111-1111-111111111111','Conciertos','Conciertos y shows',1)
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre), status=VALUES(status);

-- Add 5 more tipos de evento for 10 total
INSERT IGNORE INTO ev_catalogo.tipo_evento (id, nombre, descripcion, status) VALUES
('66666666-6666-6666-6666-666666666661','Baby Shower','Celebración de nacimiento',1),
('77777777-7777-7777-7777-777777777771','Graduación','Fiestas de graduación',1),
('88888888-8888-8888-8888-888888888881','Aniversario','Celebración de aniversario',1),
('99999999-9999-9999-9999-999999999991','Fiesta Temática','Fiestas temáticas',1),
('aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaa1','Evento Deportivo','Eventos deportivos',1)
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre), status=VALUES(status);

/* ============================================================
   2) Servicios determinísticos (mínimo 4 servicios por tipo_evento)
   ============================================================ */
INSERT IGNORE INTO ev_catalogo.servicio (id, nombre, descripcion, categoria, tipo_evento_id, status, created_by) VALUES
-- Matrimonio (1111)
('svc-catering-1111','Catering Premium','Servicio de catering completo','CATERING', '11111111-1111-1111-1111-111111111111',1,@SYS_ADMIN),
('svc-foto-1111','Fotografía Matrimonio','Fotografía profesional para bodas','FOTOGRAFIA', '11111111-1111-1111-1111-111111111111',1,@SYS_ADMIN),
('svc-musica-1111','Música / DJ','DJ o banda para matrimonios','ENTRETENIMIENTO', '11111111-1111-1111-1111-111111111111',1,@SYS_ADMIN),
('svc-deco-1111','Decoración Matrimonio','Decoración y ambientación nupcial','DECORACION', '11111111-1111-1111-1111-111111111111',1,@SYS_ADMIN),
-- Cumpleaños (2222)
('svc-musica-2222','DJ / Música','DJ profesional o animador','ENTRETENIMIENTO', '22222222-2222-2222-2222-222222222222',1,@SYS_ADMIN),
('svc-anim-2222','Animación','Animadores y shows infantiles','ANIMACION', '22222222-2222-2222-2222-222222222222',1,@SYS_ADMIN),
('svc-foto-2222','Fotografía Cumpleaños','Fotografía para fiestas','FOTOGRAFIA', '22222222-2222-2222-2222-222222222222',1,@SYS_ADMIN),
('svc-cake-2222','Pastelería','Torta y mesa de postres','PASTELERIA', '22222222-2222-2222-2222-222222222222',1,@SYS_ADMIN),
-- Corporativo (3333)
('svc-local-3333','Alquiler Local','Locales para eventos corporativos','LOCAL', '33333333-3333-3333-3333-333333333333',1,@SYS_ADMIN),
('svc-av-3333','A/V y Sonido','Equipo audiovisual y sonorización','AUDIOVISUAL', '33333333-3333-3333-3333-333333333333',1,@SYS_ADMIN),
('svc-coffee-3333','Coffee Break','Servicio de coffee break','CATERING', '33333333-3333-3333-3333-333333333333',1,@SYS_ADMIN),
('svc-deco-3333','Decoración Corporativa','Decoración y branding','DECORACION', '33333333-3333-3333-3333-333333333333',1,@SYS_ADMIN),
-- Quinceañeros (4444)
('svc-catering-4444','Catering Quince','Servicio catering para 15 años','CATERING', '44444444-1111-1111-1111-111111111111',1,@SYS_ADMIN),
('svc-musica-4444','Música Quince','DJ / Banda para 15 años','ENTRETENIMIENTO', '44444444-1111-1111-1111-111111111111',1,@SYS_ADMIN),
('svc-foto-4444','Fotografía Quince','Fotografía para 15 años','FOTOGRAFIA', '44444444-1111-1111-1111-111111111111',1,@SYS_ADMIN),
('svc-deco-4444','Decoración Quince','Decoración tematica','DECORACION', '44444444-1111-1111-1111-111111111111',1,@SYS_ADMIN),
-- Conciertos (5555)
('svc-sonido-5555','Sonido Profesional','Sonido e ingeniería','SONIDO', '55555555-1111-1111-1111-111111111111',1,@SYS_ADMIN),
('svc-luz-5555','Iluminación','Iluminación de escenarios','ILUMINACION', '55555555-1111-1111-1111-111111111111',1,@SYS_ADMIN),
('svc-seg-5555','Seguridad','Servicios de seguridad y control','SEGURIDAD', '55555555-1111-1111-1111-111111111111',1,@SYS_ADMIN),
('svc-local-5555','Local Concierto','Local para conciertos','LOCAL', '55555555-1111-1111-1111-111111111111',1,@SYS_ADMIN)
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre), tipo_evento_id=VALUES(tipo_evento_id), categoria=VALUES(categoria);

-- Add 2 more servicios per tipo_evento for 10 tipos x 6 servicios = 60
-- (IDs: svc-<tipo>-<n>)
INSERT IGNORE INTO ev_catalogo.servicio (id, nombre, descripcion, categoria, tipo_evento_id, status, created_by) VALUES
('svc-catering-1111-2','Catering Deluxe','Catering premium','CATERING', '11111111-1111-1111-1111-111111111111',1,@SYS_ADMIN),
('svc-bar-1111','Barra Libre','Barra de tragos','BAR', '11111111-1111-1111-1111-111111111111',1,@SYS_ADMIN),
('svc-show-2222','Show Infantil','Show para niños','ENTRETENIMIENTO', '22222222-2222-2222-2222-222222222222',1,@SYS_ADMIN),
('svc-mago-2222','Mago','Show de magia','ENTRETENIMIENTO', '22222222-2222-2222-2222-222222222222',1,@SYS_ADMIN),
('svc-host-3333','Host','Maestro de ceremonias','SERVICIO', '33333333-3333-3333-3333-333333333333',1,@SYS_ADMIN),
('svc-catering-3333','Catering Corporativo','Catering para empresas','CATERING', '33333333-3333-3333-3333-333333333333',1,@SYS_ADMIN),
('svc-catering-4444-2','Catering Deluxe Quince','Catering premium 15 años','CATERING', '44444444-1111-1111-1111-111111111111',1,@SYS_ADMIN),
('svc-foto-4444-2','Fotografía Pro Quince','Fotografía profesional 15 años','FOTOGRAFIA', '44444444-1111-1111-1111-111111111111',1,@SYS_ADMIN),
('svc-backline-5555','Backline','Instrumentos musicales','SONIDO', '55555555-1111-1111-1111-111111111111',1,@SYS_ADMIN),
('svc-catering-5555','Catering Concierto','Catering para conciertos','CATERING', '55555555-1111-1111-1111-111111111111',1,@SYS_ADMIN),
('svc-catering-6666','Catering Baby Shower','Catering para baby shower','CATERING', '66666666-6666-6666-6666-666666666661',1,@SYS_ADMIN),
('svc-foto-6666','Fotografía Baby Shower','Fotografía baby shower','FOTOGRAFIA', '66666666-6666-6666-6666-666666666661',1,@SYS_ADMIN),
('svc-catering-7777','Catering Graduación','Catering para graduación','CATERING', '77777777-7777-7777-7777-777777777771',1,@SYS_ADMIN),
('svc-foto-7777','Fotografía Graduación','Fotografía graduación','FOTOGRAFIA', '77777777-7777-7777-7777-777777777771',1,@SYS_ADMIN),
('svc-catering-8888','Catering Aniversario','Catering para aniversario','CATERING', '88888888-8888-8888-8888-888888888881',1,@SYS_ADMIN),
('svc-foto-8888','Fotografía Aniversario','Fotografía aniversario','FOTOGRAFIA', '88888888-8888-8888-8888-888888888881',1,@SYS_ADMIN),
('svc-catering-9999','Catering Temático','Catering para fiestas temáticas','CATERING', '99999999-9999-9999-9999-999999999991',1,@SYS_ADMIN),
('svc-foto-9999','Fotografía Temática','Fotografía temática','FOTOGRAFIA', '99999999-9999-9999-9999-999999999991',1,@SYS_ADMIN),
('svc-catering-aaaa','Catering Deportivo','Catering para eventos deportivos','CATERING', 'aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaa1',1,@SYS_ADMIN),
('svc-foto-aaaa','Fotografía Deportivo','Fotografía deportiva','FOTOGRAFIA', 'aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaa1',1,@SYS_ADMIN)
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre), tipo_evento_id=VALUES(tipo_evento_id), categoria=VALUES(categoria);

/* ============================================================
   3) Opciones de servicio (opcion_servicio) y precios vigentes
   ============================================================ */
-- Asegurar columnas necesarias para categoría y filtrado por tipo_evento
-- Las columnas `tipo_evento_id` y `categoria` son gestionadas por `db/bootstrap.sql` (idempotente).

INSERT IGNORE INTO ev_catalogo.opcion_servicio (id, servicio_id, nombre, detalles, status, created_by, tipo_evento_id, categoria) VALUES
-- Matrimonio opciones
('op-cater-100','svc-catering-1111','Buffet 100 pax', JSON_OBJECT('capacidad',100,'duracion_horas',5,'personal',4),1,@SYS_ADMIN,'11111111-1111-1111-1111-111111111111','CATERING'),
('op-cater-150','svc-catering-1111','Buffet 150 pax', JSON_OBJECT('capacidad',150,'duracion_horas',5,'personal',5),1,@SYS_ADMIN,'11111111-1111-1111-1111-111111111111','CATERING'),
('op-foto-wed-4h','svc-foto-1111','Fotografía 4h', JSON_OBJECT('duracion_h',4,'incluye','edicion'),1,@SYS_ADMIN,'11111111-1111-1111-1111-111111111111','FOTOGRAFIA'),
('op-dj-wed-6h','svc-musica-1111','DJ 6h', JSON_OBJECT('duracion_h',6,'equipo','completo'),1,@SYS_ADMIN,'11111111-1111-1111-1111-111111111111','ENTRETENIMIENTO'),
('op-deco-wed','svc-deco-1111','Decoración básica', JSON_OBJECT('tipo','boda','incluye','flores'),1,@SYS_ADMIN,'11111111-1111-1111-1111-111111111111',NULL),
-- Cumpleaños opciones
('op-dj-4h','svc-musica-2222','DJ Pro 4h', JSON_OBJECT('duracion_h',4,'equipo','completo'),1,@SYS_ADMIN,'22222222-2222-2222-2222-222222222222','ENTRETENIMIENTO'),
('op-anim-kids','svc-anim-2222','Animación kids', JSON_OBJECT('edad','3-10','duracion_h',3),1,@SYS_ADMIN,'22222222-2222-2222-2222-222222222222',NULL),
('op-foto-bday','svc-foto-2222','Fotografía fiesta', JSON_OBJECT('duracion_h',3),1,@SYS_ADMIN,'22222222-2222-2222-2222-222222222222','FOTOGRAFIA'),
('op-cake-std','svc-cake-2222','Torta 20 porciones', JSON_OBJECT('porciones',20),1,@SYS_ADMIN,'22222222-2222-2222-2222-222222222222','OTRO'),
-- Corporativo opciones
('op-local-med','svc-local-3333','Local mediano', JSON_OBJECT('capacidad',150,'ubicacion','Lima'),1,@SYS_ADMIN,'33333333-3333-3333-3333-333333333333',NULL),
('op-av-standard','svc-av-3333','A/V pack estándar', JSON_OBJECT('incluye','proyector,sonido'),1,@SYS_ADMIN,'33333333-3333-3333-3333-333333333333',NULL),
('op-coffee-std','svc-coffee-3333','Coffee break básico', JSON_OBJECT('personas',50),1,@SYS_ADMIN,'33333333-3333-3333-3333-333333333333',NULL),
('op-deco-corp','svc-deco-3333','Decoración corporativa', JSON_OBJECT('branding',true),1,@SYS_ADMIN,'33333333-3333-3333-3333-333333333333',NULL),
-- Quince opciones
('op-cater-100-q','svc-catering-4444','Buffet 100 pax', JSON_OBJECT('capacidad',100),1,@SYS_ADMIN,'44444444-1111-1111-1111-111111111111','CATERING'),
('op-mus-4h-q','svc-musica-4444','DJ 4h', JSON_OBJECT('duracion_h',4),1,@SYS_ADMIN,'44444444-1111-1111-1111-111111111111','ENTRETENIMIENTO'),
('op-foto-q','svc-foto-4444','Fotografía 4h', JSON_OBJECT('duracion_h',4),1,@SYS_ADMIN,'44444444-1111-1111-1111-111111111111','FOTOGRAFIA'),
('op-deco-q','svc-deco-4444','Decoración tematica', JSON_OBJECT('tema','princesa'),1,@SYS_ADMIN,'44444444-1111-1111-1111-111111111111',NULL),
-- Concierto opciones
('op-sonido-pro','svc-sonido-5555','Sonido Pro', JSON_OBJECT('canales',8),1,@SYS_ADMIN,'55555555-1111-1111-1111-111111111111','ENTRETENIMIENTO'),
('op-luz-basic','svc-luz-5555','Iluminación básica', JSON_OBJECT('canales',6),1,@SYS_ADMIN,'55555555-1111-1111-1111-111111111111',NULL),
('op-seg-std','svc-seg-5555','Seguridad estándar', JSON_OBJECT('guardias',4),1,@SYS_ADMIN,'55555555-1111-1111-1111-111111111111','OTRO'),
('op-local-conc','svc-local-5555','Local grande', JSON_OBJECT('capacidad',1000),1,@SYS_ADMIN,'55555555-1111-1111-1111-111111111111',NULL)
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre), detalles=VALUES(detalles), tipo_evento_id=VALUES(tipo_evento_id), categoria=VALUES(categoria);

-- Add 10+ opciones de servicio for new servicios (op-<servicio>-<n>)
INSERT IGNORE INTO ev_catalogo.opcion_servicio (id, servicio_id, nombre, detalles, status, created_by, tipo_evento_id, categoria) VALUES
('op-catering-1111-2a','svc-catering-1111-2','Buffet 200 pax', JSON_OBJECT('capacidad',200,'duracion_horas',6),1,@SYS_ADMIN,'11111111-1111-1111-1111-111111111111','CATERING'),
('op-bar-1111','svc-bar-1111','Barra Libre Premium', JSON_OBJECT('tragos',50),1,@SYS_ADMIN,'11111111-1111-1111-1111-111111111111','BAR'),
('op-show-2222','svc-show-2222','Show Infantil', JSON_OBJECT('duracion_h',2),1,@SYS_ADMIN,'22222222-2222-2222-2222-222222222222','ENTRETENIMIENTO'),
('op-mago-2222','svc-mago-2222','Show de Magia', JSON_OBJECT('duracion_h',1),1,@SYS_ADMIN,'22222222-2222-2222-2222-222222222222','ENTRETENIMIENTO'),
('op-host-3333','svc-host-3333','Host Corporativo', JSON_OBJECT('idioma','español'),1,@SYS_ADMIN,'33333333-3333-3333-3333-333333333333','OTRO'),
('op-catering-3333','svc-catering-3333','Catering Ejecutivo', JSON_OBJECT('capacidad',80),1,@SYS_ADMIN,'33333333-3333-3333-3333-333333333333','CATERING'),
('op-catering-4444-2a','svc-catering-4444-2','Buffet Deluxe 15 años', JSON_OBJECT('capacidad',120),1,@SYS_ADMIN,'44444444-1111-1111-1111-111111111111','CATERING'),
('op-foto-4444-2','svc-foto-4444-2','Fotografía Pro', JSON_OBJECT('duracion_h',5),1,@SYS_ADMIN,'44444444-1111-1111-1111-111111111111','FOTOGRAFIA'),
('op-backline-5555','svc-backline-5555','Backline Full', JSON_OBJECT('instrumentos',10),1,@SYS_ADMIN,'55555555-1111-1111-1111-111111111111','ENTRETENIMIENTO'),
('op-catering-5555','svc-catering-5555','Catering Backstage', JSON_OBJECT('capacidad',50),1,@SYS_ADMIN,'55555555-1111-1111-1111-111111111111','CATERING'),
('op-catering-6666','svc-catering-6666','Buffet Baby Shower', JSON_OBJECT('capacidad',40),1,@SYS_ADMIN,'66666666-6666-6666-6666-666666666661','CATERING'),
('op-foto-6666','svc-foto-6666','Fotografía Baby', JSON_OBJECT('duracion_h',2),1,@SYS_ADMIN,'66666666-6666-6666-6666-666666666661','FOTOGRAFIA'),
('op-catering-7777','svc-catering-7777','Buffet Graduación', JSON_OBJECT('capacidad',60),1,@SYS_ADMIN,'77777777-7777-7777-7777-777777777771','CATERING'),
('op-foto-7777','svc-foto-7777','Fotografía Graduación', JSON_OBJECT('duracion_h',3),1,@SYS_ADMIN,'77777777-7777-7777-7777-777777777771','FOTOGRAFIA'),
('op-catering-8888','svc-catering-8888','Buffet Aniversario', JSON_OBJECT('capacidad',80),1,@SYS_ADMIN,'88888888-8888-8888-8888-888888888881','CATERING'),
('op-foto-8888','svc-foto-8888','Fotografía Aniversario', JSON_OBJECT('duracion_h',2),1,@SYS_ADMIN,'88888888-8888-8888-8888-888888888881','FOTOGRAFIA'),
('op-catering-9999','svc-catering-9999','Buffet Temático', JSON_OBJECT('capacidad',100),1,@SYS_ADMIN,'99999999-9999-9999-9999-999999999991','CATERING'),
('op-foto-9999','svc-foto-9999','Fotografía Temática', JSON_OBJECT('duracion_h',2),1,@SYS_ADMIN,'99999999-9999-9999-9999-999999999991','FOTOGRAFIA'),
('op-catering-aaaa','svc-catering-aaaa','Buffet Deportivo', JSON_OBJECT('capacidad',120),1,@SYS_ADMIN,'aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaa1','CATERING'),
('op-foto-aaaa','svc-foto-aaaa','Fotografía Deportivo', JSON_OBJECT('duracion_h',2),1,@SYS_ADMIN,'aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaa1','FOTOGRAFIA')
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre), detalles=VALUES(detalles), tipo_evento_id=VALUES(tipo_evento_id), categoria=VALUES(categoria);

-- Add 5 more proveedores, each with 2+ habilidades (multi-servicio)
INSERT IGNORE INTO ev_proveedores.proveedor (id, nombre, categoria, ruc, contacto, direccion, email, telefono, rating_prom, status, created_by) VALUES
('prov-006','BarTest','BAR','20400123456','Carlos Barrios','Av. Pisco 123, Lima','bar@bartest.pe','+51 900111333',4.2,1,@SYS_ADMIN),
('prov-007','ShowTest','ENTRETENIMIENTO','20400123457','María López','Jr. Teatro 45, Lima','show@showtest.pe','+51 900222444',4.1,1,@SYS_ADMIN),
('prov-008','HostTest','SERVICIO','20400123458','Luis Gómez','Calle Ceremonias 12, Lima','host@hosttest.pe','+51 900333555',4.0,1,@SYS_ADMIN),
('prov-009','CateringTest','CATERING','20400123459','Sofía Torres','Av. Banquetes 78, Lima','catering@cateringtest.pe','+51 900444666',4.8,1,@SYS_ADMIN),
('prov-010','PhotoTest','FOTOGRAFIA','20400123460','Andrés Ruiz','Psje. Cámara 9, Lima','photo@phototest.pe','+51 900555777',4.9,1,@SYS_ADMIN)
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre), email=VALUES(email), telefono=VALUES(telefono), categoria=VALUES(categoria), ruc=VALUES(ruc), contacto=VALUES(contacto), direccion=VALUES(direccion), rating_prom=VALUES(rating_prom), status=VALUES(status);

-- Habilidades: cada proveedor tiene 2+ servicios
INSERT IGNORE INTO ev_proveedores.habilidad_proveedor (id, proveedor_id, servicio_id, nivel) VALUES
(UUID(),'prov-006','svc-bar-1111',5),
(UUID(),'prov-006','svc-catering-1111-2',4),
(UUID(),'prov-007','svc-show-2222',5),
(UUID(),'prov-007','svc-mago-2222',4),
(UUID(),'prov-008','svc-host-3333',5),
(UUID(),'prov-008','svc-catering-3333',4),
(UUID(),'prov-009','svc-catering-4444-2',5),
(UUID(),'prov-009','svc-foto-4444-2',4),
(UUID(),'prov-010','svc-foto-8888',5),
(UUID(),'prov-010','svc-foto-9999',4);

-- Calendario: disponibilidad para nuevos proveedores
INSERT IGNORE INTO ev_proveedores.calendario_proveedor (id, proveedor_id, inicio, fin, tipo, created_by) VALUES
(UUID(),'prov-006', DATE_ADD(CURRENT_DATE(), INTERVAL 32 DAY), DATE_ADD(CURRENT_DATE(), INTERVAL 33 DAY), 1, @SYS_ADMIN),
(UUID(),'prov-007', DATE_ADD(CURRENT_DATE(), INTERVAL 33 DAY), DATE_ADD(CURRENT_DATE(), INTERVAL 34 DAY), 1, @SYS_ADMIN),
(UUID(),'prov-008', DATE_ADD(CURRENT_DATE(), INTERVAL 34 DAY), DATE_ADD(CURRENT_DATE(), INTERVAL 35 DAY), 1, @SYS_ADMIN),
(UUID(),'prov-009', DATE_ADD(CURRENT_DATE(), INTERVAL 35 DAY), DATE_ADD(CURRENT_DATE(), INTERVAL 36 DAY), 1, @SYS_ADMIN),
(UUID(),'prov-010', DATE_ADD(CURRENT_DATE(), INTERVAL 36 DAY), DATE_ADD(CURRENT_DATE(), INTERVAL 37 DAY), 1, @SYS_ADMIN);

-- Add 8 more usuarios de prueba (10+ total)
INSERT IGNORE INTO ev_iam.usuario (id, email, password_hash, nombre, telefono, status) VALUES
('user-client-03','cliente3@eventos.test','$bcrypt-sha256$v=2,t=2b,r=12$0mZ35JSikYcRUxPds2IKK.$G/4eI2JPqTURMzE34fgCa2qNRYdlnSC','Cliente Tres','+51 900001003',1),
('user-client-04','cliente4@eventos.test','$bcrypt-sha256$v=2,t=2b,r=12$0mZ35JSikYcRUxPds2IKK.$G/4eI2JPqTURMzE34fgCa2qNRYdlnSC','Cliente Cuatro','+51 900001004',1),
('user-client-05','cliente5@eventos.test','$bcrypt-sha256$v=2,t=2b,r=12$0mZ35JSikYcRUxPds2IKK.$G/4eI2JPqTURMzE34fgCa2qNRYdlnSC','Cliente Cinco','+51 900001005',1),
('user-client-06','cliente6@eventos.test','$bcrypt-sha256$v=2,t=2b,r=12$0mZ35JSikYcRUxPds2IKK.$G/4eI2JPqTURMzE34fgCa2qNRYdlnSC','Cliente Seis','+51 900001006',1),
('user-client-07','cliente7@eventos.test','$bcrypt-sha256$v=2,t=2b,r=12$0mZ35JSikYcRUxPds2IKK.$G/4eI2JPqTURMzE34fgCa2qNRYdlnSC','Cliente Siete','+51 900001007',1),
('user-client-08','cliente8@eventos.test','$bcrypt-sha256$v=2,t=2b,r=12$0mZ35JSikYcRUxPds2IKK.$G/4eI2JPqTURMzE34fgCa2qNRYdlnSC','Cliente Ocho','+51 900001008',1),
('user-client-09','cliente9@eventos.test','$bcrypt-sha256$v=2,t=2b,r=12$0mZ35JSikYcRUxPds2IKK.$G/4eI2JPqTURMzE34fgCa2qNRYdlnSC','Cliente Nueve','+51 900001009',1),
('user-client-10','cliente10@eventos.test','$bcrypt-sha256$v=2,t=2b,r=12$0mZ35JSikYcRUxPds2IKK.$G/4eI2JPqTURMzE34fgCa2qNRYdlnSC','Cliente Diez','+51 900001010',1);

-- Roles para nuevos usuarios
INSERT IGNORE INTO ev_iam.usuario_rol (id, usuario_id, rol_id) VALUES
(UUID(),'user-client-03','aaaa1111-1111-1111-1111-aaaaaaaaaaa2'),
(UUID(),'user-client-04','aaaa1111-1111-1111-1111-aaaaaaaaaaa2'),
(UUID(),'user-client-05','aaaa1111-1111-1111-1111-aaaaaaaaaaa2'),
(UUID(),'user-client-06','aaaa1111-1111-1111-1111-aaaaaaaaaaa2'),
(UUID(),'user-client-07','aaaa1111-1111-1111-1111-aaaaaaaaaaa2'),
(UUID(),'user-client-08','aaaa1111-1111-1111-1111-aaaaaaaaaaa2'),
(UUID(),'user-client-09','aaaa1111-1111-1111-1111-aaaaaaaaaaa2'),
(UUID(),'user-client-10','aaaa1111-1111-1111-1111-aaaaaaaaaaa2');

-- Add 8 more pedidos, items, holds, reservas for coverage
-- Pedidos: clientes 3-10, tipos de evento variados
INSERT IGNORE INTO ev_contratacion.pedido_evento (id, cliente_id, tipo_evento_id, fecha_evento, hora_inicio, hora_fin, ubicacion, moneda, status, correlation_id, request_id, created_by)
VALUES
('ped-0003', 'user-client-03', '44444444-1111-1111-1111-111111111111', DATE_ADD(CURRENT_DATE(), INTERVAL 50 DAY), '18:00:00','23:00:00','Surco','PEN',1,'corr-ped-0003','req-ped-0003', 'user-client-03'),
('ped-0004', 'user-client-04', '55555555-1111-1111-1111-111111111111', DATE_ADD(CURRENT_DATE(), INTERVAL 60 DAY), '19:00:00','02:00:00','Barranco','PEN',1,'corr-ped-0004','req-ped-0004', 'user-client-04'),
('ped-0005', 'user-client-05', '66666666-6666-6666-6666-666666666661', DATE_ADD(CURRENT_DATE(), INTERVAL 70 DAY), '10:00:00','15:00:00','San Borja','PEN',1,'corr-ped-0005','req-ped-0005', 'user-client-05'),
('ped-0006', 'user-client-06', '77777777-7777-7777-7777-777777777771', DATE_ADD(CURRENT_DATE(), INTERVAL 80 DAY), '11:00:00','16:00:00','La Molina','PEN',1,'corr-ped-0006','req-ped-0006', 'user-client-06'),
('ped-0007', 'user-client-07', '88888888-8888-8888-8888-888888888881', DATE_ADD(CURRENT_DATE(), INTERVAL 90 DAY), '12:00:00','17:00:00','San Miguel','PEN',1,'corr-ped-0007','req-ped-0007', 'user-client-07'),
('ped-0008', 'user-client-08', '99999999-9999-9999-9999-999999999991', DATE_ADD(CURRENT_DATE(), INTERVAL 100 DAY), '13:00:00','18:00:00','Callao','PEN',1,'corr-ped-0008','req-ped-0008', 'user-client-08'),
('ped-0009', 'user-client-09', 'aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaa1', DATE_ADD(CURRENT_DATE(), INTERVAL 110 DAY), '14:00:00','19:00:00','Chorrillos','PEN',1,'corr-ped-0009','req-ped-0009', 'user-client-09'),
('ped-0010', 'user-client-10', '11111111-1111-1111-1111-111111111111', DATE_ADD(CURRENT_DATE(), INTERVAL 120 DAY), '15:00:00','20:00:00','Lince','PEN',1,'corr-ped-0010','req-ped-0010', 'user-client-10')
ON DUPLICATE KEY UPDATE fecha_evento=VALUES(fecha_evento);

-- Items para nuevos pedidos (servicios variados)
INSERT IGNORE INTO ev_contratacion.item_pedido_evento (id, pedido_id, opcion_servicio_id, nombre_servicio, cantidad, precio_unitario, subtotal, tipo_item, referencia_id, created_by)
VALUES
('it-ped-0003-1','ped-0003','op-catering-4444-2a','Buffet Deluxe 15 años',1,8000.00,8000.00,'SERVICIO',NULL,'user-client-03'),
('it-ped-0004-1','ped-0004','op-backline-5555','Backline Full',1,15000.00,15000.00,'SERVICIO',NULL,'user-client-04'),
('it-ped-0005-1','ped-0005','op-catering-6666','Buffet Baby Shower',1,2500.00,2500.00,'SERVICIO',NULL,'user-client-05'),
('it-ped-0006-1','ped-0006','op-catering-7777','Buffet Graduación',1,3000.00,3000.00,'SERVICIO',NULL,'user-client-06'),
('it-ped-0007-1','ped-0007','op-catering-8888','Buffet Aniversario',1,3500.00,3500.00,'SERVICIO',NULL,'user-client-07'),
('it-ped-0008-1','ped-0008','op-catering-9999','Buffet Temático',1,4000.00,4000.00,'SERVICIO',NULL,'user-client-08'),
('it-ped-0009-1','ped-0009','op-catering-aaaa','Buffet Deportivo',1,4500.00,4500.00,'SERVICIO',NULL,'user-client-09'),
('it-ped-0010-1','ped-0010','op-cater-100','Buffet 100 pax',1,6500.00,6500.00,'SERVICIO',NULL,'user-client-10');

-- Update monto_total for pedidos ped-0003 .. ped-0010 (ensure totals reflect inserted items)
UPDATE ev_contratacion.pedido_evento pe
JOIN (
   SELECT pedido_id, COALESCE(SUM(COALESCE(subtotal,0)),0) as total
   FROM ev_contratacion.item_pedido_evento
   WHERE pedido_id IN ('ped-0003','ped-0004','ped-0005','ped-0006','ped-0007','ped-0008','ped-0009','ped-0010')
   GROUP BY pedido_id
) t ON pe.id = t.pedido_id
SET pe.monto_total = t.total
WHERE pe.id IN ('ped-0003','ped-0004','ped-0005','ped-0006','ped-0007','ped-0008','ped-0009','ped-0010');

-- Holds para nuevos pedidos
INSERT IGNORE INTO ev_proveedores.reserva_temporal (id, proveedor_id, opcion_servicio_id, inicio, fin, status, expira_en, correlation_id, created_by)
VALUES
('hold-0002','prov-006','op-bar-1111', DATE_ADD(CURRENT_DATE(), INTERVAL 50 DAY), DATE_ADD(DATE_ADD(CURRENT_DATE(), INTERVAL 50 DAY), INTERVAL 2 HOUR), 0, DATE_ADD(NOW(), INTERVAL 60 MINUTE), 'corr-hold-0002', 'user-client-03'),
('hold-0003','prov-007','op-show-2222', DATE_ADD(CURRENT_DATE(), INTERVAL 60 DAY), DATE_ADD(DATE_ADD(CURRENT_DATE(), INTERVAL 60 DAY), INTERVAL 2 HOUR), 0, DATE_ADD(NOW(), INTERVAL 60 MINUTE), 'corr-hold-0003', 'user-client-04'),
('hold-0004','prov-008','op-host-3333', DATE_ADD(CURRENT_DATE(), INTERVAL 70 DAY), DATE_ADD(DATE_ADD(CURRENT_DATE(), INTERVAL 70 DAY), INTERVAL 2 HOUR), 0, DATE_ADD(NOW(), INTERVAL 60 MINUTE), 'corr-hold-0004', 'user-client-05'),
('hold-0005','prov-009','op-catering-4444-2a', DATE_ADD(CURRENT_DATE(), INTERVAL 80 DAY), DATE_ADD(DATE_ADD(CURRENT_DATE(), INTERVAL 80 DAY), INTERVAL 2 HOUR), 0, DATE_ADD(NOW(), INTERVAL 60 MINUTE), 'corr-hold-0005', 'user-client-06'),
('hold-0006','prov-010','op-foto-8888', DATE_ADD(CURRENT_DATE(), INTERVAL 90 DAY), DATE_ADD(DATE_ADD(CURRENT_DATE(), INTERVAL 90 DAY), INTERVAL 2 HOUR), 0, DATE_ADD(NOW(), INTERVAL 60 MINUTE), 'corr-hold-0006', 'user-client-07'),
('hold-0007','prov-001','op-cater-100', DATE_ADD(CURRENT_DATE(), INTERVAL 100 DAY), DATE_ADD(DATE_ADD(CURRENT_DATE(), INTERVAL 100 DAY), INTERVAL 2 HOUR), 0, DATE_ADD(NOW(), INTERVAL 60 MINUTE), 'corr-hold-0007', 'user-client-08'),
('hold-0008','prov-002','op-dj-4h', DATE_ADD(CURRENT_DATE(), INTERVAL 110 DAY), DATE_ADD(DATE_ADD(CURRENT_DATE(), INTERVAL 110 DAY), INTERVAL 2 HOUR), 0, DATE_ADD(NOW(), INTERVAL 60 MINUTE), 'corr-hold-0008', 'user-client-09'),
('hold-0009','prov-003','op-local-med', DATE_ADD(CURRENT_DATE(), INTERVAL 120 DAY), DATE_ADD(DATE_ADD(CURRENT_DATE(), INTERVAL 120 DAY), INTERVAL 2 HOUR), 0, DATE_ADD(NOW(), INTERVAL 60 MINUTE), 'corr-hold-0009', 'user-client-10');

-- Reservas confirmadas para nuevos pedidos
INSERT IGNORE INTO ev_contratacion.reserva (id, item_pedido_id, proveedor_id, inicio, fin, status, hold_id, created_by)
VALUES
('res-0002','it-ped-0003-1','prov-006', DATE_ADD(CURRENT_DATE(), INTERVAL 50 DAY), DATE_ADD(DATE_ADD(CURRENT_DATE(), INTERVAL 50 DAY), INTERVAL 4 HOUR), 1, 'hold-0002', 'user-client-03'),
('res-0003','it-ped-0004-1','prov-007', DATE_ADD(CURRENT_DATE(), INTERVAL 60 DAY), DATE_ADD(DATE_ADD(CURRENT_DATE(), INTERVAL 60 DAY), INTERVAL 4 HOUR), 1, 'hold-0003', 'user-client-04'),
('res-0004','it-ped-0005-1','prov-008', DATE_ADD(CURRENT_DATE(), INTERVAL 70 DAY), DATE_ADD(DATE_ADD(CURRENT_DATE(), INTERVAL 70 DAY), INTERVAL 4 HOUR), 1, 'hold-0004', 'user-client-05'),
('res-0005','it-ped-0006-1','prov-009', DATE_ADD(CURRENT_DATE(), INTERVAL 80 DAY), DATE_ADD(DATE_ADD(CURRENT_DATE(), INTERVAL 80 DAY), INTERVAL 4 HOUR), 1, 'hold-0005', 'user-client-06'),
('res-0006','it-ped-0007-1','prov-010', DATE_ADD(CURRENT_DATE(), INTERVAL 90 DAY), DATE_ADD(DATE_ADD(CURRENT_DATE(), INTERVAL 90 DAY), INTERVAL 4 HOUR), 1, 'hold-0006', 'user-client-07'),
('res-0007','it-ped-0008-1','prov-001', DATE_ADD(CURRENT_DATE(), INTERVAL 100 DAY), DATE_ADD(DATE_ADD(CURRENT_DATE(), INTERVAL 100 DAY), INTERVAL 4 HOUR), 1, 'hold-0007', 'user-client-08'),
('res-0008','it-ped-0009-1','prov-002', DATE_ADD(CURRENT_DATE(), INTERVAL 110 DAY), DATE_ADD(DATE_ADD(CURRENT_DATE(), INTERVAL 110 DAY), INTERVAL 4 HOUR), 1, 'hold-0008', 'user-client-09'),
('res-0009','it-ped-0010-1','prov-003', DATE_ADD(CURRENT_DATE(), INTERVAL 120 DAY), DATE_ADD(DATE_ADD(CURRENT_DATE(), INTERVAL 120 DAY), INTERVAL 4 HOUR), 1, 'hold-0009', 'user-client-10');

-- Precios vigentes para las opciones (monto fijo determinístico)
INSERT IGNORE INTO ev_catalogo.precio_servicio (id, opcion_servicio_id, moneda, monto, vigente_desde, vigente_hasta, created_by) VALUES
(UUID(), 'op-cater-100', 'PEN', 6500.00, CURRENT_DATE(), NULL, @SYS_ADMIN),
(UUID(), 'op-cater-150', 'PEN', 9000.00, CURRENT_DATE(), NULL, @SYS_ADMIN),
(UUID(), 'op-foto-wed-4h', 'PEN', 2200.00, CURRENT_DATE(), NULL, @SYS_ADMIN),
(UUID(), 'op-dj-wed-6h', 'PEN', 2600.00, CURRENT_DATE(), NULL, @SYS_ADMIN),
(UUID(), 'op-deco-wed', 'PEN', 1800.00, CURRENT_DATE(), NULL, @SYS_ADMIN),
(UUID(), 'op-dj-4h', 'PEN', 1800.00, CURRENT_DATE(), NULL, @SYS_ADMIN),
(UUID(), 'op-anim-kids', 'PEN', 900.00, CURRENT_DATE(), NULL, @SYS_ADMIN),
(UUID(), 'op-foto-bday', 'PEN', 1200.00, CURRENT_DATE(), NULL, @SYS_ADMIN),
(UUID(), 'op-cake-std', 'PEN', 350.00, CURRENT_DATE(), NULL, @SYS_ADMIN),
(UUID(), 'op-local-med', 'PEN', 4000.00, CURRENT_DATE(), NULL, @SYS_ADMIN),
(UUID(), 'op-av-standard', 'PEN', 1500.00, CURRENT_DATE(), NULL, @SYS_ADMIN),
(UUID(), 'op-coffee-std', 'PEN', 800.00, CURRENT_DATE(), NULL, @SYS_ADMIN),
(UUID(), 'op-deco-corp', 'PEN', 1200.00, CURRENT_DATE(), NULL, @SYS_ADMIN),
(UUID(), 'op-cater-100-q', 'PEN', 6500.00, CURRENT_DATE(), NULL, @SYS_ADMIN),
(UUID(), 'op-mus-4h-q', 'PEN', 1800.00, CURRENT_DATE(), NULL, @SYS_ADMIN),
(UUID(), 'op-foto-q', 'PEN', 2200.00, CURRENT_DATE(), NULL, @SYS_ADMIN),
(UUID(), 'op-deco-q', 'PEN', 1600.00, CURRENT_DATE(), NULL, @SYS_ADMIN),
(UUID(), 'op-sonido-pro', 'PEN', 12000.00, CURRENT_DATE(), NULL, @SYS_ADMIN),
(UUID(), 'op-luz-basic', 'PEN', 4500.00, CURRENT_DATE(), NULL, @SYS_ADMIN),
(UUID(), 'op-seg-std', 'PEN', 2000.00, CURRENT_DATE(), NULL, @SYS_ADMIN),
(UUID(), 'op-local-conc', 'PEN', 25000.00, CURRENT_DATE(), NULL, @SYS_ADMIN);

-- Precios explícitos para opciones agregadas dinámicamente y opciones nuevas
INSERT IGNORE INTO ev_catalogo.precio_servicio (id, opcion_servicio_id, moneda, monto, vigente_desde, vigente_hasta, created_by) VALUES
(UUID(),'op-backline-5555','PEN',12000.00,CURRENT_DATE(),NULL,@SYS_ADMIN),
(UUID(),'op-bar-1111','PEN',2000.00,CURRENT_DATE(),NULL,@SYS_ADMIN),
(UUID(),'op-show-2222','PEN',1500.00,CURRENT_DATE(),NULL,@SYS_ADMIN),
(UUID(),'op-mago-2222','PEN',1200.00,CURRENT_DATE(),NULL,@SYS_ADMIN),
(UUID(),'op-host-3333','PEN',900.00,CURRENT_DATE(),NULL,@SYS_ADMIN),
(UUID(),'op-catering-3333','PEN',7000.00,CURRENT_DATE(),NULL,@SYS_ADMIN),
(UUID(),'op-catering-1111-2a','PEN',12500.00,CURRENT_DATE(),NULL,@SYS_ADMIN),
(UUID(),'op-catering-4444-2a','PEN',8000.00,CURRENT_DATE(),NULL,@SYS_ADMIN),
(UUID(),'op-foto-4444-2','PEN',3000.00,CURRENT_DATE(),NULL,@SYS_ADMIN),
(UUID(),'op-catering-5555','PEN',18000.00,CURRENT_DATE(),NULL,@SYS_ADMIN),
(UUID(),'op-catering-6666','PEN',2200.00,CURRENT_DATE(),NULL,@SYS_ADMIN),
(UUID(),'op-foto-6666','PEN',1300.00,CURRENT_DATE(),NULL,@SYS_ADMIN),
(UUID(),'op-catering-7777','PEN',3200.00,CURRENT_DATE(),NULL,@SYS_ADMIN),
(UUID(),'op-foto-7777','PEN',1400.00,CURRENT_DATE(),NULL,@SYS_ADMIN),
(UUID(),'op-catering-8888','PEN',3500.00,CURRENT_DATE(),NULL,@SYS_ADMIN),
(UUID(),'op-foto-8888','PEN',1500.00,CURRENT_DATE(),NULL,@SYS_ADMIN),
(UUID(),'op-catering-9999','PEN',4000.00,CURRENT_DATE(),NULL,@SYS_ADMIN),
(UUID(),'op-foto-9999','PEN',1600.00,CURRENT_DATE(),NULL,@SYS_ADMIN),
(UUID(),'op-catering-aaaa','PEN',4500.00,CURRENT_DATE(),NULL,@SYS_ADMIN),
(UUID(),'op-foto-aaaa','PEN',1700.00,CURRENT_DATE(),NULL,@SYS_ADMIN)
ON DUPLICATE KEY UPDATE monto=VALUES(monto), vigente_hasta=VALUES(vigente_hasta);

-- Actualizar `opcion_servicio` para incluir `tipo_evento_id` y `categoria` para que el frontend muestre categoría
UPDATE ev_catalogo.opcion_servicio SET tipo_evento_id = '11111111-1111-1111-1111-111111111111', categoria = 'CATERING' WHERE id IN ('op-cater-100','op-cater-150','op-cater-100-q');
UPDATE ev_catalogo.opcion_servicio SET tipo_evento_id = '11111111-1111-1111-1111-111111111111', categoria = 'FOTOGRAFIA' WHERE id IN ('op-foto-wed-4h','op-foto-q');
UPDATE ev_catalogo.opcion_servicio SET tipo_evento_id = '11111111-1111-1111-1111-111111111111', categoria = 'ENTRETENIMIENTO' WHERE id IN ('op-dj-wed-6h');

UPDATE ev_catalogo.opcion_servicio SET tipo_evento_id = '22222222-2222-2222-2222-222222222222', categoria = 'ENTRETENIMIENTO' WHERE id IN ('op-dj-4h','op-anim-kids');
UPDATE ev_catalogo.opcion_servicio SET tipo_evento_id = '22222222-2222-2222-2222-222222222222', categoria = 'FOTOGRAFIA' WHERE id IN ('op-foto-bday');
UPDATE ev_catalogo.opcion_servicio SET tipo_evento_id = '22222222-2222-2222-2222-222222222222', categoria = 'OTRO' WHERE id IN ('op-cake-std');

UPDATE ev_catalogo.opcion_servicio SET tipo_evento_id = '33333333-3333-3333-3333-333333333333', categoria = 'OTRO' WHERE id IN ('op-local-med','op-av-standard','op-coffee-std','op-deco-corp');

UPDATE ev_catalogo.opcion_servicio SET tipo_evento_id = '44444444-1111-1111-1111-111111111111', categoria = 'CATERING' WHERE id IN ('op-cater-100-q');
UPDATE ev_catalogo.opcion_servicio SET tipo_evento_id = '44444444-1111-1111-1111-111111111111', categoria = 'ENTRETENIMIENTO' WHERE id IN ('op-mus-4h-q');
UPDATE ev_catalogo.opcion_servicio SET tipo_evento_id = '44444444-1111-1111-1111-111111111111', categoria = 'FOTOGRAFIA' WHERE id IN ('op-foto-q');

UPDATE ev_catalogo.opcion_servicio SET tipo_evento_id = '55555555-1111-1111-1111-111111111111', categoria = 'ENTRETENIMIENTO' WHERE id IN ('op-sonido-pro','op-luz-basic');
UPDATE ev_catalogo.opcion_servicio SET tipo_evento_id = '55555555-1111-1111-1111-111111111111', categoria = 'OTRO' WHERE id IN ('op-seg-std','op-local-conc');

-- Asegurar que todas las opciones tengan `tipo_evento_id` heredado del servicio si está vacío
-- Algunos clientes (MySQL Workbench en modo "safe updates") rechazan UPDATEs
-- que no usan una columna KEY en la cláusula WHERE (Error 1175). Para permitir
-- que este script sea ejecutable desde esos clientes, desactivamos temporalmente
-- la comprobación SQL_SAFE_UPDATES en la sesión, ejecutamos los UPDATEs y la
-- restauramos.
-- En lugar de desactivar SQL_SAFE_UPDATES (que algunos clientes no permiten),
-- hacemos UPDATEs que usan la columna KEY `id` en la cláusula WHERE. Para
-- evitar problemas con subconsultas que referencian la misma tabla, envolvemos
-- el SELECT en un derived table.

UPDATE ev_catalogo.opcion_servicio os
JOIN ev_catalogo.servicio s ON s.id = os.servicio_id
SET os.tipo_evento_id = s.tipo_evento_id
WHERE os.id IN (
   SELECT id FROM (
      SELECT id FROM ev_catalogo.opcion_servicio WHERE tipo_evento_id IS NULL
   ) AS _tmp
);

-- Rellenar categoría por defecto donde falte (usando id en WHERE para cumplir safe-updates)
UPDATE ev_catalogo.opcion_servicio
SET categoria = 'OTRO'
WHERE id IN (
   SELECT id FROM (
      SELECT id FROM ev_catalogo.opcion_servicio WHERE categoria IS NULL
   ) AS _tmp2
);

/* ============================================================
   4) Paquetes representativos por tipo_evento
   ============================================================ */
INSERT IGNORE INTO ev_paquetes.paquete (id, codigo, nombre, descripcion, status, created_by) VALUES
('pkg-matr-0001','PKG-MATR-STD','Paquete Matrimonio Básico','Catering 100p + Fotografía 4h',1,@SYS_ADMIN),
('pkg-cum-0001','PKG-CUMP-STD','Paquete Cumpleaños','Buffet 100p + DJ 4h',1,@SYS_ADMIN),
('pkg-corp-0001','PKG-CORP-STD','Paquete Corporativo','Local mediano + Decoración estándar',1,@SYS_ADMIN)
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre), descripcion=VALUES(descripcion);

-- Ítems de paquetes (referencian opciones creadas arriba)
INSERT IGNORE INTO ev_paquetes.item_paquete (id, paquete_id, opcion_servicio_id, cantidad) VALUES
('ipkg-matr-1','pkg-matr-0001','op-cater-100',1),
('ipkg-matr-2','pkg-matr-0001','op-foto-wed-4h',1),
('ipkg-cum-1','pkg-cum-0001','op-cater-100',1),
('ipkg-cum-2','pkg-cum-0001','op-dj-4h',1),
('ipkg-corp-1','pkg-corp-0001','op-local-med',1),
('ipkg-corp-2','pkg-corp-0001','op-deco-corp',1)
ON DUPLICATE KEY UPDATE cantidad=VALUES(cantidad);

-- Precio vigente para paquetes (monto calculado aproximado)
INSERT IGNORE INTO ev_paquetes.precio_paquete (id, paquete_id, moneda, monto, vigente_desde, vigente_hasta, created_by) VALUES
(UUID(),'pkg-matr-0001','PEN',8700.00,CURRENT_DATE(),NULL,@SYS_ADMIN),
(UUID(),'pkg-cum-0001','PEN',8300.00,CURRENT_DATE(),NULL,@SYS_ADMIN),
(UUID(),'pkg-corp-0001','PEN',5200.00,CURRENT_DATE(),NULL,@SYS_ADMIN);

-- Paquetes adicionales: 2 paquetes extra por tipo_evento (idempotente)
INSERT IGNORE INTO ev_paquetes.paquete (id, codigo, nombre, descripcion, status, created_by) VALUES
('pkg-matr-0002','PKG-MATR-PLUS','Paquete Matrimonio Plus','Catering 150p + DJ 6h + Decoración',1,@SYS_ADMIN),
('pkg-matr-0003','PKG-MATR-PREMIUM','Paquete Matrimonio Premium','Catering 150p + Fotografía 4h + Decoración',1,@SYS_ADMIN),
('pkg-cum-0002','PKG-CUMP-PLUS','Paquete Cumpleaños Plus','Buffet 150p + Animación',1,@SYS_ADMIN),
('pkg-cum-0003','PKG-CUMP-PREMIUM','Paquete Cumpleaños Premium','Buffet 150p + DJ 4h + Foto',1,@SYS_ADMIN),
('pkg-corp-0002','PKG-CORP-PLUS','Paquete Corporativo Plus','Local mediano + A/V pack',1,@SYS_ADMIN),
('pkg-corp-0003','PKG-CORP-PREMIUM','Paquete Corporativo Premium','Local mediano + Coffee break + Decoración',1,@SYS_ADMIN),
('pkg-quince-0001','PKG-QUINCE-STD','Paquete Quince Estándar','Catering 100p + Música 4h',1,@SYS_ADMIN),
('pkg-quince-0002','PKG-QUINCE-PLUS','Paquete Quince Plus','Catering 100p + Fotografía 4h + Decoración',1,@SYS_ADMIN),
('pkg-conc-0001','PKG-CONC-STD','Paquete Concierto Estándar','Sonido Pro + Iluminación básica',1,@SYS_ADMIN),
('pkg-conc-0002','PKG-CONC-PLUS','Paquete Concierto Plus','Sonido Pro + Iluminación + Seguridad',1,@SYS_ADMIN)
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre), descripcion=VALUES(descripcion);

-- Items para paquetes adicionales (usar opciones existentes)
INSERT IGNORE INTO ev_paquetes.item_paquete (id, paquete_id, opcion_servicio_id, cantidad) VALUES
('ipkg-matr-3','pkg-matr-0002','op-cater-150',1),
('ipkg-matr-4','pkg-matr-0002','op-dj-wed-6h',1),
('ipkg-matr-5','pkg-matr-0002','op-deco-wed',1),
('ipkg-matr-6','pkg-matr-0003','op-cater-150',1),
('ipkg-matr-7','pkg-matr-0003','op-foto-wed-4h',1),
('ipkg-matr-8','pkg-matr-0003','op-deco-wed',1),
('ipkg-cum-3','pkg-cum-0002','op-cater-150',1),
('ipkg-cum-4','pkg-cum-0002','op-anim-kids',1),
('ipkg-cum-5','pkg-cum-0003','op-cater-150',1),
('ipkg-cum-6','pkg-cum-0003','op-dj-4h',1),
('ipkg-cum-7','pkg-cum-0003','op-foto-bday',1),
('ipkg-corp-3','pkg-corp-0002','op-local-med',1),
('ipkg-corp-4','pkg-corp-0002','op-av-standard',1),
('ipkg-corp-5','pkg-corp-0003','op-local-med',1),
('ipkg-corp-6','pkg-corp-0003','op-coffee-std',1),
('ipkg-corp-7','pkg-corp-0003','op-deco-corp',1),
('ipkg-quince-1','pkg-quince-0001','op-cater-100-q',1),
('ipkg-quince-2','pkg-quince-0001','op-mus-4h-q',1),
('ipkg-quince-3','pkg-quince-0001','op-foto-q',1),
('ipkg-quince-4','pkg-quince-0002','op-cater-100-q',1),
('ipkg-quince-5','pkg-quince-0002','op-foto-q',1),
('ipkg-conc-1','pkg-conc-0001','op-sonido-pro',1),
('ipkg-conc-2','pkg-conc-0001','op-luz-basic',1),
('ipkg-conc-3','pkg-conc-0002','op-sonido-pro',1),
('ipkg-conc-4','pkg-conc-0002','op-luz-basic',1),
('ipkg-conc-5','pkg-conc-0002','op-seg-std',1)
ON DUPLICATE KEY UPDATE cantidad=VALUES(cantidad);

-- Precios para paquetes adicionales
INSERT IGNORE INTO ev_paquetes.precio_paquete (id, paquete_id, moneda, monto, vigente_desde, vigente_hasta, created_by) VALUES
(UUID(),'pkg-matr-0002','PEN',11500.00,CURRENT_DATE(),NULL,@SYS_ADMIN),
(UUID(),'pkg-matr-0003','PEN',14200.00,CURRENT_DATE(),NULL,@SYS_ADMIN),
(UUID(),'pkg-cum-0002','PEN',9800.00,CURRENT_DATE(),NULL,@SYS_ADMIN),
(UUID(),'pkg-cum-0003','PEN',12500.00,CURRENT_DATE(),NULL,@SYS_ADMIN),
(UUID(),'pkg-corp-0002','PEN',7200.00,CURRENT_DATE(),NULL,@SYS_ADMIN),
(UUID(),'pkg-corp-0003','PEN',9200.00,CURRENT_DATE(),NULL,@SYS_ADMIN),
(UUID(),'pkg-quince-0001','PEN',9900.00,CURRENT_DATE(),NULL,@SYS_ADMIN),
(UUID(),'pkg-quince-0002','PEN',12800.00,CURRENT_DATE(),NULL,@SYS_ADMIN),
(UUID(),'pkg-conc-0001','PEN',30500.00,CURRENT_DATE(),NULL,@SYS_ADMIN),
(UUID(),'pkg-conc-0002','PEN',36000.00,CURRENT_DATE(),NULL,@SYS_ADMIN);

/* ============================================================
   5) Proveedores y habilidades
   ============================================================ */
INSERT IGNORE INTO ev_proveedores.proveedor (id, nombre, categoria, ruc, contacto, direccion, email, telefono, rating_prom, status, created_by) VALUES
('prov-001','SazonTest','CATERING','20123456789','Juan Pérez','Av. La Cocina 123, Lima','contacto@sazontest.pe','+51 900111222',4.7,1,@SYS_ADMIN),
('prov-002','DJTest','MUSICA','20123456780','Diego Ramos','Jr. Ritmo 45, Lima','dj@djtest.pe','+51 900333444',4.6,1,@SYS_ADMIN),
('prov-003','LocalTest','LOCAL','20123456781','Mariana Fuentes','Av. Eventos 200, Lima','local@localtest.pe','+51 900555666',4.5,1,@SYS_ADMIN),
('prov-004','FotoTest','FOTOGRAFIA','20123456782','Carlos Medina','Calle Flash 12, Lima','foto@fototest.pe','+51 900777888',4.4,1,@SYS_ADMIN),
('prov-005','DecoTest','DECORACION','20123456783','Laura Peña','Jr. Flores 88, Lima','deco@decotest.pe','+51 900999000',4.3,1,@SYS_ADMIN)
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre), email=VALUES(email), telefono=VALUES(telefono), categoria=VALUES(categoria), ruc=VALUES(ruc), contacto=VALUES(contacto), direccion=VALUES(direccion), rating_prom=VALUES(rating_prom), status=VALUES(status);

INSERT IGNORE INTO ev_proveedores.habilidad_proveedor (id, proveedor_id, servicio_id, nivel) VALUES
(UUID(),'prov-001','svc-catering-1111',5),
(UUID(),'prov-002','svc-musica-2222',5),
(UUID(),'prov-003','svc-local-3333',5),
(UUID(),'prov-004','svc-foto-4444',5),
(UUID(),'prov-005','svc-deco-5555',5);

-- Calendario simple: cada proveedor tiene disponibilidad en +30 dias
INSERT IGNORE INTO ev_proveedores.calendario_proveedor (id, proveedor_id, inicio, fin, tipo, created_by) VALUES
(UUID(),'prov-001', DATE_ADD(CURRENT_DATE(), INTERVAL 30 DAY), DATE_ADD(CURRENT_DATE(), INTERVAL 31 DAY), 1, @SYS_ADMIN),
(UUID(),'prov-002', DATE_ADD(CURRENT_DATE(), INTERVAL 30 DAY), DATE_ADD(CURRENT_DATE(), INTERVAL 31 DAY), 1, @SYS_ADMIN),
(UUID(),'prov-003', DATE_ADD(CURRENT_DATE(), INTERVAL 30 DAY), DATE_ADD(CURRENT_DATE(), INTERVAL 31 DAY), 1, @SYS_ADMIN),
(UUID(),'prov-004', DATE_ADD(CURRENT_DATE(), INTERVAL 31 DAY), DATE_ADD(CURRENT_DATE(), INTERVAL 32 DAY), 1, @SYS_ADMIN),
(UUID(),'prov-005', DATE_ADD(CURRENT_DATE(), INTERVAL 30 DAY), DATE_ADD(CURRENT_DATE(), INTERVAL 31 DAY), 1, @SYS_ADMIN);

/* ============================================================
   6) Usuarios de prueba + roles
   ============================================================ */
INSERT IGNORE INTO ev_iam.usuario (id, email, password_hash, nombre, telefono, status) VALUES
('user-client-01','cliente1@eventos.test','$bcrypt-sha256$v=2,t=2b,r=12$0mZ35JSikYcRUxPds2IKK.$G/4eI2JPqTURMzE34fgCa2qNRYdlnSC','Cliente Uno','+51 900001001',1),
('user-client-02','cliente2@eventos.test','$bcrypt-sha256$v=2,t=2b,r=12$0mZ35JSikYcRUxPds2IKK.$G/4eI2JPqTURMzE34fgCa2qNRYdlnSC','Cliente Dos','+51 900001002',1);

INSERT IGNORE INTO ev_iam.usuario_rol (id, usuario_id, rol_id) VALUES
(UUID(),'user-client-01','aaaa1111-1111-1111-1111-aaaaaaaaaaa2'),
(UUID(),'user-client-02','aaaa1111-1111-1111-1111-aaaaaaaaaaa2');

-- Asegurar que `admin@eventos.pe` tenga rol ADMIN y crear cliente de prueba
INSERT IGNORE INTO ev_iam.usuario (id, email, password_hash, nombre, telefono, status) VALUES
('ee111111-1111-4111-8111-aaaaaaaaaaa1','admin@eventos.pe','$bcrypt-sha256$v=2,t=2b,r=12$0mZ35JSikYcRUxPds2IKK.$G/4eI2JPqTURMzE34fgCa2qNRYdlnSC','Administrador Principal','+51 900 111 000',1),
('user-test-01','test.cliente@eventos.pe','$bcrypt-sha256$v=2,t=2b,r=12$0vbWQ1NS7Ocmbvm4Zbh3te$79/YApTBj2dOhlQjxtKnrMJaz/lyWtW','Cliente Test','+51 900002002',1)
ON DUPLICATE KEY UPDATE email=VALUES(email), nombre=VALUES(nombre);

INSERT IGNORE INTO ev_iam.usuario_rol (id, usuario_id, rol_id) VALUES
('ur-admin-0001','ee111111-1111-4111-8111-aaaaaaaaaaa1','aaaa1111-1111-1111-1111-aaaaaaaaaaa1'),
('ur-test-0001','user-test-01','aaaa1111-1111-1111-1111-aaaaaaaaaaa2');

/* ============================================================
   7) Pedidos de ejemplo (draft -> cotizado) + items
   ============================================================ */
-- Pedido 1: demo user, paquete matrimonio
INSERT IGNORE INTO ev_contratacion.pedido_evento (id, cliente_id, tipo_evento_id, fecha_evento, hora_inicio, hora_fin, ubicacion, moneda, status, correlation_id, request_id, created_by)
VALUES
('ped-0001', @DEMO_USER, '11111111-1111-1111-1111-111111111111', DATE_ADD(CURRENT_DATE(), INTERVAL 20 DAY), '10:00:00','18:00:00','Miraflores','PEN',1,'corr-ped-0001','req-ped-0001', @DEMO_USER)
ON DUPLICATE KEY UPDATE fecha_evento=VALUES(fecha_evento);

INSERT IGNORE INTO ev_contratacion.item_pedido_evento (id, pedido_id, opcion_servicio_id, nombre_servicio, cantidad, precio_unitario, subtotal, tipo_item, referencia_id, created_by)
VALUES
('it-ped-0001-1','ped-0001','op-cater-100','Buffet 100 pax',1,6500.00,6500.00,'SERVICIO',NULL,@DEMO_USER),
('it-ped-0001-2','ped-0001',NULL,'Paquete Matrimonio Básico',1,8700.00,8700.00,'PAQUETE','pkg-matr-0001',@DEMO_USER);

-- Update monto_total in pedido
UPDATE ev_contratacion.pedido_evento pe
JOIN (
  SELECT pedido_id, COALESCE(SUM(COALESCE(subtotal,0)),0) as total
  FROM ev_contratacion.item_pedido_evento
  WHERE pedido_id = 'ped-0001'
  GROUP BY pedido_id
) t ON pe.id = t.pedido_id
SET pe.monto_total = t.total
WHERE pe.id = 'ped-0001';

-- Pedido 2: cliente1, servicio local + deco
INSERT IGNORE INTO ev_contratacion.pedido_evento (id, cliente_id, tipo_evento_id, fecha_evento, hora_inicio, hora_fin, ubicacion, moneda, status, correlation_id, request_id, created_by)
VALUES
('ped-0002', 'user-client-01', '33333333-3333-3333-3333-333333333333', DATE_ADD(CURRENT_DATE(), INTERVAL 40 DAY), '09:00:00','17:00:00','San Isidro','PEN',1,'corr-ped-0002','req-ped-0002', 'user-client-01')
ON DUPLICATE KEY UPDATE fecha_evento=VALUES(fecha_evento);

INSERT IGNORE INTO ev_contratacion.item_pedido_evento (id, pedido_id, opcion_servicio_id, nombre_servicio, cantidad, precio_unitario, subtotal, tipo_item, referencia_id, created_by)
VALUES
('it-ped-0002-1','ped-0002','op-local-med','Local mediano',1,4000.00,4000.00,'SERVICIO',NULL,'user-client-01'),
('it-ped-0002-2','ped-0002','op-deco-corp','Decoración estándar',1,1200.00,1200.00,'SERVICIO',NULL,'user-client-01');

UPDATE ev_contratacion.pedido_evento pe
JOIN (
  SELECT pedido_id, COALESCE(SUM(COALESCE(subtotal,0)),0) as total
  FROM ev_contratacion.item_pedido_evento
  WHERE pedido_id = 'ped-0002'
  GROUP BY pedido_id
) t ON pe.id = t.pedido_id
SET pe.monto_total = t.total
WHERE pe.id = 'ped-0002';

/* ============================================================
   8) Holds (reserva_temporal) example + confirmed reserva
   ============================================================ */
-- Hold for DJ (reserve a provider's opcion_servicio)
INSERT IGNORE INTO ev_proveedores.reserva_temporal (id, proveedor_id, opcion_servicio_id, inicio, fin, status, expira_en, correlation_id, created_by)
VALUES
('hold-0001','prov-002','op-dj-4h', DATE_ADD(CURRENT_DATE(), INTERVAL 40 DAY), DATE_ADD(DATE_ADD(CURRENT_DATE(), INTERVAL 40 DAY), INTERVAL 4 HOUR), 0, DATE_ADD(NOW(), INTERVAL 60 MINUTE), 'corr-hold-0001', @DEMO_USER)
ON DUPLICATE KEY UPDATE proveedor_id=VALUES(proveedor_id);

-- Confirmed reserva for one item in ped-0002 (simulate a reservation)
INSERT IGNORE INTO ev_contratacion.reserva (id, item_pedido_id, proveedor_id, inicio, fin, status, hold_id, created_by)
VALUES
('res-0001','it-ped-0002-1','prov-003', DATE_ADD(CURRENT_DATE(), INTERVAL 40 DAY), DATE_ADD(DATE_ADD(CURRENT_DATE(), INTERVAL 40 DAY), INTERVAL 8 HOUR), 1, 'hold-0001', 'user-client-01')
ON DUPLICATE KEY UPDATE proveedor_id=VALUES(proveedor_id);

COMMIT;

-- Verification quick queries you can run after execution
-- SELECT id,codigo,nombre FROM ev_paquetes.paquete WHERE codigo LIKE 'PKG-%';
-- SELECT paquete_id,monto_total_vigente FROM ev_paquetes.v_paquete_precio_vigente_total WHERE paquete_id IN ('pkg-matr-0001','pkg-cum-0001','pkg-corp-0001');
-- SELECT id,opcion_servicio_id,cantidad FROM ev_paquetes.item_paquete WHERE paquete_id LIKE 'pkg-%';

/* ============================================================
    9) Robustez adicional: asegurar datos completos y cobertura >=10
    - Añadir proveedores hasta prov-020 con datos completos
    - Rellenar campos NULL existentes con valores por defecto razonables
    - Asegurar precios para opciones que puedan faltar
    - Agregar paquetes/proveedores/habilidades/calendarios adicionales para pruebas
    - Mantener idempotencia
    ============================================================ */

START TRANSACTION;

-- Añadir proveedores adicionales (prov-011 .. prov-020)
INSERT IGNORE INTO ev_proveedores.proveedor (id, nombre, categoria, ruc, contacto, direccion, email, telefono, rating_prom, status, created_by) VALUES
('prov-011','EventosPlus','SERVICIO','20400123461','Rosa Martínez','Av. Central 10, Lima','hello@eventosplus.pe','+51 900666111',4.2,1,@SYS_ADMIN),
('prov-012','HappyCakes','PASTELERIA','20400123462','Miguel Ángel','Jr. Dulces 5, Lima','contact@happycakes.pe','+51 900666222',4.6,1,@SYS_ADMIN),
('prov-013','StageWorks','SONIDO','20400123463','Pedro Castillo','Av. Escenario 66, Lima','info@stageworks.pe','+51 900666333',4.4,1,@SYS_ADMIN),
('prov-014','LightLab','ILUMINACION','20400123464','Ana Ruiz','Calle Luz 21, Lima','sales@lightlab.pe','+51 900666444',4.3,1,@SYS_ADMIN),
('prov-015','SecureCo','SEGURIDAD','20400123465','Marco Polo','Av. Seguro 99, Lima','ops@secureco.pe','+51 900666555',4.1,1,@SYS_ADMIN),
('prov-016','FlowerArt','DECORACION','20400123466','Elena Gómez','Pasaje Flores 8, Lima','hola@flowerart.pe','+51 900666666',4.5,1,@SYS_ADMIN),
('prov-017','ProPhoto','FOTOGRAFIA','20400123467','Ricardo Flores','Jr. Cámara 77, Lima','contact@prophoto.pe','+51 900666777',4.7,1,@SYS_ADMIN),
('prov-018','KidsFun','ANIMACION','20400123468','Carla Mendez','Av. Niños 44, Lima','kids@kidsfun.pe','+51 900666888',4.0,1,@SYS_ADMIN),
('prov-019','BarMasters','BAR','20400123469','Oscar Vega','Jr. Coctel 3, Lima','bar@barmasters.pe','+51 900666999',4.2,1,@SYS_ADMIN),
('prov-020','CorporateSvc','SERVICIO','20400123470','Patricia Soto','Av. Empresarial 1, Lima','contact@corporatesvc.pe','+51 900667000',4.0,1,@SYS_ADMIN
) ON DUPLICATE KEY UPDATE nombre=VALUES(nombre), email=VALUES(email), telefono=VALUES(telefono), categoria=VALUES(categoria), ruc=VALUES(ruc), contacto=VALUES(contacto), direccion=VALUES(direccion), rating_prom=VALUES(rating_prom), status=VALUES(status);

-- Rellenar campos NULL existentes en `proveedor` con valores por defecto no destructivos
UPDATE ev_proveedores.proveedor
SET
   categoria = COALESCE(categoria, 'OTRO'),
   ruc = COALESCE(ruc, CONCAT('20', LPAD(FLOOR(RAND()*100000000),8,'0'))),
   contacto = COALESCE(contacto, 'Contacto'),
   direccion = COALESCE(direccion, 'Sin direccion registrada'),
   email = COALESCE(email, CONCAT(REPLACE(LOWER(nombre),' ','_'),'@example.local')),
   telefono = COALESCE(telefono, '+51 900000000'),
   rating_prom = COALESCE(rating_prom, 4.0)
WHERE id LIKE 'prov-%';

-- Asegurar que existan precios para cualquier opción creada sin precio (segunda verificación más amplia)
INSERT IGNORE INTO ev_catalogo.precio_servicio (id, opcion_servicio_id, moneda, monto, vigente_desde, vigente_hasta, created_by)
SELECT UUID(), o.id, 'PEN', 1500.00, CURRENT_DATE(), NULL, @SYS_ADMIN
FROM ev_catalogo.opcion_servicio o
LEFT JOIN ev_catalogo.precio_servicio p ON p.opcion_servicio_id = o.id AND (p.vigente_hasta IS NULL OR p.vigente_hasta >= CURRENT_DATE())
WHERE p.id IS NULL;

-- Añadir habilidades para los nuevos proveedores (asociar a servicios relevantes)
INSERT IGNORE INTO ev_proveedores.habilidad_proveedor (id, proveedor_id, servicio_id, nivel) VALUES
(UUID(),'prov-011','svc-catering-1111',4),
(UUID(),'prov-012','svc-cake-2222',5),
(UUID(),'prov-013','svc-sonido-5555',5),
(UUID(),'prov-014','svc-luz-5555',5),
(UUID(),'prov-015','svc-seg-5555',4),
(UUID(),'prov-016','svc-deco-1111',5),
(UUID(),'prov-017','svc-foto-1111',5),
(UUID(),'prov-018','svc-anim-2222',4),
(UUID(),'prov-019','svc-bar-1111',4),
(UUID(),'prov-020','svc-local-3333',4);

-- Calendario para nuevos proveedores: disponibilidad en +45..+54 dias
INSERT IGNORE INTO ev_proveedores.calendario_proveedor (id, proveedor_id, inicio, fin, tipo, created_by) VALUES
(UUID(),'prov-011', DATE_ADD(CURRENT_DATE(), INTERVAL 45 DAY), DATE_ADD(CURRENT_DATE(), INTERVAL 46 DAY), 1, @SYS_ADMIN),
(UUID(),'prov-012', DATE_ADD(CURRENT_DATE(), INTERVAL 46 DAY), DATE_ADD(CURRENT_DATE(), INTERVAL 47 DAY), 1, @SYS_ADMIN),
(UUID(),'prov-013', DATE_ADD(CURRENT_DATE(), INTERVAL 47 DAY), DATE_ADD(CURRENT_DATE(), INTERVAL 48 DAY), 1, @SYS_ADMIN),
(UUID(),'prov-014', DATE_ADD(CURRENT_DATE(), INTERVAL 48 DAY), DATE_ADD(CURRENT_DATE(), INTERVAL 49 DAY), 1, @SYS_ADMIN),
(UUID(),'prov-015', DATE_ADD(CURRENT_DATE(), INTERVAL 49 DAY), DATE_ADD(CURRENT_DATE(), INTERVAL 50 DAY), 1, @SYS_ADMIN),
(UUID(),'prov-016', DATE_ADD(CURRENT_DATE(), INTERVAL 50 DAY), DATE_ADD(CURRENT_DATE(), INTERVAL 51 DAY), 1, @SYS_ADMIN),
(UUID(),'prov-017', DATE_ADD(CURRENT_DATE(), INTERVAL 51 DAY), DATE_ADD(CURRENT_DATE(), INTERVAL 52 DAY), 1, @SYS_ADMIN),
(UUID(),'prov-018', DATE_ADD(CURRENT_DATE(), INTERVAL 52 DAY), DATE_ADD(CURRENT_DATE(), INTERVAL 53 DAY), 1, @SYS_ADMIN),
(UUID(),'prov-019', DATE_ADD(CURRENT_DATE(), INTERVAL 53 DAY), DATE_ADD(CURRENT_DATE(), INTERVAL 54 DAY), 1, @SYS_ADMIN),
(UUID(),'prov-020', DATE_ADD(CURRENT_DATE(), INTERVAL 54 DAY), DATE_ADD(CURRENT_DATE(), INTERVAL 55 DAY), 1, @SYS_ADMIN);

-- Asegurar al menos 10 paquetes (crear paquetes extra si faltan)
INSERT IGNORE INTO ev_paquetes.paquete (id, codigo, nombre, descripcion, status, created_by) VALUES
('pkg-extra-001','PKG-EXTRA-001','Paquete Extra 1','Paquete adicional para pruebas',1,@SYS_ADMIN),
('pkg-extra-002','PKG-EXTRA-002','Paquete Extra 2','Paquete adicional para pruebas',1,@SYS_ADMIN),
('pkg-extra-003','PKG-EXTRA-003','Paquete Extra 3','Paquete adicional para pruebas',1,@SYS_ADMIN),
('pkg-extra-004','PKG-EXTRA-004','Paquete Extra 4','Paquete adicional para pruebas',1,@SYS_ADMIN),
('pkg-extra-005','PKG-EXTRA-005','Paquete Extra 5','Paquete adicional para pruebas',1,@SYS_ADMIN);

-- Insertar items y precios para paquetes extra (usar opciones ya existentes como fallback)
INSERT IGNORE INTO ev_paquetes.item_paquete (id, paquete_id, opcion_servicio_id, cantidad) 
SELECT UUID(), p.id, o.id, 1
FROM ev_paquetes.paquete p
JOIN (SELECT id FROM ev_paquetes.paquete WHERE codigo LIKE 'PKG-EXTRA-%') px ON px.id = p.id
JOIN (SELECT id FROM ev_catalogo.opcion_servicio LIMIT 5) o ON 1=1
WHERE p.codigo LIKE 'PKG-EXTRA-%';

INSERT IGNORE INTO ev_paquetes.precio_paquete (id, paquete_id, moneda, monto, vigente_desde, vigente_hasta, created_by)
SELECT UUID(), p.id, 'PEN', COALESCE(SUM(ps.monto * ip.cantidad), 5000.00), CURRENT_DATE(), NULL, @SYS_ADMIN
FROM ev_paquetes.paquete p
LEFT JOIN ev_paquetes.item_paquete ip ON ip.paquete_id = p.id
LEFT JOIN ev_catalogo.v_opcion_con_precio_vigente ps ON ps.opcion_id = ip.opcion_servicio_id
WHERE p.codigo LIKE 'PKG-EXTRA-%'
GROUP BY p.id;

-- Limpieza: asegurar no hay filas con emails locales inválidos
UPDATE ev_proveedores.proveedor
SET email = CONCAT('prov_', id, '@example.local')
WHERE id IN (
   SELECT id FROM (
      SELECT id FROM ev_proveedores.proveedor WHERE email IS NULL OR email = ''
   ) AS _tmp_prov_email
);

COMMIT;

-- Verificaciones finales: listar filas incompletas para inspección manual
-- SELECT id,nombre,categoria,ruc,contacto,direccion,email,telefono,rating_prom FROM ev_proveedores.proveedor WHERE categoria IS NULL OR email IS NULL OR telefono IS NULL OR direccion IS NULL;
-- SELECT COUNT(*) FROM ev_catalogo.opcion_servicio;
-- SELECT COUNT(*) FROM ev_catalogo.precio_servicio WHERE vigente_hasta IS NULL OR vigente_hasta >= CURRENT_DATE();

