from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

# Create FastAPI app
app_kei = FastAPI()

# -----------------------
# Data Model (Schema)
# -----------------------
class SensorData(BaseModel):
    sensor_id: str
    timestamp: datetime
    temperature: float
    vibration: float
    pressure: float
    rpm: int

# -----------------------
# Routes
# -----------------------

@app_kei.get("/")
def read_root():
    return {"message": "Hello World"}

@app_kei.get("/health")
def health_check():
    return {"status": "alive"}

@app_kei.post("/sensor_data")
def receive_sensor_data(data: SensorData):
    return {
        "message": "Sensor data received",
        "sensor_id": data.sensor_id,
        "timestamp": data.timestamp
    }
