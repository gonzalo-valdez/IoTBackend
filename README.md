# Vehicle Telemetry Service

Este proyecto es un servicio backend para ingestión y análisis de telemetría de vehículos. Incluye:

- Almacenamiento en SQLite (`data.db`)
- Ingesta de telemetría vía REST API
- Consulta de telemetría (último registro, estadísticas, anomalías)
- Envío de comandos a vehículos vía MQTT
- Detección simple de anomalías usando z-score robusto

---

## Instalación

1. Clonar el repositorio:

```bash
git clone https://github.com/gonzalo-valdez/IoTBackend.git
cd IoTBackend
```
Instalar dependencias:

```bash
pip install -r requirements.txt
```

Ejecutar la API
```bash
uvicorn app.main:app --reload
```
Por defecto, estará disponible en http://127.0.0.1:8000.

Endpoints principales
POST /ingest
Ingesta de telemetría de un vehículo.

Ejemplo payload:
```json
{
    "vehicle_id": "veh-001",
    "ts": "2025-09-22T10:15:30Z",
    "speed_kmh": 42.7,
    "temperature_c": 68.3,
    "battery_pct": 55,
    "range_km": 110.0,
    "odometer_km": 12345.6,
    "gps": {"lat": 40.4168, "lon": -3.7038},
    "smoke_detected": false,
    "status": "moving"
}
```
Curl de ejemplo:

```bash
curl -X POST http://127.0.0.1:8000/ingest \
-H "Content-Type: application/json" \
-d '{
    "vehicle_id": "veh-001",
    "ts": "2025-09-22T10:15:30Z",
    "speed_kmh": 42.7,
    "temperature_c": 68.3,
    "battery_pct": 55,
    "range_km": 110.0,
    "odometer_km": 12345.6,
    "gps": {"lat": 40.4168, "lon": -3.7038},
    "smoke_detected": false,
    "status": "moving"
}'
```
GET /vehicles/{vehicle_id}/latest
Obtiene la última telemetría de un vehículo.
```bash
curl http://127.0.0.1:8000/vehicles/veh-001/latest
```

GET /vehicles/{vehicle_id}/stats?minutes=60
Obtiene estadísticas (min, max, avg) de las variables speed_kmh, temperature_c y battery_pct en una ventana de tiempo.
```bash
curl http://127.0.0.1:8000/vehicles/veh-001/stats?minutes=60
```

GET /vehicles/{vehicle_id}/anomalies?minutes=60
Detecta puntos de telemetría anómalos en la ventana especificada usando z-score robusto.
```bash
curl http://127.0.0.1:8000/vehicles/veh-001/anomalies?minutes=60
```

POST /vehicles/{vehicle_id}/commands
Envía un comando a un vehículo.

Ejemplo payload:
```json
{
    "command": "start"
}
```

Curl de ejemplo:
```bash
curl -X POST http://127.0.0.1:8000/vehicles/veh-001/commands \
-H "Content-Type: application/json" \
-d '{"command":"start"}'
```
Script para publicar telemetría vía MQTT
Guardar como publish_example.py:
```python
import os
import json
import time
import random
import paho.mqtt.client as mqtt
from datetime import datetime, timezone

# Configuración del broker
broker = os.getenv("MQTT_HOST", "test.mosquitto.org")
port = int(os.getenv("MQTT_PORT", "1883"))
vehicle_id = "veh-001"
topic = f"vehicles/{vehicle_id}/telemetry"

client = mqtt.Client()
client.connect(broker, port, 60)

for i in range(10):
    payload = {
        "vehicle_id": vehicle_id,
        "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "speed_kmh": round(random.uniform(0, 120), 2),
        "temperature_c": round(random.uniform(20, 80), 2),
        "battery_pct": random.randint(10, 100),   # ahora es int
        "range_km": round(random.uniform(50, 300), 2),
        "odometer_km": round(random.uniform(1000, 50000), 2),
        "gps": {
            "lat": round(40.4168 + random.random()/100, 6),
            "lon": round(-3.7038 + random.random()/100, 6)
        },
        "smoke_detected": False,
        "status": "moving"  # solo 'moving' o 'stopped'
    }
    client.publish(topic, json.dumps(payload), qos=1)
    print(f"Published: {payload}")
    time.sleep(0.5)

# Espera un momento antes de desconectar
time.sleep(2)
client.disconnect()
print("[MQTT] Desconectado")
```
Ejecutar:
```bash
python publish_example.py
```
Esto publicará 10 mensajes de telemetría de ejemplo al broker MQTT local.

Notas finales
La base de datos SQLite se llama data.db y no se reinicia automáticamente entre ejecuciones.

Los tests del proyecto usan IDs de vehículo únicos para no interferir con datos existentes.

La detección de anomalías es simple y basada en z-score robusto para speed_kmh, temperature_c y battery_pct.

La API puede ejecutarse con uvicorn y se integra con MQTT para enviar comandos y recibir telemetría en tiempo real.

