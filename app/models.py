from pydantic import BaseModel, Field, field_validator
from typing import Literal, Annotated
from datetime import datetime

class GPS(BaseModel):
    lat: Annotated[float, Field(ge=-90, le=90)]
    lon: Annotated[float, Field(ge=-180, le=180)]

class Telemetry(BaseModel):
    vehicle_id: str
    ts: str  # ISO8601 string
    speed_kmh: float
    temperature_c: float
    battery_pct: Annotated[int, Field(ge=0, le=100)]
    range_km: float
    odometer_km: float
    gps: GPS
    smoke_detected: bool
    status: Literal["moving", "stopped"]

    @field_validator("ts")
    @classmethod
    def validate_ts(cls, v: str) -> str:
        try:
            # Normalizamos reemplazando 'Z' por UTC offset
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except Exception:
            raise ValueError("Invalid ISO8601 timestamp")
        return v
