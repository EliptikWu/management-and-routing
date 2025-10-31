"""
Schemas: Áreas
"""
from pydantic import BaseModel, Field
from datetime import datetime


class AreaBase(BaseModel):
    nombre: str = Field(..., max_length=100, description="Nombre del área")
    responsable: str = Field(..., max_length=150, description="Responsable del área")
    contacto: str | None = Field(None, max_length=100, description="Email o teléfono")


class AreaCreate(AreaBase):
    pass


class AreaResponse(AreaBase):
    id: int
    activo: bool
    creada_en: datetime
    
    class Config:
        from_attributes = True