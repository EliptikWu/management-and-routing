"""
Modelos: Órdenes y Asignaciones de Áreas
"""
from sqlalchemy import (
    Column, Integer, String, Text, Enum, TIMESTAMP, ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database import Base


class Orden(Base):
    __tablename__ = "ordenes"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=False)
    creador = Column(String(150), nullable=False)
    
    estado_global = Column(
        Enum(
            'NUEVA', 'ASIGNADA', 'EN_PROGRESO', 'PENDIENTE', 
            'COMPLETADA', 'CERRADA_SIN_SOLUCION', 'VENCIDA',
            name='estado_enum'
        ),
        default='NUEVA',
        nullable=False
    )
    
    prioridad = Column(
        Enum('BAJA', 'MEDIA', 'ALTA', 'CRITICA', name='prioridad_enum'),
        default='MEDIA',
        nullable=False
    )
    
    creada_en = Column(TIMESTAMP, server_default=func.now())
    actualizada_en = Column(
        TIMESTAMP, 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    # Relaciones
    asignaciones = relationship(
        "OrdenArea", 
        back_populates="orden",
        cascade="all, delete-orphan"
    )
    historial = relationship(
        "Historial", 
        back_populates="orden",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Orden(id={self.id}, titulo='{self.titulo}', estado='{self.estado_global}')>"


class OrdenArea(Base):
    __tablename__ = "orden_area"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    orden_id = Column(Integer, ForeignKey("ordenes.id", ondelete="CASCADE"), nullable=False)
    area_id = Column(Integer, ForeignKey("areas.id", ondelete="RESTRICT"), nullable=False)
    
    asignada_a = Column(String(150))
    
    estado_parcial = Column(
        Enum(
            'NUEVA', 'ASIGNADA', 'EN_PROGRESO', 'PENDIENTE', 
            'COMPLETADA', 'CERRADA_SIN_SOLUCION', 'VENCIDA',
            name='estado_enum'
        ),
        default='ASIGNADA',
        nullable=False
    )
    
    seg_acumulados = Column(Integer, default=0)
    
    asignada_en = Column(TIMESTAMP, server_default=func.now())
    iniciada_en = Column(TIMESTAMP)
    pausada_en = Column(TIMESTAMP)
    completada_en = Column(TIMESTAMP)
    
    notas = Column(Text)
    
    # Relaciones
    orden = relationship("Orden", back_populates="asignaciones")
    area = relationship("Area", back_populates="asignaciones")
    
    def __repr__(self):
        return f"<OrdenArea(orden_id={self.orden_id}, area_id={self.area_id}, estado='{self.estado_parcial}')>"