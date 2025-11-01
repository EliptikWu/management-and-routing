"""
Configuración compartida para pruebas
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.config import settings
from src.database import Base

# Usar la base de datos real (no SQLite) para pruebas de integración
engine = create_engine(settings.database_url)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Session:
    """
    Fixture que provee una sesión de base de datos para pruebas
    Usa la base de datos real con seed data
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def clean_test_orden(db: Session):
    """
    Crea una orden de prueba limpia y la elimina después
    """
    from src.models import Orden, OrdenArea, Historial
    
    # Crear orden de prueba
    orden = Orden(
        titulo="TEST - Orden para pruebas automáticas",
        descripcion="Orden creada automáticamente por el sistema de pruebas",
        creador="test_automation@pytest.com",
        estado_global="NUEVA",
        prioridad="MEDIA"
    )
    db.add(orden)
    db.commit()
    db.refresh(orden)
    
    yield orden
    
    # Limpieza: eliminar orden y datos relacionados
    db.query(Historial).filter(Historial.orden_id == orden.id).delete()
    db.query(OrdenArea).filter(OrdenArea.orden_id == orden.id).delete()
    db.query(Orden).filter(Orden.id == orden.id).delete()
    db.commit()