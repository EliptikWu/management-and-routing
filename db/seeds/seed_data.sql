-- ============================================
-- SEED DATA: Enrutador de Órdenes Multiárea
-- Propósito: Datos de prueba para desarrollo y testing
-- ============================================

USE ordenes_multiarea;

-- Limpiar datos existentes (en orden por foreign keys)
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE historial;
TRUNCATE TABLE orden_area;
TRUNCATE TABLE ordenes;
TRUNCATE TABLE areas;
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================
-- ÁREAS (3 áreas operativas)
-- ============================================
INSERT INTO areas (id, nombre, responsable, contacto, activo) VALUES
(1, 'Soporte Técnico', 'Carlos Mendoza', 'cmendoza@empresa.com', TRUE),
(2, 'Infraestructura IT', 'Ana Rodríguez', 'arodriguez@empresa.com', TRUE),
(3, 'Desarrollo', 'Luis Martínez', 'lmartinez@empresa.com', TRUE),
(4, 'Seguridad Informática', 'María García', 'mgarcia@empresa.com', TRUE),
(5, 'Operaciones', 'Jorge Silva', 'jsilva@empresa.com', TRUE);

-- ============================================
-- ÓRDENES (8 órdenes: 2 simples, 6 complejas con multiárea)
-- ============================================

-- Orden 1: Simple - Solo Soporte Técnico
INSERT INTO ordenes (id, titulo, descripcion, creador, estado_global, prioridad, creada_en) VALUES
(1, 
 'Reseteo de contraseña para usuario nuevo',
 'El usuario Juan Pérez necesita reseteo de contraseña de su cuenta corporativa. ID: JPEREZ. Requiere acceso urgente para inicio de labores.',
 'admin@empresa.com',
 'ASIGNADA',
 'MEDIA',
 DATE_SUB(NOW(), INTERVAL 2 HOUR));

-- Orden 2: Simple - Solo Desarrollo
INSERT INTO ordenes (id, titulo, descripcion, creador, estado_global, prioridad, creada_en) VALUES
(2,
 'Bug en módulo de reportes',
 'Los reportes mensuales no generan el gráfico de barras correctamente. Se muestra error "Chart.js undefined" en consola del navegador.',
 'jlopez@empresa.com',
 'EN_PROGRESO',
 'ALTA',
 DATE_SUB(NOW(), INTERVAL 5 HOUR));

-- Orden 3: Multiárea - Soporte + Infraestructura (Completa)
INSERT INTO ordenes (id, titulo, descripcion, creador, estado_global, prioridad, creada_en) VALUES
(3,
 'Configuración de estación de trabajo para gerente',
 'Nuevo gerente de ventas requiere: 1) Instalación de software (Office, CRM, VPN), 2) Permisos de red y carpetas compartidas, 3) Configuración de impresora departamental.',
 'rrhh@empresa.com',
 'COMPLETADA',
 'MEDIA',
 DATE_SUB(NOW(), INTERVAL 1 DAY));

-- Orden 4: Multiárea - IT + Seguridad + Desarrollo (En progreso mixto)
INSERT INTO ordenes (id, titulo, descripcion, creador, estado_global, prioridad, creada_en) VALUES
(4,
 'Migración de servidor de base de datos',
 'Migrar base de datos productiva de MySQL 5.7 a MySQL 8.0. Incluye: backup completo, pruebas de compatibilidad, actualización de aplicaciones dependientes y auditoría de seguridad post-migración.',
 'cto@empresa.com',
 'EN_PROGRESO',
 'CRITICA',
 DATE_SUB(NOW(), INTERVAL 6 HOUR));

-- Orden 5: Multiárea - Todas las áreas (Compleja, pendiente)
INSERT INTO ordenes (id, titulo, descripcion, creador, estado_global, prioridad, creada_en) VALUES
(5,
 'Implementación de nuevo sistema ERP',
 'Despliegue del nuevo sistema ERP: infraestructura en cloud, desarrollo de integraciones, capacitación de usuarios, configuración de permisos y monitoreo de seguridad.',
 'direccion@empresa.com',
 'PENDIENTE',
 'CRITICA',
 DATE_SUB(NOW(), INTERVAL 3 DAY));

-- Orden 6: Multiárea - Soporte + Seguridad (Nueva)
INSERT INTO ordenes (id, titulo, descripcion, creador, estado_global, prioridad, creada_en) VALUES
(6,
 'Investigación de acceso no autorizado',
 'Se detectaron intentos de login fallidos desde IP sospechosa. Requiere análisis de logs, bloqueo de IP y revisión de cuentas comprometidas.',
 'seguridad@empresa.com',
 'ASIGNADA',
 'ALTA',
 DATE_SUB(NOW(), INTERVAL 30 MINUTE));

-- Orden 7: Multiárea - IT + Desarrollo (Vencida)
INSERT INTO ordenes (id, titulo, descripcion, creador, estado_global, prioridad, creada_en) VALUES
(7,
 'Optimización de rendimiento del portal web',
 'El portal corporativo presenta lentitud en horas pico. Requiere análisis de infraestructura (balanceo, cache) y optimización de código (queries N+1, assets pesados).',
 'webmaster@empresa.com',
 'VENCIDA',
 'ALTA',
 DATE_SUB(NOW(), INTERVAL 4 HOUR));

-- Orden 8: Simple - Solo Operaciones (Cerrada sin solución)
INSERT INTO ordenes (id, titulo, descripcion, creador, estado_global, prioridad, creada_en) VALUES
(8,
 'Solicitud de licencia software descontinuado',
 'Usuario solicita instalación de Adobe Flash Player para aplicación legacy. El software ya no tiene soporte del fabricante.',
 'usuario@empresa.com',
 'CERRADA_SIN_SOLUCION',
 'BAJA',
 DATE_SUB(NOW(), INTERVAL 2 DAY));

-- ============================================
-- ASIGNACIONES (orden_area)
-- ============================================

-- Orden 1: Solo Soporte
INSERT INTO orden_area (orden_id, area_id, asignada_a, estado_parcial, seg_acumulados, asignada_en, iniciada_en) VALUES
(1, 1, 'Pedro Sánchez', 'EN_PROGRESO', 15, DATE_SUB(NOW(), INTERVAL 1 HOUR), DATE_SUB(NOW(), INTERVAL 45 MINUTE));

-- Orden 2: Solo Desarrollo
INSERT INTO orden_area (orden_id, area_id, asignada_a, estado_parcial, seg_acumulados, asignada_en, iniciada_en) VALUES
(2, 3, 'Laura Díaz', 'EN_PROGRESO', 120, DATE_SUB(NOW(), INTERVAL 4 HOUR), DATE_SUB(NOW(), INTERVAL 4 HOUR));

-- Orden 3: Multiárea COMPLETADA
INSERT INTO orden_area (orden_id, area_id, asignada_a, estado_parcial, seg_acumulados, asignada_en, iniciada_en, completada_en) VALUES
(3, 1, 'Carlos Mendoza', 'COMPLETADA', 450, DATE_SUB(NOW(), INTERVAL 1 DAY), DATE_SUB(NOW(), INTERVAL 23 HOUR), DATE_SUB(NOW(), INTERVAL 20 HOUR)),
(3, 2, 'Roberto Vega', 'COMPLETADA', 380, DATE_SUB(NOW(), INTERVAL 1 DAY), DATE_SUB(NOW(), INTERVAL 22 HOUR), DATE_SUB(NOW(), INTERVAL 20 HOUR));

-- Orden 4: Multiárea EN_PROGRESO mixto
INSERT INTO orden_area (orden_id, area_id, asignada_a, estado_parcial, seg_acumulados, asignada_en, iniciada_en) VALUES
(4, 2, 'Ana Rodríguez', 'COMPLETADA', 250, DATE_SUB(NOW(), INTERVAL 5 HOUR), DATE_SUB(NOW(), INTERVAL 5 HOUR)),
(4, 4, 'María García', 'EN_PROGRESO', 85, DATE_SUB(NOW(), INTERVAL 4 HOUR), DATE_SUB(NOW(), INTERVAL 3 HOUR)),
(4, 3, NULL, 'PENDIENTE', 0, DATE_SUB(NOW(), INTERVAL 4 HOUR), NULL);

-- Orden 5: Multiárea PENDIENTE (no iniciadas)
INSERT INTO orden_area (orden_id, area_id, asignada_a, estado_parcial, seg_acumulados, asignada_en) VALUES
(5, 1, NULL, 'ASIGNADA', 0, DATE_SUB(NOW(), INTERVAL 3 DAY)),
(5, 2, NULL, 'ASIGNADA', 0, DATE_SUB(NOW(), INTERVAL 3 DAY)),
(5, 3, NULL, 'ASIGNADA', 0, DATE_SUB(NOW(), INTERVAL 3 DAY)),
(5, 4, NULL, 'ASIGNADA', 0, DATE_SUB(NOW(), INTERVAL 3 DAY));

-- Orden 6: Multiárea NUEVA/ASIGNADA
INSERT INTO orden_area (orden_id, area_id, asignada_a, estado_parcial, seg_acumulados, asignada_en) VALUES
(6, 1, 'Pedro Sánchez', 'ASIGNADA', 0, DATE_SUB(NOW(), INTERVAL 25 MINUTE)),
(6, 4, 'Elena Torres', 'ASIGNADA', 0, DATE_SUB(NOW(), INTERVAL 25 MINUTE));

-- Orden 7: Multiárea VENCIDA
INSERT INTO orden_area (orden_id, area_id, asignada_a, estado_parcial, seg_acumulados, asignada_en, iniciada_en) VALUES
(7, 2, 'Roberto Vega', 'VENCIDA', 180, DATE_SUB(NOW(), INTERVAL 3 HOUR), DATE_SUB(NOW(), INTERVAL 3 HOUR)),
(7, 3, 'Luis Martínez', 'EN_PROGRESO', 95, DATE_SUB(NOW(), INTERVAL 2 HOUR), DATE_SUB(NOW(), INTERVAL 2 HOUR));

-- Orden 8: Solo Operaciones CERRADA_SIN_SOLUCION
INSERT INTO orden_area (orden_id, area_id, asignada_a, estado_parcial, seg_acumulados, asignada_en, completada_en) VALUES
(8, 5, 'Jorge Silva', 'CERRADA_SIN_SOLUCION', 60, DATE_SUB(NOW(), INTERVAL 2 DAY), DATE_SUB(NOW(), INTERVAL 2 DAY));

-- ============================================
-- HISTORIAL (eventos iniciales - triggers crearán más)
-- ============================================

-- Los triggers ya generaron eventos de CREADA y AREA_ASIGNADA
-- Aquí agregamos eventos adicionales relevantes

INSERT INTO historial (orden_id, evento, detalle, estado_global, timestamp, actor) VALUES
-- Orden 3: Completada
(3, 'COMPLETADA', 'Todas las áreas completaron sus tareas', 'COMPLETADA', DATE_SUB(NOW(), INTERVAL 20 HOUR), 'SISTEMA'),

-- Orden 4: Progreso
(4, 'INICIO_TRABAJO', 'Infraestructura IT inició backup de base de datos', 'EN_PROGRESO', DATE_SUB(NOW(), INTERVAL 5 HOUR), 'Ana Rodríguez'),
(4, 'INICIO_TRABAJO', 'Seguridad inició auditoría de permisos', 'EN_PROGRESO', DATE_SUB(NOW(), INTERVAL 3 HOUR), 'María García'),

-- Orden 7: Timeout
(7, 'TIMEOUT_SLA', 'Área Infraestructura superó el SLA de 60 segundos', 'VENCIDA', DATE_SUB(NOW(), INTERVAL 1 HOUR), 'SISTEMA'),

-- Orden 8: Cerrada sin solución
(8, 'CERRADA_SIN_SOLUCION', 'Software descontinuado, no es posible instalar. Se sugirió alternativa HTML5.', 'CERRADA_SIN_SOLUCION', DATE_SUB(NOW(), INTERVAL 2 DAY), 'Jorge Silva');

-- ============================================
-- VERIFICACIÓN DE DATOS
-- ============================================

SELECT '=== VERIFICACIÓN DE SEED DATA ===' as '';

SELECT 'Áreas creadas:' as tipo, COUNT(*) as cantidad FROM areas;
SELECT 'Órdenes creadas:' as tipo, COUNT(*) as cantidad FROM ordenes;
SELECT 'Asignaciones creadas:' as tipo, COUNT(*) as cantidad FROM orden_area;
SELECT 'Eventos de historial:' as tipo, COUNT(*) as cantidad FROM historial;

SELECT '=== RESUMEN DE ÓRDENES ===' as '';
SELECT 
    id,
    titulo,
    estado_global,
    prioridad,
    (SELECT COUNT(*) FROM orden_area WHERE orden_id = o.id) as areas_asignadas
FROM ordenes o
ORDER BY id;

SELECT '=== ÓRDENES MULTIÁREA (2+) ===' as '';
SELECT 
    o.id,
    o.titulo,
    COUNT(oa.id) as num_areas,
    GROUP_CONCAT(a.nombre SEPARATOR ', ') as areas
FROM ordenes o
JOIN orden_area oa ON o.id = oa.orden_id
JOIN areas a ON oa.area_id = a.id
GROUP BY o.id
HAVING num_areas >= 2
ORDER BY num_areas DESC;

SELECT 'Seed data cargado exitosamente' as status;