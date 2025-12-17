# Predictive Maintenance API

## Description
A FastAPI-based project for collecting industrial sensor data and detecting potential equipment failures using rule-based analysis.  
Sensors can submit telemetry such as temperature, vibration, pressure, and RPM. The system analyzes recent data and generates alerts when abnormal conditions are detected.

## Features
- Collect sensor data via REST API
- Store sensor configurations and thresholds
- Predict potential equipment failures based on recent readings
- Simple in-memory storage (data lost on server restart)
- FastAPI Swagger docs available at `/docs`

## Installation
```bash
git clone <your-repo-url>
cd predictive_maintenance/backend
python -m venv venv
venv\Scripts\activate  # Windows
# or source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
