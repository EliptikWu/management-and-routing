-- ============================================
-- SCHEMA: Enrutador de Órdenes Multiárea
-- DB: MySQL 8.0+
-- Versión: 001
-- Descripción: Esquema inicial con áreas, órdenes, asignaciones e historial
-- ============================================

-- Crear base de datos si no existe
CREATE DATABASE IF NOT EXISTS ordenes_multiarea
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE ordenes_multiarea;

-- ============================================
-- TABLA: areas
-- Propósito: Catálogo de áreas/departamentos que gestionan órdenes
-- ============================================
CREATE TABLE IF NOT EXISTS areas (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    responsable VARCHAR(150) NOT NULL,
    contacto VARCHAR(100) NULL COMMENT 'Email, teléfono o extensión',
    activo BOOLEAN DEFAULT TRUE,
    creada_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_areas_nombre (nombre),
    INDEX idx_areas_activo (activo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Áreas o departamentos que procesan órdenes de trabajo';

-- ============================================
-- TABLA: ordenes
-- Propósito: Registro de órdenes de trabajo
-- ============================================
CREATE TABLE IF NOT EXISTS ordenes (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    descripcion TEXT NOT NULL,
    creador VARCHAR(150) NOT NULL COMMENT 'Usuario que creó la orden',
    
    -- Estado global de la orden (calculado desde orden_area)
    estado_global ENUM(
        'NUEVA',
        'ASIGNADA',
        'EN_PROGRESO',
        'PENDIENTE',
        'COMPLETADA',
        'CERRADA_SIN_SOLUCION',
        'VENCIDA'
    ) DEFAULT 'NUEVA' NOT NULL,
    
    prioridad ENUM('BAJA', 'MEDIA', 'ALTA', 'CRITICA') DEFAULT 'MEDIA' NOT NULL,
    
    creada_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizada_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_ordenes_estado (estado_global),
    INDEX idx_ordenes_creador (creador),
    INDEX idx_ordenes_prioridad (prioridad),
    INDEX idx_ordenes_creada_en (creada_en),
    INDEX idx_ordenes_actualizada_en (actualizada_en)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Órdenes de trabajo con estado global';

-- ============================================
-- TABLA: orden_area
-- Propósito: Asignación de órdenes a áreas (relación N:M)
-- ============================================
CREATE TABLE IF NOT EXISTS orden_area (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    orden_id INT UNSIGNED NOT NULL,
    area_id INT UNSIGNED NOT NULL,
    
    asignada_a VARCHAR(150) NULL COMMENT 'Persona específica dentro del área',
    
    -- Estado parcial de esta área en esta orden
    estado_parcial ENUM(
        'NUEVA',
        'ASIGNADA',
        'EN_PROGRESO',
        'PENDIENTE',
        'COMPLETADA',
        'CERRADA_SIN_SOLUCION',
        'VENCIDA'
    ) DEFAULT 'ASIGNADA' NOT NULL,
    
    seg_acumulados INT UNSIGNED DEFAULT 0 COMMENT 'Segundos acumulados en esta asignación',
    
    -- Timestamps de ciclo de vida
    asignada_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    iniciada_en TIMESTAMP NULL,
    pausada_en TIMESTAMP NULL,
    completada_en TIMESTAMP NULL,
    
    notas TEXT NULL COMMENT 'Observaciones o comentarios del área',
    
    FOREIGN KEY (orden_id) REFERENCES ordenes(id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    FOREIGN KEY (area_id) REFERENCES areas(id) 
        ON DELETE RESTRICT 
        ON UPDATE CASCADE,
    
    UNIQUE KEY uk_orden_area (orden_id, area_id),
    INDEX idx_orden_area_estado (estado_parcial),
    INDEX idx_orden_area_asignada (asignada_a),
    INDEX idx_orden_area_seg (seg_acumulados)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Asignaciones de órdenes a áreas con estado individual';

-- ============================================
-- TABLA: historial
-- Propósito: Trazabilidad completa de eventos por orden
-- ============================================
CREATE TABLE IF NOT EXISTS historial (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    orden_id INT UNSIGNED NOT NULL,
    
    evento VARCHAR(100) NOT NULL COMMENT 'Tipo de evento: CREADA, ASIGNADA, CAMBIO_ESTADO, TIMEOUT, etc.',
    detalle TEXT NULL COMMENT 'Descripción detallada del evento',
    
    estado_global ENUM(
        'NUEVA',
        'ASIGNADA',
        'EN_PROGRESO',
        'PENDIENTE',
        'COMPLETADA',
        'CERRADA_SIN_SOLUCION',
        'VENCIDA'
    ) NULL COMMENT 'Estado global después del evento',
    
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actor VARCHAR(150) NULL COMMENT 'Usuario o sistema que generó el evento',
    
    FOREIGN KEY (orden_id) REFERENCES ordenes(id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    
    INDEX idx_historial_orden (orden_id, timestamp),
    INDEX idx_historial_evento (evento),
    INDEX idx_historial_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Registro cronológico de eventos por orden';

-- ============================================
-- VISTAS ÚTILES
-- ============================================

-- Vista: Resumen de órdenes con conteo de áreas
CREATE OR REPLACE VIEW v_ordenes_resumen AS
SELECT 
    o.id,
    o.titulo,
    o.estado_global,
    o.prioridad,
    o.creador,
    o.creada_en,
    o.actualizada_en,
    COUNT(oa.id) as total_areas,
    SUM(CASE WHEN oa.estado_parcial = 'COMPLETADA' THEN 1 ELSE 0 END) as areas_completadas,
    SUM(oa.seg_acumulados) as total_segundos
FROM ordenes o
LEFT JOIN orden_area oa ON o.id = oa.orden_id
GROUP BY o.id;

-- Vista: Órdenes con SLA vencido (más de 60 segundos en progreso)
CREATE OR REPLACE VIEW v_ordenes_vencidas AS
SELECT 
    o.id,
    o.titulo,
    oa.area_id,
    a.nombre as area_nombre,
    oa.estado_parcial,
    oa.seg_acumulados
FROM ordenes o
JOIN orden_area oa ON o.id = oa.orden_id
JOIN areas a ON oa.area_id = a.id
WHERE oa.estado_parcial IN ('EN_PROGRESO', 'PENDIENTE')
  AND oa.seg_acumulados >= 60;

-- ============================================
-- TRIGGERS
-- ============================================

-- Trigger: Registrar en historial cuando se crea una orden
DELIMITER $$

CREATE TRIGGER tr_orden_creada
AFTER INSERT ON ordenes
FOR EACH ROW
BEGIN
    INSERT INTO historial (orden_id, evento, detalle, estado_global, actor)
    VALUES (
        NEW.id,
        'CREADA',
        CONCAT('Orden creada: ', NEW.titulo),
        NEW.estado_global,
        NEW.creador
    );
END$$

-- Trigger: Registrar en historial cuando cambia el estado global
CREATE TRIGGER tr_orden_cambio_estado
AFTER UPDATE ON ordenes
FOR EACH ROW
BEGIN
    IF OLD.estado_global != NEW.estado_global THEN
        INSERT INTO historial (orden_id, evento, detalle, estado_global, actor)
        VALUES (
            NEW.id,
            'CAMBIO_ESTADO_GLOBAL',
            CONCAT('Estado cambió de ', OLD.estado_global, ' a ', NEW.estado_global),
            NEW.estado_global,
            'SISTEMA'
        );
    END IF;
END$$

-- Trigger: Registrar asignación de área
CREATE TRIGGER tr_area_asignada
AFTER INSERT ON orden_area
FOR EACH ROW
BEGIN
    DECLARE v_area_nombre VARCHAR(100);
    
    SELECT nombre INTO v_area_nombre FROM areas WHERE id = NEW.area_id;
    
    INSERT INTO historial (orden_id, evento, detalle, actor)
    VALUES (
        NEW.orden_id,
        'AREA_ASIGNADA',
        CONCAT('Área asignada: ', v_area_nombre, 
               CASE WHEN NEW.asignada_a IS NOT NULL 
                    THEN CONCAT(' → ', NEW.asignada_a) 
                    ELSE '' 
               END),
        'SISTEMA'
    );
END$$

-- Trigger: Registrar cambios de estado parcial
CREATE TRIGGER tr_orden_area_cambio_estado
AFTER UPDATE ON orden_area
FOR EACH ROW
BEGIN
    DECLARE v_area_nombre VARCHAR(100);
    
    IF OLD.estado_parcial != NEW.estado_parcial THEN
        SELECT nombre INTO v_area_nombre FROM areas WHERE id = NEW.area_id;
        
        INSERT INTO historial (orden_id, evento, detalle, actor)
        VALUES (
            NEW.orden_id,
            'CAMBIO_ESTADO_PARCIAL',
            CONCAT('Área ', v_area_nombre, ': ', OLD.estado_parcial, ' → ', NEW.estado_parcial),
            COALESCE(NEW.asignada_a, 'SISTEMA')
        );
    END IF;
END$$

DELIMITER ;

-- ============================================
-- VERIFICACIÓN
-- ============================================
SELECT 'Schema creado exitosamente' as status;
SHOW TABLES;