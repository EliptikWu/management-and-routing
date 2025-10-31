"""
Routers de la API
"""
from src.routers.ordenes import router as ordenes_router
from src.routers.areas import router as areas_router

__all__ = ["ordenes_router", "areas_router"]