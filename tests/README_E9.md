# E9: Guía de Pruebas

## 📋 Requisitos Previos

1. Base de datos inicializada con seed data:
```bash
mysql -u root -p ordenes_multiarea < db/migrations/001_initial_schema.sql
mysql -u root -p ordenes_multiarea < db/seeds/seed_data.sql
```

2. Dependencias instaladas:
```bash
pip install -r requirements.txt
```

3. Servidor corriendo (para algunas pruebas de integración):
```bash
python src/main.py
```

## 🚀 Comandos de Ejecución

### Ejecutar TODAS las pruebas del E9
```bash
pytest tests/test_reglas_estado.py tests/test_temporizador_tick.py -v
```

### Ejecutar solo pruebas de reglas de estado
```bash
pytest tests/test_reglas_estado.py -v
```

### Ejecutar solo pruebas del temporizador
```bash
pytest tests/test_temporizador_tick.py -v
```

### Ejecutar una prueba específica
```bash
pytest tests/test_reglas_estado.py::test_caso_1_dos_areas_una_completada_otra_en_progreso -v
```

### Ejecutar con salida detallada
```bash
pytest tests/test_reglas_estado.py -v -s
```

### Ejecutar con coverage
```bash
pytest tests/test_reglas_estado.py tests/test_temporizador_tick.py --cov=src/services --cov-report=html
```

## ✅ Casos de Prueba Implementados

### Reglas de Estado (`test_reglas_estado.py`)
- ✅ **CASO 1**: Dos áreas (COMPLETADA + EN_PROGRESO) => EN_PROGRESO
- ✅ **CASO 2**: Timeout SLA => VENCIDA => global VENCIDA
- ✅ **CASO 3**: Todas COMPLETADAS => global COMPLETADA
- ✅ **CASO EXTRA**: Mezcla de estados => prioridad correcta

### Temporizador (`test_temporizador_tick.py`)
- ✅ Incremento de segundos en áreas EN_PROGRESO
- ✅ No incremento en áreas COMPLETADAS
- ✅ Aplicación de timeout al superar SLA
- ✅ Manejo de múltiples órdenes concurrentes
- ✅ Idempotencia del tick

## 📊 Salida Esperada
```
tests/test_reglas_estado.py::test_caso_1_dos_areas_una_completada_otra_en_progreso PASSED [ 14%]
✅ CASO 1 PASÓ: Dos áreas (COMPLETADA + EN_PROGRESO) => EN_PROGRESO

tests/test_reglas_estado.py::test_caso_2_timeout_sla_cambia_a_vencida PASSED [ 28%]
✅ CASO 2 PASÓ: Timeout SLA (60s) => VENCIDA => global VENCIDA

tests/test_reglas_estado.py::test_caso_3_todas_completadas_global_completada PASSED [ 42%]
✅ CASO 3 PASÓ: 3 áreas COMPLETADAS => global COMPLETADA

tests/test_reglas_estado.py::test_caso_extra_mezcla_estados_complejos PASSED [ 57%]
✅ CASO EXTRA PASÓ: Mezcla de estados => EN_PROGRESO (prioridad correcta)

tests/test_temporizador_tick.py::test_tick_incrementa_segundos_en_progreso PASSED [ 71%]
✅ TICK incrementó segundos: 30s → 40s

tests/test_temporizador_tick.py::test_tick_no_incrementa_completadas PASSED [ 85%]
✅ TICK respetó área COMPLETADA (segundos sin cambio: 100s)

tests/test_temporizador_tick.py::test_tick_aplica_timeout_correctamente PASSED [100%]
✅ TICK aplicó timeout: 50s + 10s = 60s >= 60s => VENCIDA

========================== 7 passed in 2.45s ==========================
```

## 🐛 Troubleshooting

### Error: "Área de Soporte no encontrada en seed data"
**Solución**: Ejecutar el seed data:
```bash
mysql -u root -p ordenes_multiarea < db/seeds/seed_data.sql
```

### Error: "Can't connect to MySQL server"
**Solución**: Verificar que MySQL esté corriendo y `.env` tenga credenciales correctas

### Error: "No module named 'pytest'"
**Solución**: 
```bash
pip install pytest pytest-asyncio
```

## 📝 Notas

- Las pruebas usan la base de datos REAL (no mock) para mayor fidelidad
- Cada prueba limpia sus datos de prueba al finalizar
- Se recomienda ejecutar en entorno de desarrollo, NO en producción
- El fixture `clean_test_orden` crea/elimina órdenes automáticamente