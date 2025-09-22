from unittest.mock import patch, MagicMock
from app.mqtt_client import handle_message
import json

def test_handle_message_calls_save():
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
    msg = MagicMock()
    msg.payload = json.dumps(payload).encode("utf-8")

    with patch("app.mqtt_client.save_telemetry") as mock_save:
        handle_message(None, None, msg)
        mock_save.assert_called_once()
