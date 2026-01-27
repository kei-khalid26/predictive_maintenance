import psycopg2
import pandas as pd
import numpy as np

# -------------------------------
# Database helpers
# -------------------------------

def get_postgres_connection():
    """Return a connection to Postgres DB using environment variables"""
    import os
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", 5432),
        dbname=os.getenv("POSTGRES_DB", "pm_db"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres")
    )

def fetch_sensor_data(limit=None):
    """Fetch sensor data from the database as a pandas DataFrame"""
    conn = get_postgres_connection()
    query = "SELECT device_id, timestamp, temperature, vibration, pressure, rpm FROM sensor_data ORDER BY timestamp ASC"
    if limit:
        query += f" LIMIT {limit}"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# -------------------------------
# Windowing helper
# -------------------------------

def create_sliding_windows(df, window_size=10, step=1):
    """
    Convert time-series data into sliding windows.
    df: pandas DataFrame with columns [temperature, vibration, pressure, rpm]
    Returns: numpy array of shape [num_windows, window_size, num_features]
    """
    features = ["temperature", "vibration", "pressure", "rpm"]
    data = df[features].values
    windows = []
    for start in range(0, len(data) - window_size + 1, step):
        end = start + window_size
        windows.append(data[start:end])
    return np.array(windows)

def fetch_sensor_data(limit=None):
    conn = get_postgres_connection()
    query = """
        SELECT device_id, timestamp, temperature, vibration, pressure, rpm
        FROM sensor_data
        ORDER BY timestamp ASC
    """
    if limit:
        query += " LIMIT %s"
        df = pd.read_sql(query, conn, params=(limit,))
    else:
        df = pd.read_sql(query, conn)

    conn.close()
    return df

