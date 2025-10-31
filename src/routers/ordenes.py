"""
Router: Endpoints de órdenes
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional

from src.database import get_db
from src.schemas.orden import (
    OrdenCreate, OrdenResponse, OrdenListResponse,
    AsignacionCreate, CambioEstadoRequest, OrdenAreaResponse
)
from src.schemas.historial import HistorialResponse
from src.services.orden_service import OrdenService
from src.models import Historial

router = APIRouter(prefix="/ordenes", tags=["Órdenes"])


@router.post("/", response_model=OrdenResponse, status_code=201)
def crear_orden(
    orden_data: OrdenCreate,
    db: Session = Depends(get_db)
):
    """
    Crea una nueva orden de trabajo
    
    - **titulo**: Título descriptivo (5-200 caracteres)
    - **descripcion**: Descripción detallada (mínimo 10 caracteres)
    - **creador**: Email o nombre del creador
    - **prioridad**: BAJA | MEDIA | ALTA | CRITICA
    """
    try:
        orden = OrdenService.crear_orden(db, orden_data)
        return orden
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[OrdenListResponse])
def listar_ordenes(
    estado: Optional[str] = Query(None, description="Filtrar por estado global"),
    skip: int = Query(0, ge=0, description="Órdenes a omitir"),
    limit: int = Query(100, ge=1, le=500, description="Máximo de órdenes"),
    db: Session = Depends(get_db)
):
    """
    Lista órdenes con agregaciones
    
    - **estado**: Filtro opcional por estado_global
    - Incluye conteo de áreas y segundos acumulados
    """
    ordenes = OrdenService.listar_ordenes(db, estado, skip, limit)
    return ordenes


@router.get("/{orden_id}", response_model=OrdenResponse)
def obtener_orden(
    orden_id: int = Path(..., gt=0, description="ID de la orden"),
    db: Session = Depends(get_db)
):
    """
    Obtiene el detalle completo de una orden
    
    Incluye:
    - Datos de la orden
    - Todas las asignaciones de áreas con sus estados
    - Segundos acumulados por área
    """
    orden = OrdenService.obtener_orden(db, orden_id)
    if not orden:
        raise HTTPException(status_code=404, detail=f"Orden {orden_id} no encontrada")
    
    # Enriquecer asignaciones con nombre del área
    for asignacion in orden.asignaciones:
        asignacion.area_nombre = asignacion.area.nombre
    
    return orden


@router.post("/{orden_id}/asignaciones", response_model=OrdenResponse)
def asignar_areas(
    orden_id: int = Path(..., gt=0),
    asignacion_data: AsignacionCreate = ...,
    db: Session = Depends(get_db)
):
    """
    Asigna una o más áreas a una orden
    
    - **area_ids**: Lista de IDs de áreas (mínimo 1)
    - **asignada_a**: Persona específica (opcional)
    
    No permite duplicados (orden-área)
    """
    try:
        orden = OrdenService.asignar_areas(db, orden_id, asignacion_data, actor="API_USER")
        
        # Enriquecer asignaciones
        for asignacion in orden.asignaciones:
            asignacion.area_nombre = asignacion.area.nombre
        
        return orden
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{orden_id}/asignaciones/{area_id}", response_model=OrdenResponse)
def quitar_area(
    orden_id: int = Path(..., gt=0),
    area_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """
    Quita un área de una orden
    
    Recalcula el estado global automáticamente
    """
    try:
        orden = OrdenService.quitar_area(db, orden_id, area_id, actor="API_USER")
        
        for asignacion in orden.asignaciones:
            asignacion.area_nombre = asignacion.area.nombre
        
        return orden
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{orden_id}/areas/{area_id}", response_model=OrdenAreaResponse)
def cambiar_estado_parcial(
    orden_id: int = Path(..., gt=0),
    area_id: int = Path(..., gt=0),
    cambio_data: CambioEstadoRequest = ...,
    db: Session = Depends(get_db)
):
    """
    Cambia el estado parcial de un área en una orden
    
    Estados válidos:
    - EN_PROGRESO: Área trabajando activamente
    - PENDIENTE: Pausado temporalmente
    - COMPLETADA: Área finalizó su parte
    - CERRADA_SIN_SOLUCION: Cerrada sin resolver
    - VENCIDA: Superó el SLA (generalmente por temporizador)
    
    Actualiza timestamps automáticamente y recalcula estado global
    """
    try:
        asignacion = OrdenService.cambiar_estado_parcial(
            db, orden_id, area_id, cambio_data, actor="API_USER"
        )
        asignacion.area_nombre = asignacion.area.nombre
        return asignacion
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{orden_id}/historial", response_model=List[HistorialResponse])
def obtener_historial(
    orden_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """
    Obtiene el historial completo de eventos de una orden
    
    Ordenado cronológicamente (más reciente primero)
    """
    historial = db.query(Historial).filter(
        Historial.orden_id == orden_id
    ).order_by(Historial.timestamp.desc()).all()
    
    if not historial:
        # Verificar si la orden existe
        from src.models import Orden
        orden = db.query(Orden).filter(Orden.id == orden_id).first()
        if not orden:
            raise HTTPException(status_code=404, detail=f"Orden {orden_id} no encontrada")
    
    return historial