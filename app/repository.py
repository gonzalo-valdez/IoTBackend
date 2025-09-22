import sqlite3
from datetime import datetime

DB_PATH = "data.db"

def dict_from_row(row):
    if not row:
        return None
    return {
        "vehicle_id": row[0],
        "ts": row[1],
        "speed_kmh": row[2],
        "temperature_c": row[3],
        "battery_pct": row[4],
        "range_km": row[5],
        "odometer_km": row[6],
        "gps": {"lat": row[7], "lon": row[8]},
        "smoke_detected": row[9],
        "status": row[10]
    }

def get_connection():
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn

def save_telemetry(data):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Evitar duplicados
    cursor.execute(
        "SELECT 1 FROM telemetry WHERE vehicle_id=? AND ts=?",
        (data["vehicle_id"], data["ts"])
    )
    if cursor.fetchone():
        conn.close()
        return

    cursor.execute(
        """INSERT INTO telemetry (
            vehicle_id, ts, speed_kmh, temperature_c,
            battery_pct, range_km, odometer_km,
            gps_lat, gps_lon, smoke_detected, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            data["vehicle_id"], data["ts"], data["speed_kmh"], data["temperature_c"],
            data["battery_pct"], data["range_km"], data["odometer_km"],
            data["gps"]["lat"], data["gps"]["lon"], data["smoke_detected"], data["status"]
        )
    )
    conn.commit()
    conn.close()

def get_latest_telemetry(vehicle_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM telemetry WHERE vehicle_id=? ORDER BY ts DESC LIMIT 1",
        (vehicle_id,)
    )
    row = cursor.fetchone()
    conn.close()
    return dict_from_row(row)

def get_telemetry_window(vehicle_id: str, window_start: datetime):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM telemetry WHERE vehicle_id>=? AND ts>=? ORDER BY ts ASC",
        (vehicle_id, window_start.isoformat())
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict_from_row(r) for r in rows]
