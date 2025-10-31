"""
Schemas: Historial
"""
from pydantic import BaseModel
from datetime import datetime


class HistorialResponse(BaseModel):
    id: int
    orden_id: int
    evento: str
    detalle: str | None
    estado_global: str | None
    timestamp: datetime
    actor: str | None
    
    class Config:
        from_attributes = True