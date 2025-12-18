import time
import random
import requests
from datetime import datetime, timezone

API_URL = "http://127.0.0.1:8000/sensor_data"

SENSORS = ["motor_1", "motor_2"]
SEND_INTERVAL_SEC = 2
ANOMALY_PROBABILITY = 0.1  # 10% chance per reading

# Normal operating ranges
NORMAL_RANGES = {
    "temperature": (60, 80),     # °C
    "vibration": (0.01, 0.05),   # mm/s
    "pressure": (90, 110),       # PSI
    "rpm": (1400, 1600)
}

# Failure-like ranges
ANOMALY_RANGES = {
    "temperature": (90, 110),
    "vibration": (0.2, 0.5),
    "pressure": (120, 140),
    "rpm": (2000, 2500)
}

def generate_value(metric):
    if random.random() < ANOMALY_PROBABILITY:
        low, high = ANOMALY_RANGES[metric]
        return random.uniform(low, high), True
    else:
        low, high = NORMAL_RANGES[metric]
        return random.uniform(low, high), False

while True:
    for sensor_id in SENSORS:
        temp, temp_anom = generate_value("temperature")
        vib, vib_anom = generate_value("vibration")
        pres, pres_anom = generate_value("pressure")
        rpm, rpm_anom = generate_value("rpm")

        is_anomaly = any([temp_anom, vib_anom, pres_anom, rpm_anom])

        payload = {
            "sensor_id": sensor_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "temperature": round(temp, 2),
            "vibration": round(vib, 3),
            "pressure": round(pres, 2),
            "rpm": int(rpm)
        }

        try:
            response = requests.post(API_URL, json=payload, timeout=2)
            response.raise_for_status()

            status = "ANOMALY" if is_anomaly else "normal"
            print(f"[{sensor_id}] {status} | {response.status_code}")

        except requests.RequestException as e:
            print(f"[{sensor_id}] ERROR sending data: {e}")

    time.sleep(SEND_INTERVAL_SEC)
