from sqlalchemy import Column, Integer, Float, String, TIMESTAMP
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True)
    timestamp = Column(TIMESTAMP, nullable=False)
    temperature = Column(Float, nullable=False)
    vibration = Column(Float, nullable=False)
    pressure = Column(Float, nullable=False)
    rpm = Column(Integer, nullable=False)
    severity = Column(String(10), nullable=False)
