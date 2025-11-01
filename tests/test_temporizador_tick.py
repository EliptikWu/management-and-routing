"""
E9 - Pruebas del Temporizador (Tick)
Verifica el funcionamiento del temporizador y acumulación de segundos
"""
import pytest
from sqlalchemy.orm import Session
from src.models import Orden, OrdenArea, Area, Historial
from src.services.temporizador_service import TemporizadorService
from src.config import settings


def test_tick_incrementa_segundos_en_progreso(db: Session, clean_test_orden):
    """
    Verifica que el tick incremente segundos en áreas EN_PROGRESO
    """
    orden = clean_test_orden
    area = db.query(Area).first()
    
    # Crear asignación EN_PROGRESO con segundos iniciales
    segundos_iniciales = 30
    asignacion = OrdenArea(
        orden_id=orden.id,
        area_id=area.id,
        estado_parcial="EN_PROGRESO",
        seg_acumulados=segundos_iniciales
    )
    db.add(asignacion)
    db.commit()
    
    asignacion_id = asignacion.id
    
    # Ejecutar tick
    resultado = TemporizadorService.ejecutar_tick(db)
    
    # VERIFICACIÓN
    assert resultado["areas_actualizadas"] >= 1, (
        f"No se actualizó ningún área. Resultado: {resultado}"
    )
    
    # Recargar asignación
    asignacion = db.query(OrdenArea).filter(OrdenArea.id == asignacion_id).first()
    segundos_esperados = segundos_iniciales + settings.N_SEG
    
    assert asignacion.seg_acumulados == segundos_esperados, (
        f"Segundos no incrementados correctamente. "
        f"Inicial: {segundos_iniciales}, Esperado: {segundos_esperados}, "
        f"Obtenido: {asignacion.seg_acumulados}"
    )
    
    print(f"✅ TICK incrementó segundos: {segundos_iniciales}s → {asignacion.seg_acumulados}s")


def test_tick_no_incrementa_completadas(db: Session, clean_test_orden):
    """
    Verifica que el tick NO incremente segundos en áreas COMPLETADAS
    """
    orden = clean_test_orden
    area = db.query(Area).first()
    
    segundos_iniciales = 100
    asignacion = OrdenArea(
        orden_id=orden.id,
        area_id=area.id,
        estado_parcial="COMPLETADA",
        seg_acumulados=segundos_iniciales
    )
    db.add(asignacion)
    db.commit()
    
    asignacion_id = asignacion.id
    
    # Ejecutar tick
    TemporizadorService.ejecutar_tick(db)
    
    # VERIFICACIÓN: segundos deben permanecer iguales
    asignacion = db.query(OrdenArea).filter(OrdenArea.id == asignacion_id).first()
    assert asignacion.seg_acumulados == segundos_iniciales, (
        f"Los segundos de áreas COMPLETADAS no deben cambiar. "
        f"Inicial: {segundos_iniciales}, Obtenido: {asignacion.seg_acumulados}"
    )
    
    print(f"✅ TICK respetó área COMPLETADA (segundos sin cambio: {segundos_iniciales}s)")


def test_tick_aplica_timeout_correctamente(db: Session, clean_test_orden):
    """
    Verifica que el tick aplique timeout cuando se supera el SLA
    """
    orden = clean_test_orden
    area = db.query(Area).first()
    
    # Crear asignación justo en el límite del SLA
    segundos_en_limite = settings.SLA_SEG - settings.N_SEG
    asignacion = OrdenArea(
        orden_id=orden.id,
        area_id=area.id,
        estado_parcial="EN_PROGRESO",
        seg_acumulados=segundos_en_limite
    )
    db.add(asignacion)
    orden.estado_global = "EN_PROGRESO"
    db.commit()
    
    asignacion_id = asignacion.id
    
    # Ejecutar tick (esto debe incrementar y superar el SLA)
    resultado = TemporizadorService.ejecutar_tick(db)
    
    # VERIFICACIÓN
    asignacion = db.query(OrdenArea).filter(OrdenArea.id == asignacion_id).first()
    
    # Verificar que se incrementaron los segundos
    assert asignacion.seg_acumulados >= settings.SLA_SEG, (
        f"Segundos no superaron el SLA. "
        f"SLA: {settings.SLA_SEG}s, Actual: {asignacion.seg_acumulados}s"
    )
    
    # Verificar que se aplicó el timeout
    assert asignacion.estado_parcial == settings.ESTADO_TIMEOUT, (
        f"Timeout no aplicado. Estado actual: {asignacion.estado_parcial}, "
        f"Esperado: {settings.ESTADO_TIMEOUT}"
    )
    
    # Verificar que se registró en historial
    evento_timeout = db.query(Historial).filter(
        Historial.orden_id == orden.id,
        Historial.evento == "TIMEOUT_SLA"
    ).first()
    
    assert evento_timeout is not None, "Evento TIMEOUT_SLA no registrado en historial"
    assert "superó el SLA" in evento_timeout.detalle, (
        f"Detalle del evento incorrecto: {evento_timeout.detalle}"
    )
    
    print(f"✅ TICK aplicó timeout: {segundos_en_limite}s + {settings.N_SEG}s = {asignacion.seg_acumulados}s >= {settings.SLA_SEG}s => {settings.ESTADO_TIMEOUT}")


def test_tick_multiples_ordenes_concurrentes(db: Session):
    """
    Verifica que el tick maneje múltiples órdenes en progreso simultáneamente
    """
    # Obtener órdenes existentes del seed
    ordenes_en_progreso = db.query(Orden).filter(
        Orden.estado_global.in_(["EN_PROGRESO", "PENDIENTE"])
    ).limit(3).all()
    
    if not ordenes_en_progreso:
        pytest.skip("No hay órdenes EN_PROGRESO en seed data para esta prueba")
    
    # Guardar segundos iniciales
    segundos_antes = {}
    for orden in ordenes_en_progreso:
        asignaciones = db.query(OrdenArea).filter(
            OrdenArea.orden_id == orden.id,
            OrdenArea.estado_parcial.in_(["EN_PROGRESO", "PENDIENTE"])
        ).all()
        segundos_antes[orden.id] = sum(a.seg_acumulados for a in asignaciones)
    
    # Ejecutar tick
    resultado = TemporizadorService.ejecutar_tick(db)
    
    # VERIFICACIÓN: al menos una orden debe haber sido actualizada
    assert resultado["areas_actualizadas"] > 0, (
        f"Ningún área fue actualizada. Resultado: {resultado}"
    )
    
    # Verificar que los segundos aumentaron en al menos una orden
    segundos_incrementados = False
    for orden in ordenes_en_progreso:
        asignaciones = db.query(OrdenArea).filter(
            OrdenArea.orden_id == orden.id,
            OrdenArea.estado_parcial.in_(["EN_PROGRESO", "PENDIENTE", "VENCIDA"])
        ).all()
        segundos_despues = sum(a.seg_acumulados for a in asignaciones)
        
        if segundos_despues > segundos_antes.get(orden.id, 0):
            segundos_incrementados = True
            break
    
    assert segundos_incrementados, (
        "Ninguna orden incrementó sus segundos después del tick"
    )
    
    print(f"✅ TICK manejó múltiples órdenes: {len(ordenes_en_progreso)} órdenes, "
          f"{resultado['areas_actualizadas']} áreas actualizadas")


def test_tick_es_idempotente(db: Session, clean_test_orden):
    """
    Verifica que ejecutar el tick múltiples veces sea seguro (idempotencia)
    """
    orden = clean_test_orden
    area = db.query(Area).first()
    
    asignacion = OrdenArea(
        orden_id=orden.id,
        area_id=area.id,
        estado_parcial="EN_PROGRESO",
        seg_acumulados=0
    )
    db.add(asignacion)
    db.commit()
    
    asignacion_id = asignacion.id
    
    # Ejecutar tick 3 veces
    for i in range(3):
        resultado = TemporizadorService.ejecutar_tick(db)
        assert "errores" not in resultado or len(resultado["errores"]) == 0, (
            f"Tick {i+1} generó errores: {resultado.get('errores', [])}"
        )
    
    # Verificar incremento correcto
    asignacion = db.query(OrdenArea).filter(OrdenArea.id == asignacion_id).first()
    segundos_esperados = settings.N_SEG * 3
    
    assert asignacion.seg_acumulados == segundos_esperados, (
        f"Incremento no lineal. Esperado: {segundos_esperados}s, "
        f"Obtenido: {asignacion.seg_acumulados}s"
    )
    
    print(f"✅ TICK es idempotente: 3 ejecuciones = {asignacion.seg_acumulados}s "
          f"({settings.N_SEG}s × 3)")