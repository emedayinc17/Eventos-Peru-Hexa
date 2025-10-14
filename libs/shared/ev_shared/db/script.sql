/* ============================================================
   SOA EVENTOS PERÚ — MVP (Hexagonal)  — SQL CONSOLIDADO
   MySQL 8 — InnoDB, utf8mb4  — Estructura + Seeds + Grants
   Ajustes clave:
     - Tokens de reset + rate limit (IAM)
     - Email Outbox (ev_mensajeria) p/ resumen de pedidos y notificaciones
     - Estados de pedido ajustados (DRAFT→COTIZADO→APROBADO→ASIGNADO→CERRADO/CANCELADO)
     - Checks de tiempos (inicio < fin)
     - Vistas de precio vigente total de paquetes
   IDs: CHAR(36) (UUID)
   ============================================================ */

SET NAMES utf8mb4;
SET time_zone = '+00:00';

/* =========================
   0) ESQUEMAS (MVP)
   ========================= */
CREATE SCHEMA IF NOT EXISTS ev_iam            DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE SCHEMA IF NOT EXISTS ev_catalogo       DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE SCHEMA IF NOT EXISTS ev_paquetes       DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE SCHEMA IF NOT EXISTS ev_proveedores    DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE SCHEMA IF NOT EXISTS ev_contratacion   DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE SCHEMA IF NOT EXISTS ev_mensajeria     DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

/* ============================================================
   1) IAM (usuarios, roles, sesiones, auditoría)
   ============================================================ */
CREATE TABLE IF NOT EXISTS ev_iam.usuario (
  id             CHAR(36)     PRIMARY KEY,
  email          VARCHAR(150) NOT NULL,
  password_hash  VARCHAR(255) NOT NULL,
  nombre         VARCHAR(150) NULL,
  telefono       VARCHAR(50)  NULL,
  status         TINYINT      NOT NULL DEFAULT 1,  -- 1=activo,0=inactivo
  last_login     DATETIME     NULL,
  created_at     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at     TIMESTAMP    NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  is_deleted     TINYINT(1)   NOT NULL DEFAULT 0,
  UNIQUE KEY uq_usuario_email (email),
  INDEX idx_usuario_status    (status),
  INDEX idx_usuario_deleted   (is_deleted)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ev_iam.rol (
  id           CHAR(36)     PRIMARY KEY,
  codigo       VARCHAR(50)  NOT NULL,
  nombre       VARCHAR(120) NOT NULL,
  descripcion  VARCHAR(255) NULL,
  status       TINYINT      NOT NULL DEFAULT 1,
  created_at   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   TIMESTAMP    NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_rol_codigo (codigo),
  INDEX idx_rol_status (status)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ev_iam.usuario_rol (
  id          CHAR(36)  PRIMARY KEY,
  usuario_id  CHAR(36)  NOT NULL,  -- referencia lógica a usuario.id
  rol_id      CHAR(36)  NOT NULL,  -- referencia lógica a rol.id
  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_usuario_rol (usuario_id, rol_id),
  INDEX idx_ur_usuario (usuario_id),
  INDEX idx_ur_rol     (rol_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ev_iam.sesion (
  id          CHAR(36)    PRIMARY KEY,
  usuario_id  CHAR(36)    NOT NULL,
  issued_at   DATETIME    NOT NULL,
  expires_at  DATETIME    NOT NULL,
  jwt_id      VARCHAR(64) NOT NULL,   -- jti
  user_agent  VARCHAR(255) NULL,
  ip          VARCHAR(64)  NULL,
  status      TINYINT      NOT NULL DEFAULT 1, -- 1=activa,0=revocada
  created_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_sesion_jti (jwt_id),
  INDEX idx_sesion_usuario (usuario_id),
  INDEX idx_sesion_expira  (expires_at),
  CONSTRAINT chk_sesion_rango CHECK (expires_at > issued_at)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ev_iam.evento_audit (
  id          CHAR(36)    PRIMARY KEY,
  fecha_hora  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actor_id    CHAR(36)    NULL,           -- usuario (lógico)
  entidad     VARCHAR(80) NOT NULL,       -- ej: 'pedido_evento','reserva_temporal','login'
  entidad_id  CHAR(36)    NOT NULL,
  accion      VARCHAR(40) NOT NULL,       -- 'CREAR','ACTUALIZAR','CANCELAR','LOGIN'
  metadata    JSON        NULL,           -- request_id, correlation_id, detalles
  INDEX idx_audit_entidad (entidad, entidad_id),
  INDEX idx_audit_actor   (actor_id, fecha_hora)
) ENGINE=InnoDB;

/* --- NUEVO: Tokens de reset de contraseña --- */
CREATE TABLE IF NOT EXISTS ev_iam.password_reset_token (
  id           CHAR(36)   PRIMARY KEY,
  usuario_id   CHAR(36)   NOT NULL,
  token_hash   VARCHAR(255) NOT NULL,  -- hash del token para no guardar texto plano
  expires_at   DATETIME   NOT NULL,
  used_at      DATETIME   NULL,
  created_at   TIMESTAMP  NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_reset_token (token_hash),
  INDEX idx_reset_user (usuario_id),
  INDEX idx_reset_exp (expires_at),
  CONSTRAINT chk_reset_window CHECK (expires_at > created_at)
) ENGINE=InnoDB;

/* --- NUEVO: Intentos de login (rate-limit básico) --- */
CREATE TABLE IF NOT EXISTS ev_iam.login_intento (
  id          CHAR(36) PRIMARY KEY,
  usuario_id  CHAR(36) NULL,
  email       VARCHAR(150) NULL,
  ip          VARCHAR(64)  NULL,
  exito       TINYINT NOT NULL,  -- 1=login ok,0=fallido
  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_login_user_time (usuario_id, created_at),
  INDEX idx_login_email_time (email, created_at),
  INDEX idx_login_ip_time (ip, created_at)
) ENGINE=InnoDB;

/* ============================================================
   2) CATÁLOGO
   ============================================================ */
CREATE TABLE IF NOT EXISTS ev_catalogo.tipo_evento (
  id           CHAR(36) PRIMARY KEY,
  nombre       VARCHAR(80)  NOT NULL,
  descripcion  VARCHAR(255) NULL,
  status       TINYINT      NOT NULL DEFAULT 1,
  created_at   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   TIMESTAMP    NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  is_deleted   TINYINT(1)   NOT NULL DEFAULT 0
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ev_catalogo.servicio (
  id             CHAR(36) PRIMARY KEY,
  nombre         VARCHAR(120) NOT NULL,
  descripcion    VARCHAR(500) NULL,
  tipo_evento_id CHAR(36) NOT NULL,      -- referencia lógica
  status         TINYINT     NOT NULL DEFAULT 1,
  created_at     TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at     TIMESTAMP   NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  is_deleted     TINYINT(1)  NOT NULL DEFAULT 0,
  created_by     CHAR(36)    NULL,
  updated_by     CHAR(36)    NULL,
  INDEX idx_serv_tipo   (tipo_evento_id),
  INDEX idx_serv_status (status),
  INDEX idx_serv_actor  (created_by, updated_by)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ev_catalogo.opcion_servicio (
  id            CHAR(36) PRIMARY KEY,
  servicio_id   CHAR(36) NOT NULL,
  nombre        VARCHAR(120) NOT NULL,
  detalles      JSON NULL,               -- capacidad, SLA, extras
  status        TINYINT NOT NULL DEFAULT 1,
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  is_deleted    TINYINT(1) NOT NULL DEFAULT 0,
  created_by    CHAR(36)  NULL,
  updated_by    CHAR(36)  NULL,
  INDEX idx_op_servicio (servicio_id),
  INDEX idx_op_status   (status),
  INDEX idx_op_actor    (created_by, updated_by)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ev_catalogo.precio_servicio (
  id                 CHAR(36) PRIMARY KEY,
  opcion_servicio_id CHAR(36) NOT NULL,
  moneda             CHAR(3)  NOT NULL DEFAULT 'PEN',
  monto              DECIMAL(12,2) NOT NULL,
  vigente_desde      DATE NOT NULL,
  vigente_hasta      DATE NULL,
  created_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by         CHAR(36)  NULL,
  INDEX idx_precio_op   (opcion_servicio_id),
  INDEX idx_precio_vig  (vigente_desde, vigente_hasta),
  INDEX idx_precio_actor(created_by)
) ENGINE=InnoDB;

/* CHECK/Índice únicos idempotentes */
SET @exists := (
  SELECT COUNT(*) FROM information_schema.table_constraints
  WHERE constraint_schema='ev_catalogo'
    AND table_name='precio_servicio'
    AND constraint_name='chk_ps_rango'
    AND constraint_type='CHECK'
);
SET @sql := IF(@exists=0,
  'ALTER TABLE ev_catalogo.precio_servicio ADD CONSTRAINT chk_ps_rango CHECK (vigente_hasta IS NULL OR vigente_hasta > vigente_desde)',
  'SELECT 1'); PREPARE s FROM @sql; EXECUTE s; DEALLOCATE PREPARE s;

SET @exists := (
  SELECT COUNT(*) FROM information_schema.statistics
  WHERE table_schema='ev_catalogo'
    AND table_name='precio_servicio'
    AND index_name='uq_precio_op_ini'
);
SET @sql := IF(@exists=0,
  'CREATE UNIQUE INDEX uq_precio_op_ini ON ev_catalogo.precio_servicio (opcion_servicio_id, vigente_desde)',
  'SELECT 1'); PREPARE s FROM @sql; EXECUTE s; DEALLOCATE PREPARE s;

/* ============================================================
   3) PAQUETES
   ============================================================ */
CREATE TABLE IF NOT EXISTS ev_paquetes.paquete (
  id           CHAR(36) PRIMARY KEY,
  codigo       VARCHAR(50)  NOT NULL UNIQUE,
  nombre       VARCHAR(120) NOT NULL,
  descripcion  VARCHAR(500) NULL,
  status       TINYINT      NOT NULL DEFAULT 1,
  created_at   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   TIMESTAMP    NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  is_deleted   TINYINT(1)   NOT NULL DEFAULT 0,
  created_by   CHAR(36)     NULL,
  updated_by   CHAR(36)     NULL,
  INDEX idx_pkg_actor (created_by, updated_by)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ev_paquetes.item_paquete (
  id                 CHAR(36) PRIMARY KEY,
  paquete_id         CHAR(36) NOT NULL,
  opcion_servicio_id CHAR(36) NOT NULL,
  cantidad           INT NOT NULL DEFAULT 1,
  INDEX idx_item_pkg (paquete_id),
  INDEX idx_item_opt (opcion_servicio_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ev_paquetes.precio_paquete (
  id            CHAR(36) PRIMARY KEY,
  paquete_id    CHAR(36) NOT NULL,
  moneda        CHAR(3)  NOT NULL DEFAULT 'PEN',
  monto         DECIMAL(12,2) NOT NULL,
  vigente_desde DATE NOT NULL,
  vigente_hasta DATE NULL,
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by    CHAR(36)  NULL,
  INDEX idx_precio_pkg (paquete_id),
  INDEX idx_precio_vig (vigente_desde, vigente_hasta),
  INDEX idx_precio_pkg_actor (created_by)
) ENGINE=InnoDB;

SET @exists := (
  SELECT COUNT(*) FROM information_schema.table_constraints
  WHERE constraint_schema='ev_paquetes'
    AND table_name='precio_paquete'
    AND constraint_name='chk_pp_rango'
    AND constraint_type='CHECK'
);
SET @sql := IF(@exists=0,
  'ALTER TABLE ev_paquetes.precio_paquete ADD CONSTRAINT chk_pp_rango CHECK (vigente_hasta IS NULL OR vigente_hasta > vigente_desde)',
  'SELECT 1'); PREPARE s FROM @sql; EXECUTE s; DEALLOCATE PREPARE s;

SET @exists := (
  SELECT COUNT(*) FROM information_schema.statistics
  WHERE table_schema='ev_paquetes'
    AND table_name='precio_paquete'
    AND index_name='uq_precio_pkg_ini'
);
SET @sql := IF(@exists=0,
  'CREATE UNIQUE INDEX uq_precio_pkg_ini ON ev_paquetes.precio_paquete (paquete_id, vigente_desde)',
  'SELECT 1'); PREPARE s FROM @sql; EXECUTE s; DEALLOCATE PREPARE s;

/* ============================================================
   4) PROVEEDORES
   ============================================================ */
CREATE TABLE IF NOT EXISTS ev_proveedores.proveedor (
  id           CHAR(36) PRIMARY KEY,
  nombre       VARCHAR(150) NOT NULL,
  email        VARCHAR(150) NULL,
  telefono     VARCHAR(50)  NULL,
  rating_prom  DECIMAL(3,2) NULL DEFAULT 0.0,
  status       TINYINT      NOT NULL DEFAULT 1,
  created_at   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   TIMESTAMP    NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  is_deleted   TINYINT(1)   NOT NULL DEFAULT 0,
  created_by   CHAR(36)     NULL,
  updated_by   CHAR(36)     NULL,
  INDEX idx_prov_status (status),
  INDEX idx_prov_actor  (created_by, updated_by)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ev_proveedores.habilidad_proveedor (
  id           CHAR(36) PRIMARY KEY,
  proveedor_id CHAR(36) NOT NULL,
  servicio_id  CHAR(36) NOT NULL,
  nivel        TINYINT NOT NULL DEFAULT 1, -- 1..5
  UNIQUE KEY uq_prov_serv (proveedor_id, servicio_id),
  INDEX idx_hab_prov (proveedor_id),
  INDEX idx_hab_serv (servicio_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ev_proveedores.calendario_proveedor (
  id               CHAR(36) PRIMARY KEY,
  proveedor_id     CHAR(36) NOT NULL,
  inicio           DATETIME NOT NULL,
  fin              DATETIME NOT NULL,
  tipo             TINYINT  NOT NULL DEFAULT 1, -- 1=turno,2=descanso
  created_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by       CHAR(36)  NULL,
  INDEX idx_cal_time (proveedor_id, inicio, fin),
  INDEX idx_cal_tipo (proveedor_id, tipo, inicio, fin),
  INDEX idx_cal_actor(created_by),
  CONSTRAINT chk_cal_rango CHECK (fin > inicio)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ev_proveedores.reserva_temporal (
  id                 CHAR(36) PRIMARY KEY,
  proveedor_id       CHAR(36) NOT NULL,
  opcion_servicio_id CHAR(36) NOT NULL,
  inicio             DATETIME NOT NULL,
  fin                DATETIME NOT NULL,
  status             TINYINT  NOT NULL DEFAULT 0, -- 0=hold,1=confirmada,2=expirada,3=liberada
  expira_en          DATETIME NOT NULL,
  correlation_id     VARCHAR(64) NULL,
  created_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by         CHAR(36)  NULL,
  INDEX idx_hold_prov_time (proveedor_id, inicio, fin),
  INDEX idx_hold_status    (status),
  INDEX idx_hold_expira    (expira_en),
  INDEX idx_hold_actor     (created_by),
  CONSTRAINT chk_hold_rango CHECK (fin > inicio AND expira_en >= created_at)
) ENGINE=InnoDB;

/* Idempotencia holds */
SET @exists := (
  SELECT COUNT(*) FROM information_schema.statistics
  WHERE table_schema='ev_proveedores'
    AND table_name='reserva_temporal'
    AND index_name='uq_hold_corr'
);
SET @sql := IF(@exists=0,
  'CREATE UNIQUE INDEX uq_hold_corr ON ev_proveedores.reserva_temporal (proveedor_id, correlation_id)',
  'SELECT 1'); PREPARE s FROM @sql; EXECUTE s; DEALLOCATE PREPARE s;

/* ============================================================
   5) CONTRATACIÓN (flujo del pedido)
   ============================================================ */
CREATE TABLE IF NOT EXISTS ev_contratacion.pedido_evento (
  id              CHAR(36) PRIMARY KEY,
  cliente_id      CHAR(36) NOT NULL,        -- ref lógica a ev_iam.usuario.id
  tipo_evento_id  CHAR(36) NOT NULL,        -- ref lógica a catálogo
  fecha_evento    DATE     NOT NULL,
  hora_inicio     TIME     NOT NULL,
  hora_fin        TIME     NULL,
  ubicacion       VARCHAR(255) NOT NULL,
  monto_total     DECIMAL(12,2) NULL DEFAULT 0.00,
  moneda          CHAR(3)  NOT NULL DEFAULT 'PEN',
  status          TINYINT  NOT NULL DEFAULT 0, -- 0=DRAFT,1=COTIZADO,2=APROBADO,3=ASIGNADO,4=CERRADO,5=CANCELADO
  correlation_id  VARCHAR(64) NULL,
  request_id      VARCHAR(64) NULL,
  created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  is_deleted      TINYINT(1) NOT NULL DEFAULT 0,
  created_by      CHAR(36)   NULL,
  updated_by      CHAR(36)   NULL,
  INDEX idx_ped_cliente (cliente_id),
  INDEX idx_ped_fecha   (fecha_evento),
  INDEX idx_ped_status  (status),
  INDEX idx_ped_actor   (created_by, updated_by),
  CONSTRAINT chk_ped_horas CHECK (hora_fin IS NULL OR hora_fin > hora_inicio),
  CONSTRAINT chk_ped_status CHECK (status IN (0,1,2,3,4,5))
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ev_contratacion.item_pedido_evento (
  id            CHAR(36) PRIMARY KEY,
  pedido_id     CHAR(36) NOT NULL,
  tipo_item     TINYINT  NOT NULL,        -- 1=OPCION_SERVICIO, 2=PAQUETE
  referencia_id CHAR(36) NOT NULL,        -- opcion_servicio_id o paquete_id
  cantidad      INT      NOT NULL DEFAULT 1,
  precio_unit   DECIMAL(12,2) NOT NULL,
  precio_total  DECIMAL(12,2) NOT NULL,
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by    CHAR(36)  NULL,
  INDEX idx_item_pedido (pedido_id),
  INDEX idx_item_ref    (referencia_id, tipo_item),
  INDEX idx_item_actor  (created_by)
) ENGINE=InnoDB;

SET @exists := (
  SELECT COUNT(*) FROM information_schema.table_constraints
  WHERE constraint_schema='ev_contratacion'
    AND table_name='item_pedido_evento'
    AND constraint_name='chk_item_importe'
    AND constraint_type='CHECK'
);
SET @sql := IF(@exists=0,
  'ALTER TABLE ev_contratacion.item_pedido_evento ADD CONSTRAINT chk_item_importe CHECK (precio_total = precio_unit * cantidad)',
  'SELECT 1'); PREPARE s FROM @sql; EXECUTE s; DEALLOCATE PREPARE s;

CREATE TABLE IF NOT EXISTS ev_contratacion.reserva (
  id             CHAR(36) PRIMARY KEY,
  item_pedido_id CHAR(36) NOT NULL,
  proveedor_id   CHAR(36) NOT NULL,
  inicio         DATETIME NOT NULL,
  fin            DATETIME NOT NULL,
  status         TINYINT  NOT NULL DEFAULT 0, -- 0=PEND,1=CONFIRMADA,2=FALLIDA,3=CANCELADA
  hold_id        CHAR(36) NULL,               -- ref lógica a reserva_temporal.id
  created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by     CHAR(36)  NULL,
  INDEX idx_reserva_prov_time (proveedor_id, inicio, fin),
  INDEX idx_reserva_item      (item_pedido_id),
  INDEX idx_reserva_status    (status),
  INDEX idx_res_hold          (hold_id),
  INDEX idx_reserva_actor     (created_by),
  CONSTRAINT chk_res_rango CHECK (fin > inicio)
) ENGINE=InnoDB;

/* Idempotencia de pedido */
SET @exists := (
  SELECT COUNT(*) FROM information_schema.statistics
  WHERE table_schema='ev_contratacion'
    AND table_name='pedido_evento'
    AND index_name='uq_ped_request'
);
SET @sql := IF(@exists=0,
  'CREATE UNIQUE INDEX uq_ped_request ON ev_contratacion.pedido_evento (request_id)',
  'SELECT 1'); PREPARE s FROM @sql; EXECUTE s; DEALLOCATE PREPARE s;

/* ============================================================
   6) MENSAJERÍA / OUTBOX (correo)
   ============================================================ */
CREATE TABLE IF NOT EXISTS ev_mensajeria.email_outbox (
  id              CHAR(36)    PRIMARY KEY,
  to_email        VARCHAR(200) NOT NULL,
  subject         VARCHAR(200) NOT NULL,
  body            MEDIUMTEXT   NOT NULL,
  template        VARCHAR(80)  NULL,       -- ej. 'resumen_pedido'
  payload_json    JSON         NULL,       -- datos para render y auditoría
  status          TINYINT      NOT NULL DEFAULT 0,  -- 0=PEND,1=ENVIADO,2=ERROR,3=REINTENTO
  attempts        INT          NOT NULL DEFAULT 0,
  last_attempt_at DATETIME     NULL,
  scheduled_at    DATETIME     NULL,
  sent_at         DATETIME     NULL,
  error_msg       VARCHAR(500) NULL,
  correlation_id  VARCHAR(64)  NULL,
  created_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by      CHAR(36)     NULL,
  INDEX idx_outbox_status_time (status, created_at),
  INDEX idx_outbox_sched       (scheduled_at),
  INDEX idx_outbox_to          (to_email),
  INDEX idx_outbox_corr        (correlation_id)
) ENGINE=InnoDB;

/* ============================================================
   7) ÍNDICES extra para soft-delete/lecturas (idempotentes)
   ============================================================ */
SET @exists := (SELECT COUNT(*) FROM information_schema.statistics
  WHERE table_schema='ev_catalogo' AND table_name='tipo_evento' AND index_name='idx_tipo_evento_activo');
SET @sql := IF(@exists=0,'CREATE INDEX idx_tipo_evento_activo ON ev_catalogo.tipo_evento (is_deleted, status)','SELECT 1');
PREPARE s FROM @sql; EXECUTE s; DEALLOCATE PREPARE s;

SET @exists := (SELECT COUNT(*) FROM information_schema.statistics
  WHERE table_schema='ev_catalogo' AND table_name='servicio' AND index_name='idx_servicio_activo');
SET @sql := IF(@exists=0,'CREATE INDEX idx_servicio_activo ON ev_catalogo.servicio (is_deleted, status)','SELECT 1');
PREPARE s FROM @sql; EXECUTE s; DEALLOCATE PREPARE s;

SET @exists := (SELECT COUNT(*) FROM information_schema.statistics
  WHERE table_schema='ev_catalogo' AND table_name='opcion_servicio' AND index_name='idx_opcion_activa');
SET @sql := IF(@exists=0,'CREATE INDEX idx_opcion_activa ON ev_catalogo.opcion_servicio (is_deleted, status)','SELECT 1');
PREPARE s FROM @sql; EXECUTE s; DEALLOCATE PREPARE s;

/* ============================================================
   8) VISTAS de lectura (read models)
   ============================================================ */
-- Precio vigente por opción
CREATE OR REPLACE VIEW ev_catalogo.v_opcion_con_precio_vigente AS
SELECT
  o.id              AS opcion_id,
  o.servicio_id,
  o.nombre,
  o.detalles,
  p.moneda,
  p.monto
FROM ev_catalogo.opcion_servicio o
JOIN ev_catalogo.precio_servicio p
  ON p.opcion_servicio_id = o.id
WHERE (p.vigente_desde <= CURRENT_DATE())
  AND (p.vigente_hasta IS NULL OR p.vigente_hasta >= CURRENT_DATE())
  AND o.is_deleted = 0
  AND o.status = 1;

-- Paquete con precios vigentes de sus ítems
CREATE OR REPLACE VIEW ev_paquetes.v_paquete_detalle AS
SELECT
  p.id          AS paquete_id,
  p.codigo,
  p.nombre,
  p.descripcion,
  p.status,
  ip.opcion_servicio_id,
  ip.cantidad,
  vc.moneda,
  vc.monto
FROM ev_paquetes.paquete p
JOIN ev_paquetes.item_paquete ip ON ip.paquete_id = p.id
JOIN ev_catalogo.v_opcion_con_precio_vigente vc ON vc.opcion_id = ip.opcion_servicio_id
WHERE p.is_deleted = 0
  AND p.status = 1;

-- NUEVA: total vigente del paquete (suma de ítems * cantidad)
CREATE OR REPLACE VIEW ev_paquetes.v_paquete_precio_vigente_total AS
SELECT
  p.paquete_id,
  MIN(p.codigo)  AS codigo,
  MIN(p.nombre)  AS nombre,
  MIN(p.descripcion) AS descripcion,
  MIN(p.status)  AS status,
  MIN(p.moneda)  AS moneda,
  SUM(p.cantidad * p.monto) AS monto_total_vigente
FROM (
  SELECT d.paquete_id, d.codigo, d.nombre, d.descripcion, d.status, d.opcion_servicio_id,
         d.cantidad, d.moneda, d.monto
  FROM ev_paquetes.v_paquete_detalle d
) p
GROUP BY p.paquete_id;

-- Pedido con datos ligeros del cliente
CREATE OR REPLACE VIEW ev_contratacion.v_pedido_con_cliente AS
SELECT
  pe.id,
  pe.cliente_id,
  u.email       AS cliente_email,
  COALESCE(u.nombre,'') AS cliente_nombre,
  pe.tipo_evento_id,
  pe.fecha_evento, pe.hora_inicio, pe.hora_fin,
  pe.ubicacion, pe.monto_total, pe.moneda,
  pe.status, pe.created_at, pe.updated_at
FROM ev_contratacion.pedido_evento pe
LEFT JOIN ev_iam.usuario u ON u.id = pe.cliente_id;

/* ============================================================
   9) SEEDS mínimos (roles + un usuario demo + catálogo base)
   ============================================================ */
INSERT INTO ev_iam.rol (id, codigo, nombre, descripcion, status) VALUES
 ('aaaa1111-1111-1111-1111-aaaaaaaaaaa1','ADMIN','Administrador','Acceso administrativo (MVP)',1),
 ('aaaa1111-1111-1111-1111-aaaaaaaaaaa2','CLIENTE','Cliente','Usuario final que contrata eventos',1)
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre), descripcion=VALUES(descripcion), status=VALUES(status);

INSERT INTO ev_iam.usuario (id, email, password_hash, nombre, telefono, status) VALUES
 ('aaaa2222-2222-2222-2222-aaaaaaaaaaa2','demo@eventos.pe','$2b$12$fHZoWsqYuYLtGuX5fdUifOp.3r.U5gGvfIUZlt9otvDAuyJ6H3Mui', 'Usuario Demo', '+51 900 000 000', 1)
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre), telefono=VALUES(telefono), status=VALUES(status);

INSERT INTO ev_iam.usuario_rol (id, usuario_id, rol_id) VALUES
 ('aaaa3333-3333-3333-3333-aaaaaaaaaaa3','aaaa2222-2222-2222-2222-aaaaaaaaaaa2','aaaa1111-1111-1111-1111-aaaaaaaaaaa2')
ON DUPLICATE KEY UPDATE usuario_id=VALUES(usuario_id), rol_id=VALUES(rol_id);

-- Catálogo base (tipos/servicios/opciones/precios vigentes)
INSERT INTO ev_catalogo.tipo_evento (id, nombre, descripcion, status) VALUES
 ('11111111-1111-1111-1111-111111111111','Matrimonio','Bodas y recepciones',1),
 ('22222222-2222-2222-2222-222222222222','Cumpleaños','Fiestas de cumpleaños',1),
 ('33333333-3333-3333-3333-333333333333','Corporativo','Eventos empresariales',1)
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre), descripcion=VALUES(descripcion), status=VALUES(status);

INSERT INTO ev_catalogo.servicio (id, nombre, descripcion, tipo_evento_id, status) VALUES
 ('44444444-4444-4444-4444-444444444444','Catering','Alimentos y bebidas','11111111-1111-1111-1111-111111111111',1),
 ('55555555-5555-5555-5555-555555555555','Música','DJ o banda','22222222-2222-2222-2222-222222222222',1),
 ('66666666-6666-6666-6666-666666666666','Local','Alquiler de local','33333333-3333-3333-3333-333333333333',1)
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre), descripcion=VALUES(descripcion), status=VALUES(status);

INSERT INTO ev_catalogo.opcion_servicio (id, servicio_id, nombre, detalles, status) VALUES
 ('77777777-7777-7777-7777-777777777777','44444444-4444-4444-4444-444444444444','Buffet 100 pax', JSON_OBJECT('capacidad',100,'menu','estandar'),1),
 ('88888888-8888-8888-8888-888888888888','55555555-5555-5555-5555-555555555555','DJ Pro 4h', JSON_OBJECT('duracion_h',4,'equipo','incluye'),1),
 ('99999999-9999-9999-9999-999999999999','66666666-6666-6666-6666-666666666666','Local mediano', JSON_OBJECT('capacidad',150,'ubicacion','Lima'),1)
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre), detalles=VALUES(detalles), status=VALUES(status);

INSERT INTO ev_catalogo.precio_servicio (id, opcion_servicio_id, moneda, monto, vigente_desde, vigente_hasta, created_by) VALUES
 ('aaaaaaa0-aaaa-aaaa-aaaa-aaaaaaaaaaa0','77777777-7777-7777-7777-777777777777','PEN',6500.00, CURRENT_DATE(), NULL, 'aaaa2222-2222-2222-2222-aaaaaaaaaaa2'),
 ('aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaa1','88888888-8888-8888-8888-888888888888','PEN',1800.00, CURRENT_DATE(), NULL, 'aaaa2222-2222-2222-2222-aaaaaaaaaaa2'),
 ('aaaaaaa2-aaaa-aaaa-aaaa-aaaaaaaaaaa2','99999999-9999-9999-9999-999999999999','PEN',4000.00, CURRENT_DATE(), NULL, 'aaaa2222-2222-2222-2222-aaaaaaaaaaa2')
ON DUPLICATE KEY UPDATE monto=VALUES(monto), vigente_hasta=VALUES(vigente_hasta);

-- Paquete “Premium 100 pax”
INSERT INTO ev_paquetes.paquete (id, codigo, nombre, descripcion, status, created_by) VALUES
 ('bbbbbbb0-bbbb-bbbb-bbbb-bbbbbbbbbbb0','PKG-PREMIUM-100','Premium 100 pax','Catering 100p + DJ 4h + Local mediano',1,'aaaa2222-2222-2222-2222-aaaaaaaaaaa2')
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre), descripcion=VALUES(descripcion), status=VALUES(status);

INSERT INTO ev_paquetes.item_paquete (id, paquete_id, opcion_servicio_id, cantidad) VALUES
 ('bbbbbbb1-bbbb-bbbb-bbbb-bbbbbbbbbbb1','bbbbbbb0-bbbb-bbbb-bbbb-bbbbbbbbbbb0','77777777-7777-7777-7777-777777777777',1),
 ('bbbbbbb2-bbbb-bbbb-bbbb-bbbbbbbbbbb2','bbbbbbb0-bbbb-bbbb-bbbb-bbbbbbbbbbb0','88888888-8888-8888-8888-888888888888',1),
 ('bbbbbbb3-bbbb-bbbb-bbbb-bbbbbbbbbbb3','bbbbbbb0-bbbb-bbbb-bbbb-bbbbbbbbbbb0','99999999-9999-9999-9999-999999999999',1)
ON DUPLICATE KEY UPDATE cantidad=VALUES(cantidad);

INSERT INTO ev_paquetes.precio_paquete (id, paquete_id, moneda, monto, vigente_desde, vigente_hasta, created_by) VALUES
 ('bbbbbbb4-bbbb-bbbb-bbbb-bbbbbbbbbbb4','bbbbbbb0-bbbb-bbbb-bbbb-bbbbbbbbbbb0','PEN',12300.00, CURRENT_DATE(), NULL,'aaaa2222-2222-2222-2222-aaaaaaaaaaa2')
ON DUPLICATE KEY UPDATE monto=VALUES(monto), vigente_hasta=VALUES(vigente_hasta);

-- Proveedores base
INSERT INTO ev_proveedores.proveedor (id, nombre, email, telefono, rating_prom, status, created_by) VALUES
 ('ccccccc0-cccc-cccc-cccc-ccccccccccc0','Sazón & Sabor','contacto@sazonsabor.pe','+51 900 111 222',4.7,1,'aaaa2222-2222-2222-2222-aaaaaaaaaaa2'),
 ('ccccccc1-cccc-cccc-cccc-ccccccccccc1','DJ Lima Beats','dj@limabeats.pe','+51 900 333 444',4.6,1,'aaaa2222-2222-2222-2222-aaaaaaaaaaa2'),
 ('ccccccc2-cccc-cccc-cccc-ccccccccccc2','Centro de Eventos Miraflores','reservas@cem.pe','+51 900 555 666',4.5,1,'aaaa2222-2222-2222-2222-aaaaaaaaaaa2')
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre), email=VALUES(email), telefono=VALUES(telefono), rating_prom=VALUES(rating_prom), status=VALUES(status);

INSERT INTO ev_proveedores.habilidad_proveedor (id, proveedor_id, servicio_id, nivel) VALUES
 ('ddddddd0-dddd-dddd-dddd-ddddddddddd0','ccccccc0-cccc-cccc-cccc-ccccccccccc0','44444444-4444-4444-4444-444444444444',5),
 ('ddddddd1-dddd-dddd-dddd-ddddddddddd1','ccccccc1-cccc-cccc-cccc-ccccccccccc1','55555555-5555-5555-5555-555555555555',5),
 ('ddddddd2-dddd-dddd-dddd-ddddddddddd2','ccccccc2-cccc-cccc-cccc-ccccccccccc2','66666666-6666-6666-6666-666666666666',4)
ON DUPLICATE KEY UPDATE nivel=VALUES(nivel);

/* ============================================================
   10) EVENTOS programados (holds expirados)
   ============================================================ */
DROP EVENT IF EXISTS ev_proveedores.evt_expira_holds;
CREATE EVENT ev_proveedores.evt_expira_holds
  ON SCHEDULE EVERY 10 MINUTE
  DO
    UPDATE ev_proveedores.reserva_temporal
       SET status = 2   -- expirada
     WHERE status = 0   -- hold activa
       AND expira_en <= NOW();

/* ============================================================
   11) USUARIOS DB / PERMISOS (por bounded context)
   ============================================================ */
CREATE USER IF NOT EXISTS 'app_iam'@'%'            IDENTIFIED BY 'IAM_2025';
CREATE USER IF NOT EXISTS 'app_catalogo'@'%'       IDENTIFIED BY 'Catalogo_2025';
CREATE USER IF NOT EXISTS 'app_paquetes'@'%'       IDENTIFIED BY 'Pkg_2025';
CREATE USER IF NOT EXISTS 'app_proveedores'@'%'    IDENTIFIED BY 'Proveedores_2025';
CREATE USER IF NOT EXISTS 'app_contratacion'@'%'   IDENTIFIED BY 'Contrata_2025';
CREATE USER IF NOT EXISTS 'app_mensajeria'@'%'     IDENTIFIED BY 'Mensajeria_2025';
CREATE USER IF NOT EXISTS 'app_api'@'%'            IDENTIFIED BY 'Api_2025!';

-- IAM
GRANT SELECT,INSERT,UPDATE,DELETE,CREATE,ALTER,INDEX ON ev_iam.*             TO 'app_iam'@'%';

-- Catálogo (lectura) + Paquetes (lectura para exposición pública)
GRANT SELECT ON ev_catalogo.*     TO 'app_catalogo'@'%';
GRANT SELECT ON ev_paquetes.*     TO 'app_catalogo'@'%';

-- Paquetes (si administras desde backoffice)
GRANT SELECT,INSERT,UPDATE,DELETE,CREATE,ALTER,INDEX ON ev_paquetes.*        TO 'app_paquetes'@'%';

-- Proveedores
GRANT SELECT,INSERT,UPDATE,DELETE,CREATE,ALTER,INDEX ON ev_proveedores.*     TO 'app_proveedores'@'%';

-- Contratación
GRANT SELECT,INSERT,UPDATE,DELETE,CREATE,ALTER,INDEX ON ev_contratacion.*    TO 'app_contratacion'@'%';

-- Mensajería/Outbox
GRANT SELECT,INSERT,UPDATE,DELETE,CREATE,ALTER,INDEX ON ev_mensajeria.*      TO 'app_mensajeria'@'%';

-- Contratacion en Mensajeria (para este MVP)
GRANT SELECT,INSERT,UPDATE,DELETE,CREATE,ALTER,INDEX ON ev_mensajeria.* 	  TO 'app_contratacion'@'%';


-- API compuesta (si una capa orquesta varios dominios)
GRANT SELECT ON ev_catalogo.*   TO 'app_api'@'%';
GRANT SELECT ON ev_paquetes.*   TO 'app_api'@'%';
GRANT SELECT,INSERT,UPDATE,DELETE,CREATE,ALTER,INDEX ON ev_iam.*           TO 'app_api'@'%';
GRANT SELECT,INSERT,UPDATE,DELETE,CREATE,ALTER,INDEX ON ev_proveedores.*   TO 'app_api'@'%';
GRANT SELECT,INSERT,UPDATE,DELETE,CREATE,ALTER,INDEX ON ev_contratacion.*  TO 'app_api'@'%';
GRANT SELECT,INSERT,UPDATE,DELETE,CREATE,ALTER,INDEX ON ev_mensajeria.*    TO 'app_api'@'%';

FLUSH PRIVILEGES;

/* ============================================================
   12) CONSULTAS de verificación (opcionales)
   ============================================================ */
-- SHOW GRANTS FOR 'app_api'@'%';
-- SELECT * FROM ev_paquetes.v_paquete_precio_vigente_total;
-- SELECT COUNT(*) FROM ev_mensajeria.email_outbox WHERE status=0;
