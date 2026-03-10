# Cognitive Biodiversity AI Dashboard

## Features
- Real-time species occurrence data (GBIF)
- Real-time temperature (Open-Meteo)
- Real-time air quality AQI (AQICN)
- ML Risk Prediction (Random Forest)
- RL Conservation Action Recommendation
- Interactive Map Visualization

## Run Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
