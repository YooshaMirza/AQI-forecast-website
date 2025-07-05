import requests
import pandas as pd
from geopy.geocoders import Nominatim

NASA_BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"

def get_lat_lon(city_name):
    geolocator = Nominatim(user_agent="aqi_forecast_app")
    location = geolocator.geocode(city_name)
    return location.latitude, location.longitude

def fetch_nasa_weather(lat, lon, start_date, end_date):
    params = {
        "parameters": "T2M,RH2M,PS,PRECTOTCORR,WS2M",
        "community": "SB",
        "longitude": lon,
        "latitude": lat,
        "start": start_date,
        "end": end_date,
        "format": "JSON"
    }
    res = requests.get(NASA_BASE_URL, params=params).json()
    if "parameter" not in res.get("properties", {}):
        return pd.DataFrame()
    raw = res['properties']['parameter']
    df = pd.DataFrame({key: pd.Series(value) for key, value in raw.items()})
    df.index = pd.to_datetime(df.index, format="%Y%m%d", errors='coerce')
    df.replace(-999.0, pd.NA, inplace=True)
    df.dropna(inplace=True)
    return df

def classify_aqi(aqi):
    if aqi <= 50:
        return "🟢 Good – Air quality is considered satisfactory."
    elif aqi <= 100:
        return "🟡 Satisfactory – Minor discomfort to sensitive people"
    elif aqi <= 200:
        return "🟠 Moderate – May cause breathing discomfort to people with lung disease"
    elif aqi <= 300:
        return "🔴 Poor – May cause discomfort to most people"
    elif aqi <= 400:
        return "🟣 Very Poor – May cause respiratory issues"
    else:
        return "⚫ Severe – Affects healthy people and seriously impacts those with existing diseases"
