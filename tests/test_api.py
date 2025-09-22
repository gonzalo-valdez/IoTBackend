import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone
from app.main import app
from app import repository

# -----------------------
# Fixture: DB temporal en memoria
# -----------------------
@pytest.fixture
def temp_db(monkeypatch):
    # Conexión SQLite en memoria
    conn = repository.get_connection(":memory:")
    cursor = conn.cursor()
    # Crear tabla igual que en la DB real
    cursor.execute("""
        CREATE TABLE telemetry (
            vehicle_id TEXT,
            ts TEXT,
            speed_kmh REAL,
            temperature_c REAL,
            battery_pct REAL,
            range_km REAL,
            odometer_km REAL,
            gps_lat REAL,
            gps_lon REAL,
            smoke_detected INTEGER,
            status TEXT
        )
    """)
    conn.commit()

    # Patch de repository.get_connection para que use esta DB temporal
    monkeypatch.setattr(repository, "get_connection", lambda db_path="data.db": conn)

    yield conn  # los tests se ejecutan aquí

    conn.close()  # limpiar después

# -----------------------
# Fixture: TestClient
# -----------------------
@pytest.fixture
def client(temp_db):
    return TestClient(app)

# -----------------------
# Payload de ejemplo
# -----------------------
payload = {
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

# -----------------------
# POST /ingest
# -----------------------
def test_post_ingest(client):
    response = client.post("/ingest", json=payload)
    assert response.status_code == 201
    assert response.json() == {"saved": True}

# -----------------------
# GET /vehicles/{vehicle_id}/latest
# -----------------------
def test_get_latest(client):
    # Guardamos primero para asegurarnos que hay datos
    repository.save_telemetry(payload)
    response = client.get(f"/vehicles/{payload['vehicle_id']}/latest")
    assert response.status_code == 200
    data = response.json()
    assert data["vehicle_id"] == payload["vehicle_id"]
    assert data["ts"] == payload["ts"]

# -----------------------
# GET /vehicles/{vehicle_id}/stats
# -----------------------
def test_get_stats(client):
    now = datetime.now(timezone.utc)

    payload1 = payload.copy()
    payload1["ts"] = now.isoformat().replace("+00:00", "Z")

    payload2 = payload.copy()
    payload2["ts"] = (now - timedelta(minutes=1)).isoformat().replace("+00:00", "Z")
    payload2["speed_kmh"] = 60
    payload2["temperature_c"] = 70
    payload2["battery_pct"] = 80

    repository.save_telemetry(payload1)
    repository.save_telemetry(payload2)

    response = client.get(f"/vehicles/{payload['vehicle_id']}/stats?minutes=5")
    assert response.status_code == 200
    stats = response.json()["stats"]

    # Verificar min/max/avg
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
    response = client.get("/vehicles/nonexistent/latest")
    assert response.status_code == 404
    assert response.json() == {"detail": "No telemetry found"}
