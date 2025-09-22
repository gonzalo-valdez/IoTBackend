# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import repository

# -----------------------
# Fixture: TestClient global
# -----------------------
@pytest.fixture(scope="session")
def client():
    return TestClient(app)

# -----------------------
# Helper para limpiar solo los datos de un vehicle_id
# -----------------------
@pytest.fixture
def clear_vehicle_data():
    def _clear(vehicle_id):
        conn = repository.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM telemetry WHERE vehicle_id=?", (vehicle_id,))
        conn.commit()
        conn.close()
    return _clear
