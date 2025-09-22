from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.responses import JSONResponse
from datetime import datetime, timezone, timedelta
import pandas as pd
from typing import List

from app.database import init_db
from app.mqtt_client import start_mqtt, publish_command
from app.models import Telemetry, CommandPayload
from app import repository


# -----------------------
# Lifespan
# -----------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    start_mqtt()
    yield
    print("[APP] Shutting down...")


app = FastAPI(
    title="Vehicle Telemetry Service",
    description="API para ingestión, consulta y análisis de telemetría de vehículos, "
                "incluyendo detección de anomalías y envío de comandos vía MQTT.",
    version="1.0.0",
    lifespan=lifespan
)


# -----------------------
# POST /ingest
# -----------------------
@app.post(
    "/ingest",
    summary="Ingesta de telemetría",
    description="Recibe un payload de telemetría de un vehículo y lo guarda en la base de datos.",
    response_description="Confirmación de guardado",
    status_code=201
)
def ingest_telemetry(payload: Telemetry):
    try:
        repository.save_telemetry(payload.model_dump())
        return JSONResponse(status_code=201, content={"saved": True})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# -----------------------
# GET /vehicles/{vehicle_id}/latest
# -----------------------
@app.get(
    "/vehicles/{vehicle_id}/latest",
    summary="Última telemetría",
    description="Devuelve el último registro de telemetría disponible para un vehículo.",
    response_model=Telemetry,
    response_description="Último registro de telemetría"
)
def latest_telemetry(vehicle_id: str = Path(..., description="ID del vehículo")):
    data = repository.get_latest_telemetry(vehicle_id)
    if not data:
        raise HTTPException(status_code=404, detail="No telemetry found")
    return data


# -----------------------
# GET /vehicles/{vehicle_id}/stats
# -----------------------
@app.get(
    "/vehicles/{vehicle_id}/stats",
    summary="Estadísticas de telemetría",
    description="Devuelve estadísticas (min, max, avg) de speed_kmh, temperature_c y battery_pct "
                "para un vehículo en una ventana de tiempo.",
)
def telemetry_stats(
    vehicle_id: str = Path(..., description="ID del vehículo"),
    minutes: int = Query(60, gt=0, description="Ventana de tiempo en minutos para calcular estadísticas")
):
    window_start = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    window_end = datetime.now(timezone.utc)
    records = repository.get_telemetry_window(vehicle_id, window_start)
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
        "window_end": window_end.isoformat() + "Z",
        "count": len(records),
        "stats": stats
    }


# -----------------------
# POST /vehicles/{vehicle_id}/commands
# -----------------------
@app.post(
    "/vehicles/{vehicle_id}/commands",
    summary="Enviar comando a vehículo",
    description="Publica un comando MQTT al vehículo indicado.",
    status_code=202,
    response_description="Indica si se publicó correctamente el comando"
)
async def send_command(
    vehicle_id: str = Path(..., description="ID del vehículo"),
    payload: CommandPayload = None
):
    publish_command(vehicle_id, payload.command)
    return {"published": True}


# -----------------------
# GET /vehicles/{vehicle_id}/anomalies
# -----------------------
@app.get(
    "/vehicles/{vehicle_id}/anomalies",
    summary="Detección de anomalías",
    description="Devuelve los registros anómalos de telemetría de un vehículo en los últimos X minutos "
                "utilizando z-score robusto.",
)
def telemetry_anomalies(
    vehicle_id: str = Path(..., description="ID del vehículo"),
    minutes: int = Query(60, gt=0, description="Ventana de tiempo en minutos para analizar anomalías")
):
    window_start = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    window = repository.get_telemetry_window(vehicle_id, window_start)
    if not window:
        raise HTTPException(status_code=404, detail="No telemetry found")

    anomalies = repository.detect_anomalies_window_with_reason(window)
    return {"vehicle_id": vehicle_id, "anomalies": anomalies}
