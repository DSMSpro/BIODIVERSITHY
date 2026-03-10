import numpy as np
from sklearn.ensemble import RandomForestClassifier

# ============================================
# ML MODEL: Biodiversity Risk Prediction
# Features: [temperature, AQI, forest_cover, human_activity]
# Output: LOW / MODERATE / HIGH
# ============================================

X_train = np.array([
    [40, 180, 20, 3],  # High Risk
    [32, 120, 40, 2],  # Moderate Risk
    [25, 60, 70, 1],   # Low Risk
])

y_train = np.array([2, 1, 0])

model = RandomForestClassifier()
model.fit(X_train, y_train)


def predict_risk(features):
    pred = model.predict([features])[0]

    if pred == 2:
        return "HIGH"
    elif pred == 1:
        return "MODERATE"
    return "LOW"
