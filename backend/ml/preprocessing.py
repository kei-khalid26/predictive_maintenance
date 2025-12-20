# import json
# import numpy as np
# from datetime import datetime

# with open("sensor_data.json","r") as f:
#     data = json.load(f)

# print(f"Loaded {len(data)} records")
# print(data[:2]) #preview first 2 records

# features = []
# timestamps = []

# for record in data:
#     features.append([
#         record["temperature"],
#         record["vibration"],
#         record["pressure"],
#         record["rpm"]
#     ])
#     timestamps.append(record["timestamp"])

# features = np.array(features)
# print("Features array shape:", features.shape)

# WINDOW_SIZE = 10  # number of consecutive readings
# stride = 1        # move 1 reading at a time

# windows = []
# for i in range(0, len(features) - WINDOW_SIZE + 1, stride):
#     window = features[i:i + WINDOW_SIZE]
#     windows.append(window)

# windows = np.array(windows)
# print("Windows shape:", windows.shape)  # (num_windows, window_size, num_features)

# mean = features.mean(axis=0)
# std = features.std(axis=0)
# features_norm = (features - mean) / std

# # Recreate windows with normalized features
# windows_norm = []
# for i in range(0, len(features_norm) - WINDOW_SIZE + 1, stride):
#     window = features_norm[i:i + WINDOW_SIZE]
#     windows_norm.append(window)

# windows_norm = np.array(windows_norm)
# print("Normalized windows shape:", windows_norm.shape)
