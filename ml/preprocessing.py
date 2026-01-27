#where I transform raw sensor data into features suitable for my ML model.import numpy as np
from sklearn.preprocessing import StandardScaler

FEATURES = ["temperature", "vibration", "pressure", "rpm"]

def fit_scaler(df):
    """
    Fit a StandardScaler on training data
    """
    scaler = StandardScaler()
    scaler.fit(df[FEATURES].values)
    return scaler

def transform(df, scaler):
    """
    Apply fitted scaler to dataframe
    """
    return scaler.transform(df[FEATURES].values)
