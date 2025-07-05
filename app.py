from flask import Flask, request, render_template
import joblib
import pandas as pd
from datetime import datetime, timedelta
from backend_utils import get_lat_lon, fetch_nasa_weather, classify_aqi

# Load models from "model/" folder
rf_model = joblib.load("model/rf_large_model.pkl")
rf_scaler = joblib.load("model/rf_large_scaler.pkl")
sgd_model = joblib.load("model/sgd_model.pkl")
sgd_scaler = joblib.load("model/scaler.pkl")

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    prediction = None
    city = ""
    if request.method == "POST":
        city = request.form.get("city")
        lat, lon = get_lat_lon(city)
        today = (datetime.today() - timedelta(days=1)).strftime('%Y%m%d')
        last_week = (datetime.today() - timedelta(days=7)).strftime('%Y%m%d')

        weather_df = fetch_nasa_weather(lat, lon, last_week, today)

        if not weather_df.empty:
            last_day_weather = weather_df.iloc[-1:]
            forecast_X = rf_scaler.transform(last_day_weather.values)
            prediction = rf_model.predict(forecast_X)[0]
            category = classify_aqi(prediction)
            return render_template("index.html", city=city.title(), prediction=round(prediction,2), category=category)

    return render_template("index.html", prediction=prediction, city=city)

if __name__ == "__main__":
    app.run(debug=True)
