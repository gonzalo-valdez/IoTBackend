from contextlib import asynccontextmanager
from app.database import init_db
from app.mqtt_client import start_mqtt
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from app.models import Telemetry
from app.repository import save_telemetry, get_latest_telemetry, get_telemetry_window
from datetime import datetime, timezone, timedelta
import pandas as pd
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    start_mqtt()
    yield
    # Shutdown (si quieres cerrar conexiones o limpiar cosas)
    print("[APP] Shutting down...")

app = FastAPI(title="Vehicle Telemetry Service", lifespan=lifespan)

# -----------------------
# POST /ingest
# -----------------------
@app.post("/ingest")
def ingest_telemetry(payload: Telemetry):
    try:
        save_telemetry(payload.model_dump()) 
        return JSONResponse(status_code=201, content={"saved": True})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# -----------------------
# GET /vehicles/{vehicle_id}/latest
# -----------------------
@app.get("/vehicles/{vehicle_id}/latest")
def latest_telemetry(vehicle_id: str):
    data = get_latest_telemetry(vehicle_id)
    if not data:
        raise HTTPException(status_code=404, detail="No telemetry found")
    return data

# -----------------------
# GET /vehicles/{vehicle_id}/stats?minutes=60
# -----------------------
@app.get("/vehicles/{vehicle_id}/stats")
def telemetry_stats(vehicle_id: str, minutes: int = 60):
    window_start = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    records = get_telemetry_window(vehicle_id, window_start)
    if not records:
        raise HTTPException(status_code=404, detail="No telemetry in window")
    
    df = pd.DataFrame(records)
    stats = {}
    for var in ["speed_kmh", "temperature_c", "battery_pct"]:
        stats[var] = {
            "min": df[var].min(),
            "max": df[var].max(),
            "avg": df[var].mean()
        }
    
    return {
        "window_start": window_start.isoformat() + "Z",
        "window_end": (datetime.now(timezone.utc) - timedelta(minutes=minutes)).isoformat() + "Z",
        "count": len(records),
        "stats": stats
    }