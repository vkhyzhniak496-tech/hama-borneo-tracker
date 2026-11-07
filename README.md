# 🌡️ Hama Borneo Tracker & Smart Ventilation Monitor

A lightweight, asynchronous telemetry system designed for tracking indoor microclimate and evaluating ambient outdoor conditions. The application records manual readings from a **Hama Borneo** weather station, enriches them with real-time meteorological data (via Open-Meteo API), and computes absolute humidity ($AH$) to assess and optimize room ventilation efficiency.

Designed for self-hosting with minimal resource overhead.

---

## 🚀 Key Features

* **Manual Microclimate Logging (Indoor):** Quick manual entry for indoor temperature and relative humidity with custom or automatic timestamps.
* **Fenestration & Ventilation Tracking:**
  * Window modes: Micro-ventilation (`micro` / `🪟≈`), Fully open (`open` / `🪟◽`), Tilted (`tilt` / `🪟◺`), Closed (`closed` / `🪟⏹`).
  * Door status: Tracks whether internal airflow is enabled (`door_open` / `🚪💨`).
* **Automated Outdoor Weather Context:** Every recorded entry is automatically matched with external temperature, relative humidity, and WMO weather icons from Open-Meteo API (Warsaw coordinates: `52.1806°N, 21.0483°E`).
* **Psychrometric Diagnostics:**
  * **Absolute Humidity ($AH$):** Real-time physical calculation of water vapor mass per cubic meter ($g/m^3$) inside and outside.
  * **Ventilation Status:** Diagnostic indicator showing whether ventilating will dry out (`Osusza`) or humidify (`Nawilża`) the room.
  * **Thermal Delta ($\Delta T$):** Quick calculation of temperature differences between indoors and outdoors.
* **Hybrid User Interface:**
  * **Mobile-First Web Dashboard:** Clean Jinja2 template optimized for phones in the local network (LAN) with entry removal and rapid form submission.
  * **REST API & Interactive Docs:** Validated endpoints (Pydantic v2) with built-in Swagger UI under `/docs`.

---

## 🧮 Psychrometric Calculation (Absolute Humidity)

Relative humidity ($RH$) is temperature-dependent and does not represent the real amount of water in the air. To evaluate ventilation drying potential, the application computes **Absolute Humidity** ($AH$) in $g/m^3$ using Magnus-Tetens approximation and the Ideal Gas Law:

### 1. Saturation Vapor Pressure ($p_{\text{sat}}$)
The saturation vapor pressure of water vapor in air (in hPa) at temperature $T$ (°C):

$$p_{\text{sat}}(T) = 6.1078 \times 10^{\left(\frac{7.5 \times T}{237.3 + T}\right)}$$

### 2. Actual Vapor Pressure ($p_{\text{act}}$)
The partial pressure exerted by water vapor present at relative humidity $RH$ (%):

$$p_{\text{act}} = p_{\text{sat}}(T) \times \frac{RH}{100}$$

### 3. Absolute Humidity ($AH$)
Derived from the ideal gas equation ($p = \rho R_s T$), where the specific gas constant for water vapor is $R_v \approx 461.5 \text{ J/(kg}\cdot\text{K)}$:

$$AH = \frac{p_{\text{act}} \times 100}{461.5 \times (T + 273.15)} \times 1000 \quad \left[\text{g/m}^3\right]$$

### Diagnostic Rule:
* **Drying (`Osusza`):** $AH_{\text{outdoor}} < AH_{\text{indoor}}$ — Fresh incoming air carries less moisture; ventilating removes room humidity.
* **Humidifying (`Nawilża`):** $AH_{\text{outdoor}} \ge AH_{\text{indoor}}$ — Outdoor air contains higher absolute moisture; ventilating introduces water vapor indoors.

---

## 🛠️ Tech Stack

* **Backend:** Python 3.10+ / 3.14, FastAPI, Uvicorn
* **Database & ORM:** SQLite (stored under `resources/hama_borneo.db`), SQLAlchemy 2.0
* **Validation:** Pydantic v2
* **Frontend:** Jinja2 HTML templates, CSS
* **Integrations:** Open-Meteo Forecast & Archive API

---

## 📂 Project Structure

```text
hama-borneo-tracker/
├── resources/
│   └── hama_borneo.db       # SQLite database file
├── templates/
│   └── index.html           # Jinja2 mobile-friendly web view
├── database.py              # SQLAlchemy engine, session, and Reading model
├── main.py                  # FastAPI app, endpoints, view context, Uvicorn
├── requirements.txt         # Project dependencies
├── schemas.py               # Pydantic data validation models
└── weather.py               # Weather fetcher, WMO mapping, AH physical formula
```

---

## ⚙️ Quick Start

### 1. Prerequisites
* Python 3.10+ (tested on Python 3.14)
* Dedicated virtual environment

### 2. Setup
```bash
git clone https://github.com/<your-username>/hama-borneo-tracker.git
cd hama-borneo-tracker

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate       # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run Application
Run directly via Python:
```bash
python main.py
```

The application binds to all network interfaces on port `8050`:
* **Web UI:** `http://<HOST_IP>:8050/`
* **Swagger UI / API Docs:** `http://<HOST_IP>:8050/docs`