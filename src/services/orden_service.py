"""
Servicio: Lógica de negocio para órdenes
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, case
from typing import List, Optional
from datetime import datetime

from src.models import Orden, OrdenArea, Area, Historial
from src.schemas.orden import OrdenCreate, AsignacionCreate, CambioEstadoRequest
from src.services.estado_service import EstadoService


class OrdenService:
    
    @staticmethod
    def crear_orden(db: Session, orden_data: OrdenCreate) -> Orden:
        """Crea una nueva orden con historial inicial"""
        nueva_orden = Orden(
            titulo=orden_data.titulo,
            descripcion=orden_data.descripcion,
            creador=orden_data.creador,
            prioridad=orden_data.prioridad,
            estado_global='NUEVA'
        )
        
        db.add(nueva_orden)
        db.flush()  # Obtener ID sin commit
        
        # Historial automático (también por trigger en BD)
        historial = Historial(
            orden_id=nueva_orden.id,
            evento='CREADA',
            detalle=f'Orden creada: {orden_data.titulo}',
            estado_global='NUEVA',
            actor=orden_data.creador
        )
        db.add(historial)
        db.commit()
        db.refresh(nueva_orden)
        
        return nueva_orden
    
    @staticmethod
    def listar_ordenes(
        db: Session, 
        estado: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[dict]:
        """Lista órdenes con agregaciones de áreas"""
        query = db.query(
            Orden.id,
            Orden.titulo,
            Orden.estado_global,
            Orden.prioridad,
            Orden.creador,
            Orden.creada_en,
            Orden.actualizada_en,
            func.count(OrdenArea.id).label('num_areas'),
            func.sum(
                case(
                    (OrdenArea.estado_parcial == 'COMPLETADA', 1),
                    else_=0
                )
            ).label('areas_completadas'),
            func.sum(OrdenArea.seg_acumulados).label('total_segundos')
        ).outerjoin(OrdenArea, Orden.id == OrdenArea.orden_id)
        
        if estado:
            query = query.filter(Orden.estado_global == estado)
        
        query = query.group_by(Orden.id).order_by(Orden.actualizada_en.desc())
        query = query.offset(skip).limit(limit)
        
        return [
            {
                'id': row.id,
                'titulo': row.titulo,
                'estado_global': row.estado_global,
                'prioridad': row.prioridad,
                'creador': row.creador,
                'num_areas': row.num_areas or 0,
                'areas_completadas': row.areas_completadas or 0,
                'total_segundos': row.total_segundos or 0,
                'creada_en': row.creada_en,
                'actualizada_en': row.actualizada_en
            }
            for row in query.all()
        ]
    
    @staticmethod
    def obtener_orden(db: Session, orden_id: int) -> Optional[Orden]:
        """Obtiene una orden con sus asignaciones y datos de áreas"""
        return db.query(Orden).options(
            joinedload(Orden.asignaciones).joinedload(OrdenArea.area)
        ).filter(Orden.id == orden_id).first()
    
    @staticmethod
    def asignar_areas(
        db: Session, 
        orden_id: int, 
        asignacion_data: AsignacionCreate,
        actor: str = "SISTEMA"
    ) -> Orden:
        """Asigna áreas a una orden"""
        orden = db.query(Orden).filter(Orden.id == orden_id).first()
        if not orden:
            raise ValueError(f"Orden {orden_id} no encontrada")
        
        # Verificar que áreas existen
        areas = db.query(Area).filter(Area.id.in_(asignacion_data.area_ids)).all()
        if len(areas) != len(asignacion_data.area_ids):
            raise ValueError("Una o más áreas no existen")
        
        # Crear asignaciones
        for area in areas:
            # Evitar duplicados
            existe = db.query(OrdenArea).filter(
                OrdenArea.orden_id == orden_id,
                OrdenArea.area_id == area.id
            ).first()
            
            if not existe:
                asignacion = OrdenArea(
                    orden_id=orden_id,
                    area_id=area.id,
                    asignada_a=asignacion_data.asignada_a,
                    estado_parcial='ASIGNADA'
                )
                db.add(asignacion)
                
                # Historial
                historial = Historial(
                    orden_id=orden_id,
                    evento='AREA_ASIGNADA',
                    detalle=f'Área asignada: {area.nombre}' + 
                            (f' → {asignacion_data.asignada_a}' if asignacion_data.asignada_a else ''),
                    actor=actor
                )
                db.add(historial)
        
        # Recalcular estado global
        EstadoService.recalcular_estado_global(db, orden)
        
        db.commit()
        db.refresh(orden)
        return orden
    
    @staticmethod
    def quitar_area(db: Session, orden_id: int, area_id: int, actor: str = "SISTEMA") -> Orden:
        """Quita un área de una orden"""
        asignacion = db.query(OrdenArea).filter(
            OrdenArea.orden_id == orden_id,
            OrdenArea.area_id == area_id
        ).first()
        
        if not asignacion:
            raise ValueError(f"Asignación no encontrada")
        
        area_nombre = asignacion.area.nombre
        
        db.delete(asignacion)
        
        # Historial
        orden = db.query(Orden).filter(Orden.id == orden_id).first()
        historial = Historial(
            orden_id=orden_id,
            evento='AREA_REMOVIDA',
            detalle=f'Área removida: {area_nombre}',
            actor=actor
        )
        db.add(historial)
        
        # Recalcular estado global
        EstadoService.recalcular_estado_global(db, orden)
        
        db.commit()
        db.refresh(orden)
        return orden
    
    @staticmethod
    def cambiar_estado_parcial(
        db: Session, 
        orden_id: int, 
        area_id: int, 
        cambio_data: CambioEstadoRequest,
        actor: str = "SISTEMA"
    ) -> OrdenArea:
        """Cambia el estado parcial de un área en una orden"""
        asignacion = db.query(OrdenArea).filter(
            OrdenArea.orden_id == orden_id,
            OrdenArea.area_id == area_id
        ).first()
        
        if not asignacion:
            raise ValueError(f"Asignación no encontrada")
        
        estado_anterior = asignacion.estado_parcial
        asignacion.estado_parcial = cambio_data.nuevo_estado
        
        # Actualizar timestamps según el estado
        if cambio_data.nuevo_estado == 'EN_PROGRESO' and not asignacion.iniciada_en:
            asignacion.iniciada_en = datetime.utcnow()
        elif cambio_data.nuevo_estado in ['COMPLETADA', 'CERRADA_SIN_SOLUCION']:
            asignacion.completada_en = datetime.utcnow()
        elif cambio_data.nuevo_estado == 'PENDIENTE':
            asignacion.pausada_en = datetime.utcnow()
        
        if cambio_data.notas:
            asignacion.notas = cambio_data.notas
        
        # Historial
        historial = Historial(
            orden_id=orden_id,
            evento='CAMBIO_ESTADO_PARCIAL',
            detalle=f'Área {asignacion.area.nombre}: {estado_anterior} → {cambio_data.nuevo_estado}',
            actor=actor
        )
        db.add(historial)
        
        # Recalcular estado global
        orden = db.query(Orden).filter(Orden.id == orden_id).first()
        EstadoService.recalcular_estado_global(db, orden)
        
        db.commit()
        db.refresh(asignacion)
        return asignacion