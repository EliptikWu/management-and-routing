"""
Aplicación principal FastAPI
Sistema de Enrutamiento de Órdenes Multiárea
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import func
from contextlib import asynccontextmanager

from src.config import settings
from src.routers import ordenes_router, areas_router
from src.routers.temporizador import router as temporizador_router
from src.database import SessionLocal
from src.models import Orden
from src.scheduler import temporizador_scheduler


# Lifespan para iniciar/detener el scheduler
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Maneja el ciclo de vida de la aplicación"""
    # Startup: Iniciar temporizador
    print("🚀 Iniciando aplicación...")
    temporizador_scheduler.iniciar()
    
    yield
    
    # Shutdown: Detener temporizador
    print("⏹️  Deteniendo aplicación...")
    temporizador_scheduler.detener()


# Crear aplicación con lifespan
app = FastAPI(
    title="Sistema de Enrutamiento de Órdenes Multiárea",
    description="MVP para gestión de órdenes con asignación multiárea y temporizador SLA",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# Registrar routers
app.include_router(ordenes_router)
app.include_router(areas_router)
app.include_router(temporizador_router)


@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Enrutador de Órdenes Multiárea",
        "version": "1.0.0",
        "docs": "/docs",
        "frontend": "/app",
        "temporizador": "activo"
    }


@app.get("/app", tags=["Frontend"])
def frontend():
    """Sirve la aplicación frontend"""
    return FileResponse("src/static/index.html")


@app.get("/kpis", tags=["KPIs"])
def obtener_kpis():
    """
    KPIs básicos del sistema
    
    Retorna:
    - total_ordenes: Total de órdenes en el sistema
    - completadas: Órdenes con estado COMPLETADA
    - pendientes: Órdenes en estados PENDIENTE, EN_PROGRESO o ASIGNADA
    - cerradas_sin_solucion: Órdenes cerradas sin resolver
    """
    db = SessionLocal()
    try:
        total = db.query(func.count(Orden.id)).scalar() or 0
        
        completadas = db.query(func.count(Orden.id)).filter(
            Orden.estado_global == 'COMPLETADA'
        ).scalar() or 0
        
        pendientes = db.query(func.count(Orden.id)).filter(
            Orden.estado_global.in_(['PENDIENTE', 'EN_PROGRESO', 'ASIGNADA', 'NUEVA'])
        ).scalar() or 0
        
        sin_solucion = db.query(func.count(Orden.id)).filter(
            Orden.estado_global == 'CERRADA_SIN_SOLUCION'
        ).scalar() or 0
        
        vencidas = db.query(func.count(Orden.id)).filter(
            Orden.estado_global == 'VENCIDA'
        ).scalar() or 0
        
        return {
            "total_ordenes": total,
            "completadas": completadas,
            "pendientes": pendientes,
            "cerradas_sin_solucion": sin_solucion,
            "vencidas": vencidas
        }
    except Exception as e:
        return {
            "total_ordenes": 0,
            "completadas": 0,
            "pendientes": 0,
            "cerradas_sin_solucion": 0,
            "vencidas": 0,
            "error": str(e)
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