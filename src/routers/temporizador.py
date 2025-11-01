"""
Router: Endpoints del temporizador
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict

from src.database import get_db
from src.services.temporizador_service import TemporizadorService
from src.scheduler import temporizador_scheduler

router = APIRouter(prefix="/temporizador", tags=["Temporizador"])


@router.post("/tick", response_model=Dict)
def ejecutar_tick_manual(db: Session = Depends(get_db)):
    """
    Ejecuta un tick del temporizador manualmente
    
    **Útil para:**
    - Testing y debugging
    - Forzar actualización inmediata
    - Llamadas desde frontend (alternativa A)
    
    **Acciones:**
    - Incrementa seg_acumulados en áreas EN_PROGRESO/PENDIENTE
    - Aplica timeout si seg_acumulados >= SLA_SEG
    - Recalcula estado_global de órdenes afectadas
    - Registra eventos TIMEOUT en historial
    """
    resultado = TemporizadorService.ejecutar_tick(db)
    return resultado


@router.get("/estado", response_model=Dict)
def obtener_estado_temporizador():
    """
    Obtiene el estado actual del temporizador
    
    Retorna información sobre:
    - Jobs activos
    - Próxima ejecución programada
    - Configuración (N_SEG, SLA_SEG)
    """
    from src.config import settings
    
    jobs = temporizador_scheduler.obtener_jobs()
    
    return {
        "activo": len(jobs) > 0,
        "configuracion": {
            "n_seg": settings.N_SEG,
            "sla_seg": settings.SLA_SEG,
            "estado_timeout": settings.ESTADO_TIMEOUT
        },
        "jobs": jobs
    }


@router.get("/estadisticas-sla", response_model=Dict)
def obtener_estadisticas_sla(db: Session = Depends(get_db)):
    """
    Obtiene estadísticas sobre el cumplimiento de SLA
    
    Retorna:
    - Total de áreas activas
    - Áreas cerca del límite (>80% SLA)
    - Áreas vencidas
    - Promedio de segundos acumulados
    - Porcentaje de cumplimiento
    """
    estadisticas = TemporizadorService.obtener_estadisticas_sla(db)
    return estadisticas


@router.post("/reiniciar")
def reiniciar_temporizador():
    """
    Reinicia el scheduler del temporizador
    
    **Advertencia:** Solo usar en caso de problemas
    """
    temporizador_scheduler.detener()
    temporizador_scheduler.iniciar()
    return {"mensaje": "Temporizador reiniciado correctamente"}