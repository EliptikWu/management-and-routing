"""
Servicio: Lógica del temporizador (tick)
Incrementa segundos y aplica reglas de SLA
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime
from typing import Dict, List

from src.models import Orden, OrdenArea, Historial
from src.services.estado_service import EstadoService
from src.config import settings


class TemporizadorService:
    
    @staticmethod
    def ejecutar_tick(db: Session) -> Dict:
        """
        Ejecuta un ciclo del temporizador de forma idempotente
        
        Retorna:
            Dict con estadísticas de la ejecución
        """
        resultado = {
            "timestamp": datetime.utcnow().isoformat(),
            "areas_actualizadas": 0,
            "timeouts_aplicados": 0,
            "ordenes_recalculadas": [],
            "errores": []
        }
        
        try:
            # 1. Incrementar segundos en áreas activas
            areas_actualizadas = TemporizadorService._incrementar_segundos(db)
            resultado["areas_actualizadas"] = areas_actualizadas
            
            # 2. Aplicar timeouts a áreas que superaron SLA
            timeouts = TemporizadorService._aplicar_timeouts(db)
            resultado["timeouts_aplicados"] = len(timeouts)
            
            # 3. Recalcular estados globales de órdenes afectadas
            ordenes_afectadas = TemporizadorService._obtener_ordenes_afectadas(db)
            for orden in ordenes_afectadas:
                EstadoService.recalcular_estado_global(db, orden)
                resultado["ordenes_recalculadas"].append(orden.id)
            
            # 4. Commit de todos los cambios
            db.commit()
            
            # Log resumido
            if areas_actualizadas > 0 or len(timeouts) > 0:
                print(f"⏱️  TICK: {areas_actualizadas} áreas actualizadas, "
                      f"{len(timeouts)} timeouts aplicados, "
                      f"{len(ordenes_afectadas)} órdenes recalculadas")
            
        except Exception as e:
            db.rollback()
            resultado["errores"].append(str(e))
            print(f"❌ Error en tick: {e}")
        
        return resultado
    
    @staticmethod
    def _incrementar_segundos(db: Session) -> int:
        """
        Incrementa seg_acumulados en áreas con estados activos
        
        Estados activos: EN_PROGRESO, PENDIENTE
        
        Retorna:
            Número de áreas actualizadas
        """
        # Obtener áreas en estados que acumulan tiempo
        areas_activas = db.query(OrdenArea).filter(
            OrdenArea.estado_parcial.in_(['EN_PROGRESO', 'PENDIENTE'])
        ).all()
        
        for area in areas_activas:
            area.seg_acumulados += settings.N_SEG
        
        return len(areas_activas)
    
    @staticmethod
    def _aplicar_timeouts(db: Session) -> List[OrdenArea]:
        """
        Aplica timeout a áreas EN_PROGRESO que superaron el SLA
        
        Retorna:
            Lista de áreas que recibieron timeout
        """
        # Buscar áreas EN_PROGRESO que superaron el SLA
        areas_vencidas = db.query(OrdenArea).filter(
            and_(
                OrdenArea.estado_parcial == 'EN_PROGRESO',
                OrdenArea.seg_acumulados >= settings.SLA_SEG
            )
        ).all()
        
        timeouts_aplicados = []
        
        for area in areas_vencidas:
            # Cambiar estado a ESTADO_TIMEOUT configurado
            estado_anterior = area.estado_parcial
            area.estado_parcial = settings.ESTADO_TIMEOUT
            
            # Registrar en historial
            historial = Historial(
                orden_id=area.orden_id,
                evento='TIMEOUT_SLA',
                detalle=f'Área {area.area.nombre} superó el SLA de {settings.SLA_SEG}s '
                        f'(acumulados: {area.seg_acumulados}s). '
                        f'Estado: {estado_anterior} → {settings.ESTADO_TIMEOUT}',
                actor='SISTEMA_TEMPORIZADOR'
            )
            db.add(historial)
            
            timeouts_aplicados.append(area)
            
            print(f"⏰ TIMEOUT: Orden #{area.orden_id} - Área {area.area.nombre} "
                  f"({area.seg_acumulados}s >= {settings.SLA_SEG}s)")
        
        return timeouts_aplicados
    
    @staticmethod
    def _obtener_ordenes_afectadas(db: Session) -> List[Orden]:
        """
        Obtiene órdenes que fueron modificadas en este tick
        
        Retorna:
            Lista de órdenes que necesitan recalcular estado global
        """
        # Obtener IDs de órdenes con áreas activas (que fueron actualizadas)
        ordenes_ids = db.query(OrdenArea.orden_id).filter(
            OrdenArea.estado_parcial.in_(['EN_PROGRESO', 'PENDIENTE', settings.ESTADO_TIMEOUT])
        ).distinct().all()
        
        orden_ids_list = [oid[0] for oid in ordenes_ids]
        
        # Obtener las órdenes completas
        ordenes = db.query(Orden).filter(Orden.id.in_(orden_ids_list)).all()
        
        return ordenes
    
    @staticmethod
    def obtener_estadisticas_sla(db: Session) -> Dict:
        """
        Obtiene estadísticas sobre el cumplimiento de SLA
        
        Retorna:
            Dict con métricas de SLA
        """
        from sqlalchemy import func
        
        # Total de áreas activas
        total_activas = db.query(func.count(OrdenArea.id)).filter(
            OrdenArea.estado_parcial.in_(['EN_PROGRESO', 'PENDIENTE'])
        ).scalar()
        
        # Áreas cerca del límite (>80% del SLA)
        limite_advertencia = int(settings.SLA_SEG * 0.8)
        cerca_limite = db.query(func.count(OrdenArea.id)).filter(
            and_(
                OrdenArea.estado_parcial == 'EN_PROGRESO',
                OrdenArea.seg_acumulados >= limite_advertencia,
                OrdenArea.seg_acumulados < settings.SLA_SEG
            )
        ).scalar()
        
        # Áreas que superaron SLA (vencidas)
        vencidas = db.query(func.count(OrdenArea.id)).filter(
            OrdenArea.estado_parcial == settings.ESTADO_TIMEOUT
        ).scalar()
        
        # Promedio de segundos acumulados en áreas activas
        promedio_seg = db.query(func.avg(OrdenArea.seg_acumulados)).filter(
            OrdenArea.estado_parcial.in_(['EN_PROGRESO', 'PENDIENTE'])
        ).scalar() or 0
        
        return {
            "sla_segundos": settings.SLA_SEG,
            "total_areas_activas": total_activas,
            "areas_cerca_limite": cerca_limite,
            "areas_vencidas": vencidas,
            "promedio_segundos": round(promedio_seg, 2),
            "porcentaje_cumplimiento": round(
                ((total_activas - vencidas) / total_activas * 100) if total_activas > 0 else 100,
                2
            )
        }