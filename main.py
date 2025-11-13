from fastapi import FastAPI, Depends, HTTPException, Path, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import text
from typing import Optional, List
import pandas as pd
from io import StringIO
from db import get_db

# --- DEFINE APP ONLY ONCE HERE ---
app = FastAPI(title="Dynamic Patient Check-in Dashboard API")

@app.get("/")
def root():
    return {"message": "Hello, Dynamic FastAPI Dashboard!"}

@app.get("/api/analytics/dashboard")
def dashboard_metrics(db=Depends(get_db)):
    metrics = {}
    try:
        # Get all table names in 'public' schema
        result = db.execute(text(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='public';"
        ))
        tables = [row[0] for row in result]

        for table in tables:
            # Count total rows in table
            total_query = f"SELECT COUNT(*) FROM {table};"
            metrics[f"{table}_total"] = db.execute(text(total_query)).scalar()

            # Detect date/timestamp columns to count today's rows
            col_query = f"""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = '{table}'
              AND data_type IN ('date','timestamp without time zone','timestamp with time zone');
            """
            cols_result = db.execute(text(col_query))
            timestamp_cols = [row[0] for row in cols_result]

            # If any timestamp/date columns exist, pick the first one for 'today' metric
            if timestamp_cols:
                col = timestamp_cols[0]
                today_query = f"SELECT COUNT(*) FROM {table} WHERE DATE({col}) = CURRENT_DATE;"
                metrics[f"{table}_today"] = db.execute(text(today_query)).scalar()

    except Exception as e:
        return {"error": str(e)}

    return metrics

@app.get("/api/appointments/list")
def list_appointments(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    db=Depends(get_db)
):
    """
    Returns a paginated list of appointments (visits) with optional filters.
    """
    try:
        filters = []
        params = {}

        if patient_id:
            filters.append("patient_id = :patient_id")
            params["patient_id"] = patient_id
        if doctor_id:
            filters.append("doctor_id = :doctor_id")
            params["doctor_id"] = doctor_id

        where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""

        # Count total matching rows
        count_query = f"SELECT COUNT(*) FROM visits {where_clause};"
        total = db.execute(text(count_query), params).scalar()

        # Pagination
        offset = (page - 1) * page_size
        query = f"""
            SELECT * FROM visits
            {where_clause}
            ORDER BY visit_id DESC
            LIMIT :limit OFFSET :offset;
        """
        params["limit"] = page_size
        params["offset"] = offset

        result = db.execute(text(query), params).fetchall()

        # Convert rows to dicts
        appointments = [dict(row._mapping) for row in result]

        return {
            "page": page,
            "page_size": page_size,
            "total": total,
            "appointments": appointments
        }

    except Exception as e:
        return {"error": str(e)}
   
@app.get("/api/analytics/export")
def export_table_csv(
    table: str = Query(..., description="new_table"),
    date_column: Optional[str] = Query(None, description="Optional date column to filter today"),
    db=Depends(get_db)
):
    try:
        # Validate table exists
        tables_result = db.execute(text(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='public';"
        ))
        tables = [row[0] for row in tables_result]
        if table not in tables:
            return {"error": f"Table '{table}' does not exist."}

        # Build query
        query_str = f"SELECT * FROM {table}"
        params = {}
        if date_column:
            query_str += f" WHERE DATE({date_column}) = CURRENT_DATE"

        query_str += ";"

        # Execute query
        result = db.execute(text(query_str)).fetchall()
        if not result:
            return {"error": "No data found."}

        # Convert to DataFrame
        df = pd.DataFrame([dict(row._mapping) for row in result])

        # Convert to CSV in-memory
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)

        return StreamingResponse(
            csv_buffer,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={table}.csv"}
        )

    except Exception as e:
        return {"error": str(e)}

# --- REMOVED DUPLICATE app DEFINITION HERE ---

@app.get("/api/clinicians/overview")
def clinicians_overview(db=Depends(get_db)):
    """
    Returns statistics for all clinicians
    """
    try:
        result = db.execute(text("""
            SELECT d.doctor_id,
                   d.first_name,
                   d.last_name,
                   COUNT(v.visit_id) AS total_visits,
                   COUNT(qt.ticket_id) AS total_queue_tickets
            FROM doctors d
            LEFT JOIN visits v ON d.doctor_id = v.doctor_id
            LEFT JOIN queue_tickets qt ON v.visit_id = qt.visit_id
            GROUP BY d.doctor_id, d.first_name, d.last_name;
        """))
        clinicians = [dict(row._mapping) for row in result] 
        return {"clinicians": clinicians}
    except Exception as e:
        return {"error": str(e)}
   

@app.patch("/api/appointment/{appointment_id}/override")
def override_appointment_queue(
    appointment_id: int = Path(..., description="ID of the appointment to override"),
    new_status: str = "PRIORITY",
    db=Depends(get_db)
):
    """
    Admin can override the queue status of an appointment.
    """
    try:
        # Check if appointment exists
        result = db.execute(text(
            "SELECT ticket_id, queue_status FROM queue_tickets WHERE visit_id = :visit_id"
        ), {"visit_id": appointment_id}).fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Appointment not found")

        # Update the queue status
        db.execute(text(
            "UPDATE queue_tickets SET queue_status = :status WHERE visit_id = :visit_id"
        ), {"status": new_status, "visit_id": appointment_id})

        db.commit()
        return {"message": f"Appointment {appointment_id} queue status overridden to '{new_status}'"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))