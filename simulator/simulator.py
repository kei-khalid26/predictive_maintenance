import time
import random
import requests
from datetime import datetime, timezone
import os

API_URL = os.getenv("API_URL", "http://pm_backend:8000/sensor_data")


SENSORS = ["motor_01", "motor_02"]
SEND_INTERVAL_SEC = 2

#moved from random range-based sampling to a stateful drift model because predictive maintenance relies on temporal trends rather than isolated anomalies.
# Gradual degradation per cycle (simulates wear)
TEMP_DRIFT_PER_CYCLE = 0.2
VIBRATION_DRIFT_PER_CYCLE = 0.002

# Probability of sudden fault (rare but possible)
ANOMALY_PROBABILITY = 0.05

API_URL = os.getenv("API_URL", "http://pm_backend:8000/sensor_data")

# Wait until backend is ready
while True:
    try:
        requests.get(API_URL.replace("/sensor_data", "/docs"), timeout=2)
        print("Backend is ready, starting simulator...")
        break
    except requests.RequestException:
        print("Waiting for backend to be ready...")
        time.sleep(2)


# Initial sensor state (IMPORTANT: persistent values)
sensor_state = {
    sensor: {
        "temperature": random.uniform(60, 70),
        "vibration": random.uniform(0.01, 0.02),
        "pressure": random.uniform(95, 105),
        "rpm": random.randint(1400, 1600)
    }
    for sensor in SENSORS
}

def classify_severity(temp, vib, pressure, rpm):
    """
    Determines severity level based on sensor values.
    """
    if temp > 95 or vib > 0.15 or pressure > 130 or rpm > 2200:
        return "critical"
    elif temp > 85 or vib > 0.08 or pressure > 115 or rpm > 1800:
        return "warning"
    return "normal"

while True:
    for sensor_id, state in sensor_state.items():

        # Gradual drift (long-term degradation)
        state["temperature"] += TEMP_DRIFT_PER_CYCLE + random.uniform(-0.1, 0.1)
        state["vibration"] += VIBRATION_DRIFT_PER_CYCLE + random.uniform(-0.001, 0.001)

        # Stable signals with noise
        state["pressure"] += random.uniform(-1, 1)
        state["rpm"] += random.randint(-30, 30)

        # Rare sudden anomaly
        if random.random() < ANOMALY_PROBABILITY:
            state["temperature"] += random.uniform(5, 10)
            state["vibration"] += random.uniform(0.05, 0.1)

        severity = classify_severity(
            state["temperature"],
            state["vibration"],
            state["pressure"],
            state["rpm"]
        )

        payload = {
            "sensor_id": sensor_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "temperature": round(state["temperature"], 2),
            "vibration": round(state["vibration"], 4),
            "pressure": round(state["pressure"], 2),
            "rpm": int(state["rpm"]),
            "severity": severity
        }

        try:
            response = requests.post(API_URL, json=payload, timeout=2)
            response.raise_for_status()

            print(
                f"[{sensor_id}] {severity.upper():8} | "
                f"T={payload['temperature']}°C "
                f"V={payload['vibration']} "
                f"P={payload['pressure']} "
                f"RPM={payload['rpm']}"
            )

        except requests.RequestException as e:
            print(f"[{sensor_id}] ERROR sending data: {e}")

    time.sleep(SEND_INTERVAL_SEC)
