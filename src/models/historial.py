"""
Modelo: Historial de eventos
"""
from sqlalchemy import Column, Integer, String, Text, Enum, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database import Base


class Historial(Base):
    __tablename__ = "historial"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    orden_id = Column(Integer, ForeignKey("ordenes.id", ondelete="CASCADE"), nullable=False)
    
    evento = Column(String(100), nullable=False)
    detalle = Column(Text)
    
    estado_global = Column(
        Enum(
            'NUEVA', 'ASIGNADA', 'EN_PROGRESO', 'PENDIENTE', 
            'COMPLETADA', 'CERRADA_SIN_SOLUCION', 'VENCIDA',
            name='estado_enum'
        )
    )
    
    timestamp = Column(TIMESTAMP, server_default=func.now())
    actor = Column(String(150))
    
    # Relaciones
    orden = relationship("Orden", back_populates="historial")
    
    def __repr__(self):
        return f"<Historial(orden_id={self.orden_id}, evento='{self.evento}')>"