from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import init_db
from app.mqtt_client import start_mqtt

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    start_mqtt()
    yield
    # Shutdown (si quieres cerrar conexiones o limpiar cosas)
    print("[APP] Shutting down...")

app = FastAPI(title="Vehicle Telemetry Service", lifespan=lifespan)

@app.get("/")
def root():
    return {"status": "running", "message": "Telemetry service is active (Task 1)"}
