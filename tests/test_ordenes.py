"""
Tests básicos para endpoints de órdenes
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.database import Base, get_db
from src.config import settings

# Base de datos de prueba (SQLite en memoria)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Setup
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_crear_orden_exitoso():
    """Test: Crear orden con datos válidos"""
    response = client.post("/ordenes/", json={
        "titulo": "Test - Instalación de software",
        "descripcion": "Instalar Office 365 en equipo del gerente de ventas",
        "creador": "test@empresa.com",
        "prioridad": "MEDIA"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["titulo"] == "Test - Instalación de software"
    assert data["estado_global"] == "NUEVA"
    assert "id" in data


def test_crear_orden_titulo_corto():
    """Test: Validación de título demasiado corto"""
    response = client.post("/ordenes/", json={
        "titulo": "Test",  # < 5 caracteres
        "descripcion": "Descripción válida con más de 10 caracteres",
        "creador": "test@empresa.com"
    })
    
    assert response.status_code == 422  # Validation error


def test_listar_ordenes():
    """Test: Listar órdenes"""
    response = client.get("/ordenes/")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_obtener_orden_inexistente():
    """Test: Obtener orden que no existe"""
    response = client.get("/ordenes/99999")
    
    assert response.status_code == 404
    assert "no encontrada" in response.json()["detail"]


# Ejecutar con: pytest tests/test_ordenes.py -v