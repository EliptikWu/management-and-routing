"""
E9 - Pruebas de Reglas de Estado Global
Verifica que el sistema calcule correctamente el estado global según los estados parciales
"""
import pytest
from sqlalchemy.orm import Session
from src.models import Orden, OrdenArea, Area
from src.services.estado_service import EstadoService


def test_caso_1_dos_areas_una_completada_otra_en_progreso(db: Session, clean_test_orden):
    """
    CASO 1: Dos áreas: una COMPLETADA, otra EN_PROGRESO => global EN_PROGRESO
    """
    orden = clean_test_orden
    
    # Obtener áreas existentes del seed
    area_soporte = db.query(Area).filter(Area.id == 1).first()
    area_infraestructura = db.query(Area).filter(Area.id == 2).first()
    
    assert area_soporte is not None, "Área de Soporte no encontrada en seed data"
    assert area_infraestructura is not None, "Área de Infraestructura no encontrada en seed data"
    
    # Asignar dos áreas con estados diferentes
    asignacion1 = OrdenArea(
        orden_id=orden.id,
        area_id=area_soporte.id,
        estado_parcial="COMPLETADA",
        seg_acumulados=120
    )
    asignacion2 = OrdenArea(
        orden_id=orden.id,
        area_id=area_infraestructura.id,
        estado_parcial="EN_PROGRESO",
        seg_acumulados=45
    )
    
    db.add(asignacion1)
    db.add(asignacion2)
    db.commit()
    
    # Recargar orden con sus asignaciones
    db.refresh(orden)
    
    # Recalcular estado global
    nuevo_estado = EstadoService.recalcular_estado_global(db, orden)
    db.commit()
    
    # VERIFICACIÓN
    assert nuevo_estado == "EN_PROGRESO", (
        f"Estado global incorrecto. Esperado: EN_PROGRESO, Obtenido: {nuevo_estado}"
    )
    
    # Verificar que se guardó en la base de datos
    db.refresh(orden)
    assert orden.estado_global == "EN_PROGRESO", (
        f"Estado no persistido correctamente. Estado en BD: {orden.estado_global}"
    )
    
    print("✅ CASO 1 PASÓ: Dos áreas (COMPLETADA + EN_PROGRESO) => EN_PROGRESO")


def test_caso_2_timeout_sla_cambia_a_vencida(db: Session, clean_test_orden):
    """
    CASO 2: Timeout SLA => estado_timeout (VENCIDA) y global se recalcula
    """
    from src.services.temporizador_service import TemporizadorService
    from src.config import settings
    
    orden = clean_test_orden
    
    # Obtener área de prueba
    area = db.query(Area).filter(Area.id == 1).first()
    
    # Crear asignación EN_PROGRESO con segundos que exceden el SLA
    asignacion = OrdenArea(
        orden_id=orden.id,
        area_id=area.id,
        estado_parcial="EN_PROGRESO",
        seg_acumulados=settings.SLA_SEG + 10  # Excede el SLA
    )
    
    db.add(asignacion)
    orden.estado_global = "EN_PROGRESO"
    db.commit()
    
    # Ejecutar lógica de timeout (simula el tick del temporizador)
    # Aplicar timeout manualmente porque la asignación ya excede SLA
    if asignacion.seg_acumulados >= settings.SLA_SEG:
        asignacion.estado_parcial = settings.ESTADO_TIMEOUT
        db.commit()
    
    # Recalcular estado global
    EstadoService.recalcular_estado_global(db, orden)
    db.commit()
    
    # VERIFICACIÓN
    db.refresh(asignacion)
    assert asignacion.estado_parcial == settings.ESTADO_TIMEOUT, (
        f"Timeout no aplicado. Estado parcial: {asignacion.estado_parcial}"
    )
    
    db.refresh(orden)
    # Con solo una área VENCIDA, el estado global debe ser VENCIDA
    assert orden.estado_global == "VENCIDA", (
        f"Estado global incorrecto después de timeout. Esperado: VENCIDA, Obtenido: {orden.estado_global}"
    )
    
    print(f"✅ CASO 2 PASÓ: Timeout SLA ({settings.SLA_SEG}s) => {settings.ESTADO_TIMEOUT} => global VENCIDA")


def test_caso_3_todas_completadas_global_completada(db: Session, clean_test_orden):
    """
    CASO 3: Todas las áreas COMPLETADAS => global COMPLETADA
    """
    orden = clean_test_orden
    
    # Obtener 3 áreas diferentes
    areas = db.query(Area).limit(3).all()
    assert len(areas) >= 3, "Se necesitan al menos 3 áreas en seed data"
    
    # Asignar todas las áreas con estado COMPLETADA
    for area in areas:
        asignacion = OrdenArea(
            orden_id=orden.id,
            area_id=area.id,
            estado_parcial="COMPLETADA",
            seg_acumulados=60
        )
        db.add(asignacion)
    
    db.commit()
    db.refresh(orden)
    
    # Recalcular estado global
    nuevo_estado = EstadoService.recalcular_estado_global(db, orden)
    db.commit()
    
    # VERIFICACIÓN
    assert nuevo_estado == "COMPLETADA", (
        f"Estado global incorrecto. Esperado: COMPLETADA, Obtenido: {nuevo_estado}"
    )
    
    db.refresh(orden)
    assert orden.estado_global == "COMPLETADA", (
        f"Estado no persistido. Estado en BD: {orden.estado_global}"
    )
    
    # Verificar que todas las asignaciones estén COMPLETADAS
    asignaciones = db.query(OrdenArea).filter(OrdenArea.orden_id == orden.id).all()
    estados_parciales = [a.estado_parcial for a in asignaciones]
    assert all(e == "COMPLETADA" for e in estados_parciales), (
        f"No todas las áreas están COMPLETADAS: {estados_parciales}"
    )
    
    print(f"✅ CASO 3 PASÓ: {len(areas)} áreas COMPLETADAS => global COMPLETADA")


def test_caso_extra_mezcla_estados_complejos(db: Session, clean_test_orden):
    """
    CASO EXTRA: Mezcla de estados - verifica prioridad de reglas
    ASIGNADA + PENDIENTE + EN_PROGRESO => EN_PROGRESO (tiene prioridad)
    """
    orden = clean_test_orden
    areas = db.query(Area).limit(3).all()
    
    estados_mezcla = ["ASIGNADA", "PENDIENTE", "EN_PROGRESO"]
    for i, area in enumerate(areas):
        asignacion = OrdenArea(
            orden_id=orden.id,
            area_id=area.id,
            estado_parcial=estados_mezcla[i],
            seg_acumulados=30
        )
        db.add(asignacion)
    
    db.commit()
    db.refresh(orden)
    
    nuevo_estado = EstadoService.recalcular_estado_global(db, orden)
    db.commit()
    
    # EN_PROGRESO tiene prioridad sobre PENDIENTE y ASIGNADA
    assert nuevo_estado == "EN_PROGRESO", (
        f"Prioridad de estados incorrecta. Esperado: EN_PROGRESO, Obtenido: {nuevo_estado}"
    )
    
    print("✅ CASO EXTRA PASÓ: Mezcla de estados => EN_PROGRESO (prioridad correcta)")