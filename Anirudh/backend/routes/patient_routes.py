from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.database import get_db
from models import Patient
from schemas.patient_schema import PatientCreate, PatientUpdate, PatientResponse
from crud import patient_crud

router = APIRouter(prefix="/patients", tags=["Patients"])

@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(patient_in: PatientCreate, db: Session = Depends(get_db)):
    # Check email uniqueness
    if patient_in.email:
        existing = db.query(Patient).filter(Patient.email == patient_in.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Patient with this email already exists."
            )
    return patient_crud.create_patient(db, patient_in)

@router.get("/", response_model=List[PatientResponse])
def read_patients(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return patient_crud.get_patients(db, skip=skip, limit=limit, search=search)

@router.get("/{patient_id}", response_model=PatientResponse)
def read_patient(patient_id: int, db: Session = Depends(get_db)):
    db_patient = patient_crud.get_patient_by_id(db, patient_id)
    if not db_patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found."
        )
    return db_patient

@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(patient_id: int, patient_in: PatientUpdate, db: Session = Depends(get_db)):
    # Check email uniqueness if email is being updated
    if patient_in.email:
        existing = db.query(Patient).filter(Patient.email == patient_in.email, Patient.id != patient_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Patient with this email already exists."
            )
            
    db_patient = patient_crud.update_patient(db, patient_id, patient_in)
    if not db_patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found."
        )
    return db_patient

@router.delete("/{patient_id}", response_model=PatientResponse)
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    db_patient = patient_crud.delete_patient(db, patient_id)
    if not db_patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found."
        )
    return db_patient
