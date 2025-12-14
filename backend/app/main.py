from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from typing import List

# In-memory storage
sensor_data_store: List["SensorData"] = []

# Create FastAPI app
app_kei = FastAPI(title="Predictive Maintenance API")


# Data Model
class SensorData(BaseModel):
    sensor_id: str
    timestamp: datetime
    temperature: float
    vibration: float
    pressure: float
    rpm: int


# Routes
@app_kei.get("/")
def read_root():
    return {"message": "Predictive Maintenance API running"}

@app_kei.get("/health")
def health_check():
    return {"status": "alive"}

@app_kei.post("/sensor_data")
def receive_sensor_data(data: SensorData):
    sensor_data_store.append(data)
    return {
        "message": "Sensor data received and saved",
        "total_records": len(sensor_data_store)
    }

@app_kei.get("/sensor_data/recent", response_model=List[SensorData])
def recent_sensor_data(limit: int = 10):
    """
    Return the most recent sensor readings.
    """
    return sensor_data_store[-limit:]
