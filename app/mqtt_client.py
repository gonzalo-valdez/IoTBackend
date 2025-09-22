import os
import json
import paho.mqtt.client as mqtt
from app.models import Telemetry
from app.repository import save_telemetry

# Broker público para pruebas
MQTT_HOST = os.getenv("MQTT_HOST", "test.mosquitto.org")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

def handle_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        telemetry = Telemetry(**payload)  # valida con Pydantic
        save_telemetry(telemetry.model_dump())
        print(f"[OK] Guardado telemetría: {telemetry.vehicle_id}")
    except Exception as e:
        print(f"[ERROR] Telemetría inválida: {e}")

def start_mqtt():
    client = mqtt.Client()
    client.on_message = handle_message
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    client.subscribe("vehicles/+/telemetry", qos=1)
    client.loop_start()
    print(f"[MQTT] Subscrito a vehicles/+/telemetry en {MQTT_HOST}:{MQTT_PORT}")
