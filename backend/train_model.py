import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib

# Features:
# [temperature, AQI, category, threat_score]

X = np.array([
    [25, 60, 0, 1],
    [30, 90, 0, 2],
    [35, 140, 1, 3],
    [40, 180, 1, 5],
    [28, 70, 0, 1],
    [38, 160, 1, 4],
])

# Labels: 0=LOW, 1=MEDIUM, 2=HIGH
y = np.array([0, 0, 1, 2, 0, 2])

model = RandomForestClassifier(n_estimators=200)
model.fit(X, y)

joblib.dump(model, "risk_model.pkl")

print("✅ ML Risk Model saved as risk_model.pkl")
