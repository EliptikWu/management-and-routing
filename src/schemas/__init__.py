"""
Schemas de validación (Pydantic)
"""
from src.schemas.area import AreaBase, AreaCreate, AreaResponse
from src.schemas.orden import (
    OrdenBase, OrdenCreate, OrdenResponse, OrdenListResponse,
    OrdenAreaBase, OrdenAreaResponse, AsignacionCreate, CambioEstadoRequest
)
from src.schemas.historial import HistorialResponse

__all__ = [
    "AreaBase", "AreaCreate", "AreaResponse",
    "OrdenBase", "OrdenCreate", "OrdenResponse", "OrdenListResponse",
    "OrdenAreaBase", "OrdenAreaResponse", "AsignacionCreate", "CambioEstadoRequest",
    "HistorialResponse"
]