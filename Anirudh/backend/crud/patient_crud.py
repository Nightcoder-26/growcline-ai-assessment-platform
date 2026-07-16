from sqlalchemy.orm import Session
from sqlalchemy import or_
from models import Patient
from schemas.patient_schema import PatientCreate, PatientUpdate

def get_patient_by_id(db: Session, patient_id: int):
    return db.query(Patient).filter(Patient.id == patient_id).first()

def get_patients(db: Session, skip: int = 0, limit: int = 100, search: str = None):
    query = db.query(Patient)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Patient.first_name.ilike(search_filter),
                Patient.last_name.ilike(search_filter),
                Patient.email.ilike(search_filter),
                Patient.phone.ilike(search_filter)
            )
        )
    return query.offset(skip).limit(limit).all()

def create_patient(db: Session, patient_in: PatientCreate):
    db_patient = Patient(**patient_in.model_dump())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def update_patient(db: Session, patient_id: int, patient_in: PatientUpdate):
    db_patient = get_patient_by_id(db, patient_id)
    if not db_patient:
        return None
    
    update_data = patient_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_patient, field, value)
        
    db.commit()
    db.refresh(db_patient)
    return db_patient

def delete_patient(db: Session, patient_id: int):
    db_patient = get_patient_by_id(db, patient_id)
    if not db_patient:
        return None
    db.delete(db_patient)
    db.commit()
    return db_patient
