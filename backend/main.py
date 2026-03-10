from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
import joblib
import numpy as np
from rl_agent import rl_recommendation

app = FastAPI()

# Enable frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# AQICN Token
AQICN_TOKEN = "66f7da3b6af1026b572b9e24f32e8726d4154e4b"

# Load ML Model
model = joblib.load("risk_model.pkl")


# ---------------------------------------------------
# 1. Fetch Species from GBIF (India + Flora/Fauna)
# ---------------------------------------------------
def fetch_species(category: str, limit: int = 30):

    kingdom = "Plantae" if category == "flora" else "Animalia"

    url = (
        f"https://api.gbif.org/v1/occurrence/search?"
        f"country=IN&kingdom={kingdom}&limit={limit}"
    )

    data = requests.get(url).json()

    species_set = set()

    for rec in data.get("results", []):
        sp = rec.get("scientificName")
        if sp:
            species_set.add(sp)

    return sorted(list(species_set))


# ---------------------------------------------------
# 2. Fetch Indian States from GBIF
# ---------------------------------------------------
def fetch_states(limit: int = 50):

    url = f"https://api.gbif.org/v1/occurrence/search?country=IN&limit={limit}"
    data = requests.get(url).json()

    state_set = set()

    for rec in data.get("results", []):
        state = rec.get("stateProvince")
        if state:
            state_set.add(state)

    return sorted(list(state_set))


# ---------------------------------------------------
# API: Options Endpoint
# ---------------------------------------------------
@app.get("/options")
def get_options(category: str = Query(...)):
    return {
        "species": fetch_species(category),
        "states": fetch_states()
    }


# ---------------------------------------------------
# 3. Coordinates from GBIF Occurrence (India + State)
# ---------------------------------------------------
def get_coordinates(species: str, state: str):

    url = (
        f"https://api.gbif.org/v1/occurrence/search?"
        f"country=IN&scientificName={species}&stateProvince={state}&limit=1"
    )

    data = requests.get(url).json()

    if not data.get("results"):
        return None, None

    rec = data["results"][0]
    return rec.get("decimalLatitude"), rec.get("decimalLongitude")


# ---------------------------------------------------
# 4. Weather from Open-Meteo
# ---------------------------------------------------
def get_weather(lat, lon):

    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    data = requests.get(url).json()

    return data["current_weather"]["temperature"]


# ---------------------------------------------------
# 5. AQI from AQICN
# ---------------------------------------------------
def get_aqi(lat, lon):

    url = f"https://api.waqi.info/feed/geo:{lat};{lon}/?token={AQICN_TOKEN}"
    data = requests.get(url).json()

    if data["status"] != "ok":
        return None

    return data["data"]["aqi"]


# ---------------------------------------------------
# 6. Threat Status from Wikidata
# ---------------------------------------------------
def get_threat_status(species: str):

    query = f"""
    SELECT ?statusLabel WHERE {{
      ?sp rdfs:label "{species}"@la.
      ?sp wdt:P141 ?status.
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    LIMIT 1
    """

    url = "https://query.wikidata.org/sparql"
    headers = {"Accept": "application/json"}

    r = requests.get(url, params={"query": query}, headers=headers)

    if r.status_code != 200:
        return "Not Available", 2

    bindings = r.json()["results"]["bindings"]

    if not bindings:
        return "Not Available", 2

    status = bindings[0]["statusLabel"]["value"]

    score_map = {
        "least concern": 1,
        "near threatened": 2,
        "vulnerable": 3,
        "endangered": 4,
        "critically endangered": 5,
    }

    return status, score_map.get(status.lower(), 2)


# ---------------------------------------------------
# FINAL Analyze Endpoint (India + ML + RL)
# ---------------------------------------------------
@app.get("/analyze")
def analyze(species: str, state: str, category: str):

    lat, lon = get_coordinates(species, state)

    if lat is None:
        return {"error": "No occurrence found for this species in selected Indian state"}

    temp = get_weather(lat, lon)
    aqi = get_aqi(lat, lon)

    threat_status, threat_score = get_threat_status(species)

    cat_val = 0 if category == "flora" else 1

    features = np.array([[temp, aqi, cat_val, threat_score]])
    pred = model.predict(features)[0]

    risk_map = {0: "LOW", 1: "MEDIUM", 2: "HIGH"}
    risk = risk_map[pred]

    action = rl_recommendation(risk)

    return {
        "species": species,
        "state": state,
        "category": category,
        "lat": lat,
        "lon": lon,
        "temperature": temp,
        "aqi": aqi,
        "threat_status": threat_status,
        "ml_risk": risk,
        "rl_action": action
    }
