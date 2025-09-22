import pytest
from app.models import Telemetry, GPS
from datetime import datetime
from pydantic import ValidationError

# --------- Datos de prueba ---------
valid_payload = {
    "vehicle_id": "veh-001",
    "ts": "2025-09-18T10:15:30Z",
    "speed_kmh": 42.7,
    "temperature_c": 68.3,
    "battery_pct": 55,
    "range_km": 110.0,
    "odometer_km": 12345.6,
    "gps": {"lat": 40.4168, "lon": -3.7038},
    "smoke_detected": False,
    "status": "moving"
}

invalid_payloads = [
    {**valid_payload, "battery_pct": -5},      # battery_pct fuera de rango
    {**valid_payload, "gps": {"lat": 100, "lon": 0}},  # lat fuera de rango
    {**valid_payload, "ts": "invalid-timestamp"}       # timestamp inválido
]

# --------- Tests ---------

def test_valid_telemetry():
    t = Telemetry(**valid_payload)
    assert t.vehicle_id == "veh-001"
    assert t.gps.lat == 40.4168
    assert t.gps.lon == -3.7038

@pytest.mark.parametrize("payload", invalid_payloads)
def test_invalid_telemetry(payload):
    with pytest.raises(Exception):
        Telemetry(**payload)

def test_timestamp_parsing():
    t = Telemetry(**valid_payload)
    # Verificamos que se pueda parsear ISO8601
    dt = datetime.fromisoformat(t.ts.replace("Z", "+00:00"))
    assert dt.year == 2025
