from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import expenses

app = FastAPI(
    title="Expense Tracker API",
    description="A simple expense tracker",
    version="1.0.0"
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the expenses route directly
app.include_router(expenses.router, prefix="/api/v1")

@app.get("/", tags=["health"])
async def health_check():
    return {"message": "Welcome to the Expense Tracker API!"}

