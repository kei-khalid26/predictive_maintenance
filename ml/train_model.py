import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import joblib
from pathlib import Path

from ml.utils import fetch_sensor_data
from ml.preprocessing import fit_scaler, transform


MODELS_DIR = Path("ml/models")
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------
# Autoencoder
# -------------------------------

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

# -------------------------------
# Training
# -------------------------------

def train():
    df = fetch_sensor_data()
    scaler = fit_scaler(df)
    X = transform(df, scaler)

    X_tensor = torch.tensor(X, dtype=torch.float32)
    dataset = TensorDataset(X_tensor)
    loader = DataLoader(dataset, batch_size=32, shuffle=True)

    model = AutoEncoder(input_dim=X.shape[1])
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.MSELoss()

    for epoch in range(30):
        epoch_loss = 0
        for (batch,) in loader:
            optimizer.zero_grad()
            recon = model(batch)
            loss = loss_fn(recon, batch)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()

        print(f"Epoch {epoch+1} | Loss: {epoch_loss:.4f}")

    torch.save(model.state_dict(), MODELS_DIR / "autoencoder.pth")
    joblib.dump(scaler, MODELS_DIR / "scaler.pkl")
    print("✅ Model & scaler saved")

if __name__ == "__main__":
    train()
