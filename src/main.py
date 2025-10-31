"""
Aplicación principal FastAPI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.routers import ordenes_router, areas_router

# Crear aplicación
app = FastAPI(
    title="Sistema de Enrutamiento de Órdenes Multiárea",
    description="MVP para gestión de órdenes con asignación multiárea y temporizador SLA",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(ordenes_router)
app.include_router(areas_router)


@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Enrutador de Órdenes Multiárea",
        "version": "1.0.0"
    }


@app.get("/kpis", tags=["KPIs"])
def obtener_kpis():
    """
    KPIs básicos del sistema
    
    TODO: Implementar con queries agregadas
    """
    from src.database import SessionLocal
    from src.models import Orden
    from sqlalchemy import func
    
    db = SessionLocal()
    try:
        total = db.query(func.count(Orden.id)).scalar()
        completadas = db.query(func.count(Orden.id)).filter(
            Orden.estado_global == 'COMPLETADA'
        ).scalar()
        pendientes = db.query(func.count(Orden.id)).filter(
            Orden.estado_global.in_(['PENDIENTE', 'EN_PROGRESO', 'ASIGNADA'])
        ).scalar()
        sin_solucion = db.query(func.count(Orden.id)).filter(
            Orden.estado_global == 'CERRADA_SIN_SOLUCION'
        ).scalar()
        
        return {
            "total_ordenes": total,
            "completadas": completadas,
            "pendientes": pendientes,
            "cerradas_sin_solucion": sin_solucion
        }
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG_MODE
    )