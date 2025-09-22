# Vehicle Telemetry Service — Tarea 1

Microservicio en **Python + FastAPI + MQTT** que:
- Se suscribe a `vehicles/+/telemetry` vía MQTT.
- Valida la telemetría recibida con **Pydantic**.
- Persiste en **SQLite** (archivo `data.db`).
- Expone un API mínimo en `/` para verificar estado.

## 🚀 Setup

```bash
git clone <repo>
cd <repo>
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
