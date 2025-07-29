# AQI Forecast Application

This application provides Air Quality Index (AQI) forecasts using machine learning models. It leverages weather data from NASA's POWER API and real-time AQI data from the World Air Quality Index (WAQI) API to deliver up-to-date, city-level air quality predictions. The app is designed for both public users and researchers seeking insights into air pollution trends.

**🌐 Live Demo:**  
[https://aqi-forecast-website.onrender.com/](https://aqi-forecast-website.onrender.com/)

---

## 🚀 Features

- **🌍 City-Based AQI Forecasting**  
  Get personalized AQI predictions for any city worldwide by entering its name.

- **🔄 Daily Model Retraining**  
  The ML model is automatically retrained every day with the latest data, ensuring accurate and current predictions.

- **🗺️ Interactive Heatmaps**  
  Visualize regional air quality trends with dynamic, color-coded heatmaps.

- **🗃️ Persistent Data Storage**  
  All models and historical data are securely backed up to GitHub for reliability and transparency.

- **💻 Modern, Responsive UI**  
  Enjoy a sleek, user-friendly interface with clear AQI categories and mobile-friendly design.

- **🛠️ Admin Tools**  
  Built-in admin panel for managing data backups, uploads, and model retraining.

---

## 🏗️ Project Structure

```
aqi_forecast_app/
│
├── .github/workflows/           # GitHub Actions CI/CD
├── app/                         # Core backend modules
│   ├── models/                  # Saved ML models
│   ├── historical_data/         # Historical AQI & weather data
│   ├── backup_manager.py        # Data backup/restore
│   ├── backend_utils.py         # API utilities
│   ├── data_manager.py          # Data management logic
│   ├── fetch_and_train.py       # Model training pipeline
│   ├── github_storage.py        # GitHub persistence
│   ├── init_directories.py      # Directory setup
│   ├── model_loader.py          # Model interface
│   ├── plot_heatmap.py          # Heatmap generator
│   └── scheduled_training.py    # Scheduled retraining
│
├── main.py                      # Flask entrypoint
├── scripts/                     # Utility scripts
│   ├── build_static_site.py     # (legacy) Static site generator
│   ├── deploy_to_github_pages.py # (legacy) GitHub Pages deployer
│   └── setup_github_integration.py # GitHub repo setup
│
├── static/                      # Static assets (maps, CSS, JS)
├── templates/                   # HTML UI templates
│   ├── admin.html               # Admin panel
│   └── index_enhanced.html      # Main UI
│
├── Procfile                     # Render/Heroku deployment config
├── README.md                    # This file
├── render.yaml                  # Render deployment config
├── requirements.txt             # Python dependencies
└── wsgi.py                      # WSGI entrypoint
```

---

## ⚡ Quickstart: Local Setup & Deployment

### 1. Clone the Repository

```bash
git clone https://github.com/YooshaMirza/AQI-forecast-website.git
cd AQI-forecast-website
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file (or set in your environment):

```
WAQI_API_KEY=your_waqi_api_key
GITHUB_TOKEN=your_github_pat   # Optional, for data backup
GITHUB_REPO=username/repo-name # Optional, for data backup
```

### 4. Initialize Application Directories

```bash
python -c "from app.init_directories import init_all; init_all()"
```

### 5. Run the Application

```bash
python main.py
```

Visit [http://localhost:5000](http://localhost:5000) in your browser.

---

## ☁️ Deployment

- **Production:** The app is live at [https://aqi-forecast-website.onrender.com/](https://aqi-forecast-website.onrender.com/)
- **Other Platforms:** You can deploy on Render, Heroku, or any WSGI-compatible host. See `render.yaml` and `Procfile` for starter configs.

---

## 🔄 Data Persistence & Reliability

- **Local Storage:** Models and historical data are saved locally on the server.
- **GitHub Backup:** Data is automatically synchronized to your GitHub repository for persistence, even on ephemeral hosts like Render.
- **Manual Backups:** Use the admin panel to create or restore backups.

---

## 🧠 How It Works

1. **User Input:** Enter a city name to get a forecast.
2. **Geocoding:** The app translates city names to geo-coordinates.
3. **Weather Data Retrieval:** NASA POWER API provides weather metrics for the location.
4. **AQI Data:** Current AQI is fetched from WAQI.
5. **ML Prediction:** The trained model predicts AQI based on combined weather and AQI data.
6. **Model Training:** The model retrains daily for improved accuracy.

---

## 🎨 AQI Categories & Color Codes

| Category      | AQI Range | Meaning                                              | Color     |
|---------------|-----------|------------------------------------------------------|-----------|
| Good          | 0-50      | Air quality is satisfactory                          | 🟢 Green  |
| Satisfactory  | 51-100    | Minor discomfort to sensitive people                 | 🟡 Yellow |
| Moderate      | 101-200   | Discomfort to people with lung disease               | 🟠 Orange |
| Poor          | 201-300   | Discomfort to most people                            | 🔴 Red    |
| Very Poor     | 301-400   | May cause respiratory issues                         | 🟣 Purple |
| Severe        | 401+      | Serious impact on health, affects even healthy people| ⚫ Maroon |

---

## 🛠️ Customization & Advanced Usage

- Add more cities or customize heatmaps by editing `app/plot_heatmap.py`.
- Schedule retraining at custom intervals via `app/scheduled_training.py`.
- Integrate additional data sources by extending `app/data_manager.py` and `app/fetch_and_train.py`.

---

## 🤝 API Credits

- [World Air Quality Index (WAQI) API](https://aqicn.org/api/)
- [NASA POWER API](https://power.larc.nasa.gov/docs/services/api/)

---

## 📄 License

MIT License.  
Feel free to use, modify, and contribute!

---
