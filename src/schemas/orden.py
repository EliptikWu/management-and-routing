"""
Schemas: Órdenes y Asignaciones
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List


class OrdenBase(BaseModel):
    titulo: str = Field(..., min_length=5, max_length=200, description="Título de la orden")
    descripcion: str = Field(..., min_length=10, description="Descripción detallada")
    prioridad: str = Field("MEDIA", pattern="^(BAJA|MEDIA|ALTA|CRITICA)$")


class OrdenCreate(OrdenBase):
    creador: str = Field(..., max_length=150, description="Usuario que crea la orden")


class OrdenAreaBase(BaseModel):
    area_id: int
    asignada_a: str | None = None
    estado_parcial: str
    seg_acumulados: int
    
    class Config:
        from_attributes = True


class OrdenAreaResponse(OrdenAreaBase):
    id: int
    area_nombre: str | None = None
    asignada_en: datetime
    iniciada_en: datetime | None = None
    completada_en: datetime | None = None


class OrdenResponse(OrdenBase):
    id: int
    creador: str
    estado_global: str
    creada_en: datetime
    actualizada_en: datetime
    asignaciones: List[OrdenAreaResponse] = []
    
    class Config:
        from_attributes = True


class OrdenListResponse(BaseModel):
    id: int
    titulo: str
    estado_global: str
    prioridad: str
    creador: str
    num_areas: int
    areas_completadas: int
    total_segundos: int
    creada_en: datetime
    actualizada_en: datetime


class AsignacionCreate(BaseModel):
    area_ids: List[int] = Field(..., min_length=1, description="Lista de IDs de áreas")
    asignada_a: str | None = Field(None, max_length=150, description="Persona asignada (opcional)")


class CambioEstadoRequest(BaseModel):
    nuevo_estado: str = Field(
        ..., 
        pattern="^(EN_PROGRESO|PENDIENTE|COMPLETADA|CERRADA_SIN_SOLUCION|VENCIDA)$",
        description="Nuevo estado parcial"
    )
    notas: str | None = Field(None, description="Notas adicionales")