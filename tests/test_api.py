# tests/test_api.py
import pytest
from datetime import datetime, timedelta, timezone
from app import repository

# -----------------------
# Payload de ejemplo
# -----------------------
def make_payload(vehicle_id, ts=None):
    if ts is None:
        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        "vehicle_id": vehicle_id,
        "ts": ts,
        "speed_kmh": 42.7,
        "temperature_c": 68.3,
        "battery_pct": 55,
        "range_km": 110.0,
        "odometer_km": 12345.6,
        "gps": {"lat": 40.4168, "lon": -3.7038},
        "smoke_detected": False,
        "status": "moving"
    }

# -----------------------
# POST /ingest
# -----------------------
def test_post_ingest(client, clear_vehicle_data):
    vid = "veh-test-ingest"
    clear_vehicle_data(vid)
    payload = make_payload(vid)
    response = client.post("/ingest", json=payload)
    assert response.status_code == 201
    assert response.json() == {"saved": True}

# -----------------------
# GET /vehicles/{vehicle_id}/latest
# -----------------------
def test_get_latest(client, clear_vehicle_data):
    vid = "veh-test-latest"
    clear_vehicle_data(vid)
    payload = make_payload(vid)
    repository.save_telemetry(payload)
    
    response = client.get(f"/vehicles/{vid}/latest")
    assert response.status_code == 200
    data = response.json()
    assert data["vehicle_id"] == vid
    assert data["ts"] == payload["ts"]

# -----------------------
# GET /vehicles/{vehicle_id}/stats
# -----------------------
def test_get_stats(client, clear_vehicle_data):
    vid = "veh-test-stats"
    clear_vehicle_data(vid)
    
    now = datetime.now(timezone.utc)
    payload1 = make_payload(vid, now.isoformat().replace("+00:00", "Z"))
    payload2 = make_payload(vid, (now - timedelta(minutes=1)).isoformat().replace("+00:00", "Z"))
    payload2["speed_kmh"] = 60
    payload2["temperature_c"] = 70
    payload2["battery_pct"] = 80

    repository.save_telemetry(payload1)
    repository.save_telemetry(payload2)

    response = client.get(f"/vehicles/{vid}/stats?minutes=5")
    assert response.status_code == 200
    stats = response.json()["stats"]

    assert stats["speed_kmh"]["min"] == 42.7
    assert stats["speed_kmh"]["max"] == 60
    assert stats["temperature_c"]["min"] == 68.3
    assert stats["temperature_c"]["max"] == 70
    assert stats["battery_pct"]["min"] == 55
    assert stats["battery_pct"]["max"] == 80

# -----------------------
# GET /vehicles/{vehicle_id}/latest para vehículo sin datos
# -----------------------
def test_get_latest_no_data(client):
    vid = "veh-test-nodata"
    response = client.get(f"/vehicles/{vid}/latest")
    assert response.status_code == 404
    assert response.json() == {"detail": "No telemetry found"}
