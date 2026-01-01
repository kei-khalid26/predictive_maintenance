from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import os
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, Float, String, DateTime, select

#DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/predictive_maintenance")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    DATABASE_URL = "postgresql+asyncpg://postgres:postgres@pm_postgres:5432/predictive_maintenance"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# ----------------------
# Database models
# ----------------------

class SensorDataDB(Base):
    __tablename__ = "sensor_data"
    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(String, index=True)
    timestamp = Column(DateTime(timezone=True))
    temperature = Column(Float)
    vibration = Column(Float)
    pressure = Column(Float)
    rpm = Column(Integer)
    severity = Column(String)

class SensorConfigDB(Base):
    __tablename__ = "sensor_config"
    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(String, unique=True, index=True)
    max_temperature = Column(Float)
    max_vibration = Column(Float)
    pressure_min = Column(Float)
    pressure_max = Column(Float)
    max_rpm = Column(Integer)

# ----------------------
# Pydantic models
# ----------------------

class SensorData(BaseModel):
    sensor_id: str
    timestamp: datetime
    temperature: float
    vibration: float
    pressure: float
    rpm: int
    severity: Optional[str] = "normal"

class SensorConfig(BaseModel):
    sensor_id: str
    max_temperature: float
    max_vibration: float
    pressure_min: float
    pressure_max: float
    max_rpm: int

class Alert(BaseModel):
    sensor_id: str
    timestamp: datetime
    issues_detected: List[str]
    severity: str

class PredictionResponse(BaseModel):
    checked_records: int
    alerts_found: int
    alerts: List[Alert]

# ----------------------
# FastAPI app
# ----------------------

app_kei = FastAPI(title="Predictive Maintenance API")

@app_kei.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app_kei.post("/sensor_data")
async def receive_sensor_data(data: SensorData):
    async with AsyncSessionLocal() as session:
        payload = data.model_dump(exclude_unset=True)
        db_data = SensorDataDB(**payload)
        session.add(db_data)
        await session.commit()
    return {"message": "Sensor data saved"}

@app_kei.get("/sensor_data/recent", response_model=List[SensorData])
async def recent_sensor_data(limit: int = 10):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(SensorDataDB).order_by(SensorDataDB.timestamp.desc()).limit(limit))
        return [SensorData(
            sensor_id=row.sensor_id,
            timestamp=row.timestamp,
            temperature=row.temperature,
            vibration=row.vibration,
            pressure=row.pressure,
            rpm=row.rpm,
            severity=row.severity
        ) for row in result.scalars()]

@app_kei.post("/sensor_config")
async def register_sensor_config(config: SensorConfig):
    async with AsyncSessionLocal() as session:
        existing = await session.execute(select(SensorConfigDB).where(SensorConfigDB.sensor_id==config.sensor_id))
        db_config = existing.scalar_one_or_none()
        if db_config:
            for field, value in config.dict().items():
                setattr(db_config, field, value)
        else:
            db_config = SensorConfigDB(**config.dict())
            session.add(db_config)
        await session.commit()
    return {"message": "Sensor configuration saved"}

@app_kei.get("/predict_failure", response_model=PredictionResponse)
async def predict_failure(recent: int = 5):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(SensorDataDB).order_by(SensorDataDB.timestamp.desc()).limit(recent))
        recent_data = result.scalars().all()

        if not recent_data:
            return PredictionResponse(checked_records=0, alerts_found=0, alerts=[])

        alerts_list = []
        # default thresholds
        default_thresholds = {
            "max_temperature": 80.0,
            "max_vibration": 0.05,
            "pressure_min": 90.0,
            "pressure_max": 110.0,
            "max_rpm": 2000
        }

        # fetch sensor configs
        config_result = await session.execute(select(SensorConfigDB))
        config_dict = {c.sensor_id: c for c in config_result.scalars().all()}

        for reading in recent_data:
            thresholds = config_dict.get(reading.sensor_id, default_thresholds)
            issues = []
            if reading.temperature > getattr(thresholds, "max_temperature", thresholds["max_temperature"]):
                issues.append("High temperature")
            if reading.vibration > getattr(thresholds, "max_vibration", thresholds["max_vibration"]):
                issues.append("High vibration")
            if reading.pressure < getattr(thresholds, "pressure_min", thresholds["pressure_min"]) or \
               reading.pressure > getattr(thresholds, "pressure_max", thresholds["pressure_max"]):
                issues.append("Pressure out of range")
            if reading.rpm > getattr(thresholds, "max_rpm", thresholds["max_rpm"]):
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
