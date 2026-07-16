import os
import sys

# Configure pycache prefix to redirect all compiled bytecode (.pyc) to a single main __pycache__ directory.
# This prevents __pycache__ folders from being created inside sub-directories.
main_dir = os.path.dirname(os.path.abspath(__file__))
pycache_dir = os.path.join(main_dir, "__pycache__")
sys.pycache_prefix = pycache_dir
os.environ["PYTHONPYCACHEPREFIX"] = pycache_dir

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Import database and models to create tables
from config.database import engine, Base
import models

# Import routes
from routes.patient_routes import router as patient_router

# Load env variables
load_dotenv()

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Patient Management System API",
    description="Backend API for managing patient data",
    version="1.0.0"
)

# CORS Configuration (allows frontend connection)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(patient_router)

@app.get("/")
def root():
    return {
        "status": "online",
        "message": "Patient Management API is running.",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

from fastapi.openapi.utils import get_openapi
from config.database import SessionLocal
from models import Patient

def custom_openapi():
    # Query the database for the last registered patient to use as an example in Swagger
    db = SessionLocal()
    last_patient = None
    try:
        last_patient = db.query(Patient).order_by(Patient.id.desc()).first()
    except Exception as e:
        print(f"Error querying last patient for Swagger example: {e}")
    finally:
        db.close()

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    if last_patient and "components" in openapi_schema and "schemas" in openapi_schema["components"]:
        patient_update_schema = openapi_schema["components"]["schemas"].get("PatientUpdate")
        if patient_update_schema:
            patient_update_schema["example"] = {
                "first_name": last_patient.first_name,
                "last_name": last_patient.last_name,
                "date_of_birth": last_patient.date_of_birth,
                "gender": last_patient.gender,
                "email": last_patient.email,
                "phone": last_patient.phone,
                "address": last_patient.address,
                "medical_history": last_patient.medical_history
            }

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    print(f"Starting server at http://{host}:{port}")
    uvicorn.run("app:app", host=host, port=port, reload=True)
