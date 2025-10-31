"""
Modelo: Áreas o departamentos
"""
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database import Base


class Area(Base):
    __tablename__ = "areas"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True)
    responsable = Column(String(150), nullable=False)
    contacto = Column(String(100))
    activo = Column(Boolean, default=True)
    creada_en = Column(TIMESTAMP, server_default=func.now())
    
    # Relaciones
    asignaciones = relationship("OrdenArea", back_populates="area")
    
    def __repr__(self):
        return f"<Area(id={self.id}, nombre='{self.nombre}')>"