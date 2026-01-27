import torch
import torch.nn as nn
import joblib
import numpy as np
from pathlib import Path

from ml.preprocessing import transform


MODELS_DIR = Path("ml/models")

class AutoEncoder(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 8),
            nn.ReLU(),
            nn.Linear(8, 4)
        )
        self.decoder = nn.Sequential(
            nn.Linear(4, 8),
            nn.ReLU(),
            nn.Linear(8, input_dim)
        )

    def forward(self, x):
        z = self.encoder(x)
        return self.decoder(z)

class AnomalyDetector:
    def __init__(self):
        self.scaler = joblib.load(MODELS_DIR / "scaler.pkl")

        self.model = AutoEncoder(input_dim=4)
        self.model.load_state_dict(
            torch.load(MODELS_DIR / "autoencoder.pth", map_location="cpu")
        )
        self.model.eval()

    def score(self, df):
        """
        Returns reconstruction error per row
        """
        X = transform(df, self.scaler)
        X_tensor = torch.tensor(X, dtype=torch.float32)

        with torch.no_grad():
            recon = self.model(X_tensor)
            error = torch.mean((recon - X_tensor) ** 2, dim=1)

        return error.numpy()
