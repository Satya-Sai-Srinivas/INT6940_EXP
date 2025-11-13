"""from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import get_db, engine

app = FastAPI()

# Test endpoint to check connection
@app.get("/health")
def check_db_connection(db: Session = Depends(get_db)):
    try:
        # Try to execute a simple query
        result = db.execute(text("SELECT 1"))
        return {"status": "success", "message": "Connected to PostgreSQL database!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Example: Fetch data from a specific table
# Replace 'your_table_name' with an actual table in your DB
@app.get("/items")
def read_items(db: Session = Depends(get_db)):
    # This is raw SQL for simplicity. In a real app, use SQLAlchemy Models.
    try:
        result = db.execute(text("SELECT * FROM admin LIMIT 5"))
        items = [dict(row._mapping) for row in result]
        return items
    except Exception as e:
         return {"error": f"Could not fetch data: {str(e)}"}
    
@app.get("/")
def read_root():
    return {"message": "Hello! The API is running."}"""

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

# Import our new modules
import crud
import models
import schemas
from database import SessionLocal, engine, get_db

# This creates the database tables (if they don't exist)
# based on your definitions in models.py
# --- UNCOMMENT THIS ONCE models.py IS FILLED ---
# models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- NEW ENDPOINT ---
@app.get("/api/clinicians/overview", response_model=List[schemas.ClinicianOverview])
def get_clinicians_overview(db: Session = Depends(get_db)):
    """
    Get an overview of statistics for all clinicians.
    """
    return crud.get_clinicians_overview(db)


# --- OLD ENDPOINTS (for testing) ---

@app.get("/")
def read_root():
    return {"message": "Welcome to the Clinician API. Go to /docs for details."}

@app.get("/health")
def check_db_connection(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "success", "message": "Connected to PostgreSQL database!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/items")
def read_items(db: Session = Depends(get_db)):
    # --- IMPORTANT ---
    # We should move this logic into crud.py,
    # but I'll leave it for now.
    # Replace 'your_table_name' with a real table!
    try:
        result = db.execute(text("SELECT * FROM your_table_name LIMIT 5"))
        items = [dict(row._mapping) for row in result]
        if not items:
             return {"message": "Query successful, but table is empty or name is wrong."}
        return items
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Database error: {e}")