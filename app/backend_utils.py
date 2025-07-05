from geopy.geocoders import Nominatim
import requests
import pandas as pd

WAQI_API_KEY = "7a13d4d6e067f50c450cf744851de3dfd604c39c"
NASA_BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"

def get_lat_lon(city_name):
    geolocator = Nominatim(user_agent="aqi_forecast_app")
    location = geolocator.geocode(city_name)
    return location.latitude, location.longitude

def get_realtime_aqi(city):
    url = f"https://api.waqi.info/feed/{city}/?token={WAQI_API_KEY}"
    r = requests.get(url).json()
    return r['data']['aqi'] if r['status'] == 'ok' else None

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
