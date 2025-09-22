import sqlite3

DB_PATH = "data.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS telemetry (
        vehicle_id TEXT,
        ts TEXT,
        speed_kmh REAL,
        temperature_c REAL,
        battery_pct REAL,
        range_km REAL,
        odometer_km REAL,
        gps_lat REAL,
        gps_lon REAL,
        smoke_detected BOOLEAN,
        status TEXT,
        PRIMARY KEY (vehicle_id, ts)
    )
    """)
    conn.commit()
    conn.close()
