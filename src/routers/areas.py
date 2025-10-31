"""
Router: Endpoints de áreas (CRUD básico)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from src.database import get_db
from src.schemas.area import AreaCreate, AreaResponse
from src.models import Area

router = APIRouter(prefix="/areas", tags=["Áreas"])


@router.get("/", response_model=List[AreaResponse])
def listar_areas(
    activo: bool = True,
    db: Session = Depends(get_db)
):
    """Lista todas las áreas activas"""
    areas = db.query(Area).filter(Area.activo == activo).all()
    return areas


@router.get("/{area_id}", response_model=AreaResponse)
def obtener_area(area_id: int, db: Session = Depends(get_db)):
    """Obtiene una área por ID"""
    area = db.query(Area).filter(Area.id == area_id).first()
    if not area:
        raise HTTPException(status_code=404, detail=f"Área {area_id} no encontrada")
    return area


@router.post("/", response_model=AreaResponse, status_code=201)
def crear_area(area_data: AreaCreate, db: Session = Depends(get_db)):
    """Crea una nueva área"""
    # Verificar nombre único
    existe = db.query(Area).filter(Area.nombre == area_data.nombre).first()
    if existe:
        raise HTTPException(status_code=400, detail=f"Área '{area_data.nombre}' ya existe")
    
    nueva_area = Area(**area_data.dict())
    db.add(nueva_area)
    db.commit()
    db.refresh(nueva_area)
    return nueva_area