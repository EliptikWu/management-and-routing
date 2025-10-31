"""
Servicio: Lógica para recalcular estados globales
"""
from sqlalchemy.orm import Session
from src.models import Orden, OrdenArea, Historial


class EstadoService:
    
    @staticmethod
    def recalcular_estado_global(db: Session, orden: Orden) -> str:
        """
        Recalcula el estado global de una orden según sus asignaciones
        
        Reglas:
        - Si no hay asignaciones: NUEVA
        - Si todas COMPLETADA: COMPLETADA
        - Si alguna CERRADA_SIN_SOLUCION y ninguna EN_PROGRESO: CERRADA_SIN_SOLUCION
        - Si alguna VENCIDA: VENCIDA
        - Si alguna EN_PROGRESO: EN_PROGRESO
        - Si alguna PENDIENTE: PENDIENTE
        - Si todas ASIGNADA: ASIGNADA
        """
        asignaciones = orden.asignaciones
        
        if not asignaciones:
            nuevo_estado = 'NUEVA'
        else:
            estados = [a.estado_parcial for a in asignaciones]
            
            # Verificar reglas en orden de prioridad
            if all(e == 'COMPLETADA' for e in estados):
                nuevo_estado = 'COMPLETADA'
            elif 'VENCIDA' in estados:
                nuevo_estado = 'VENCIDA'
            elif 'EN_PROGRESO' in estados:
                nuevo_estado = 'EN_PROGRESO'
            elif 'PENDIENTE' in estados:
                nuevo_estado = 'PENDIENTE'
            elif any(e == 'CERRADA_SIN_SOLUCION' for e in estados) and 'EN_PROGRESO' not in estados:
                nuevo_estado = 'CERRADA_SIN_SOLUCION'
            elif all(e == 'ASIGNADA' for e in estados):
                nuevo_estado = 'ASIGNADA'
            else:
                nuevo_estado = 'PENDIENTE'  # Estado por defecto para casos mixtos
        
        # Solo actualizar si cambió
        if orden.estado_global != nuevo_estado:
            estado_anterior = orden.estado_global
            orden.estado_global = nuevo_estado
            
            # Registrar en historial
            historial = Historial(
                orden_id=orden.id,
                evento='CAMBIO_ESTADO_GLOBAL',
                detalle=f'Estado global: {estado_anterior} → {nuevo_estado}',
                estado_global=nuevo_estado,
                actor='SISTEMA'
            )
            db.add(historial)
        
        return nuevo_estado