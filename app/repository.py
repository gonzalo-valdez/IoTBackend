import sqlite3
from app.database import DB_PATH

def save_telemetry(data: dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO telemetry (
            vehicle_id, ts, speed_kmh, temperature_c, battery_pct,
            range_km, odometer_km, gps_lat, gps_lon, smoke_detected, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["vehicle_id"], data["ts"], data["speed_kmh"], data["temperature_c"],
        data["battery_pct"], data["range_km"], data["odometer_km"],
        data["gps"]["lat"], data["gps"]["lon"], int(data["smoke_detected"]), data["status"]
    ))
    conn.commit()
    conn.close()
