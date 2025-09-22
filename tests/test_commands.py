import pytest
from unittest.mock import patch

def test_send_command_success(client):
    vid = "veh-test-cmd"
    payload = {"command": "start"}

    # Ajusta la ruta según donde tu endpoint importe publish_command
    with patch("app.main.publish_command") as mock_publish:
        response = client.post(f"/vehicles/{vid}/commands", json=payload)

    assert response.status_code == 202
    assert response.json() == {"published": True}
    mock_publish.assert_called_once_with(vid, "start")


def test_send_command_invalid(client):
    vid = "veh-test-cmd-invalid"
    payload = {"command": "invalid_command"}

    response = client.post(f"/vehicles/{vid}/commands", json=payload)
    assert response.status_code == 422
    assert "invalid_command" in response.text
