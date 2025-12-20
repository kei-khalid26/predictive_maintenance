from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Optional

# In-memory storage
sensor_data_store: List["SensorData"] = []

# In-memory sensor configuration storage
sensor_config_store = {}

# Default thresholds (used if no sensor-specific config exists)
default_thresholds = {
    "max_temperature": 80.0,
    "max_vibration": 0.05,
    "pressure_min": 90.0,
    "pressure_max": 110.0,
    "max_rpm": 2000
}

class Alert(BaseModel):
    sensor_id: str
    timestamp: str
    issues_detected: List[str]

class PredictionResponse(BaseModel):
    checked_records: int
    alerts_found: int
    alerts: List[Alert]

# Create FastAPI app
app_kei = FastAPI(
    title="Predictive Maintenance API",
    description = """API for collecting industrial sensor data
    and detecting potential equipment failures using rule-based analysis.
    
    Sensors can submit telemetry such as temperature, vibration, pressure, and RPM. 
    The system analyzes recent data and generates alerts when abnormal conditions are detected.quit
    """,
    version = "0.1.0"
)


# Data Model
class SensorData(BaseModel):
    sensor_id: str
    timestamp: datetime
    temperature: float
    vibration: float
    pressure: float
    rpm: int
    severity: Optional[str] = "normal"

    class Config: # wrong needs fixing, has 
        schema_extra = {
            "example": {
                "sensor_id": "motor_01",
                "timestamp": "2025-01-13T17:00:00",
                "temperature": 92.5,
                "vibration": 0.07,
                "pressure": 118.0,
                "rpm": 2150,
                "severity": "normal"
            }
        }

class SensorConfig(BaseModel):
    sensor_id: str
    max_temperature: float
    max_vibration: float
    pressure_min: float
    pressure_max: float
    max_rpm: int

    class Config:
        json_schema_extra = {
            "example": {
                "sensor_id": "motor_01",
                "max_temperature": 90.0,
                "max_vibration": 0.08,
                "pressure_min": 95.0,
                "pressure_max": 120.0,
                "max_rpm": 2200
            }
        }

class Alert(BaseModel):
    sensor_id: str
    timestamp: datetime
    issues_detected: List[str]
    severity: str


class PredictionResponse(BaseModel):
    checked_records: int
    alerts_found: int
    alerts: List[Alert]


# Routes
@app_kei.get("/")
def read_root():
    """
    Root endpoint to verify the API is running.
    """
    return {"message": "Predictive Maintenance API running"}

@app_kei.get("/health")
def health_check():
    """
    Health check endpoint for monitoring and orchestration systems.
    """
    return {"status": "alive"}

@app_kei.post("/sensor_data")
def receive_sensor_data(data: SensorData):
    """
    Receive a single sensor reading and store it in memory.
    """
    sensor_data_store.append(data)
    return {
        "message": "Sensor data received and saved",
        "total_records": len(sensor_data_store)
    }

@app_kei.get("/sensor_data/recent", response_model=List[SensorData])
def recent_sensor_data(limit: int = 10):
    """
    Retrieve the most recent sensor readings.

    Limited by the number of recent records to return (default: 10)
    """
    return sensor_data_store[-limit:]

@app_kei.get("/predict_failure", response_model=PredictionResponse)
def predict_failure(recent: int = 5):
    """
    Analyze recent sensor data and detect potential failures
    """

    if len(sensor_data_store) == 0:
        # Return an empty but valid response
        return PredictionResponse(
            checked_records=0,
            alerts_found=0,
            alerts=[]
        )

    # Take the last `recent` records
    recent_data = sensor_data_store[-recent:]
    alerts_list = []

    for reading in recent_data:
        issues = []

        # Get sensor-specific thresholds or use defaults
        thresholds = sensor_config_store.get(reading.sensor_id, default_thresholds)

        if reading.temperature > thresholds["max_temperature"]:
            issues.append("High temperature")
        if reading.vibration > thresholds["max_vibration"]:
            issues.append("High vibration")
        if reading.pressure < thresholds["pressure_min"] or reading.pressure > thresholds["pressure_max"]:
            issues.append("Pressure out of range")
        if reading.rpm > thresholds["max_rpm"]:
            issues.append("RPM too high")

        if issues:
            alerts_list.append(Alert(
                sensor_id=reading.sensor_id,
                timestamp=reading.timestamp,
                issues_detected=issues,
                severity=reading.severity
            ))

    return PredictionResponse(
        checked_records=len(recent_data),
        alerts_found=len(alerts_list),
        alerts=alerts_list
    )

@app_kei.post("/sensor_config")
def register_sensor_config(config: SensorConfig):
    """
    Register or update configuration thresholds for a sensor.
    """
    sensor_config_store[config.sensor_id] = config.model_dump()
    return {
        "message": "Sensor configuration saved",
        "sensor_id": config.sensor_id
    }





