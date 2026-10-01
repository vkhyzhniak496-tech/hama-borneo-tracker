import json
import logging
from typing import Optional, Tuple
import urllib.error
import urllib.request
import ssl
# Konfiguracja loggera
logger = logging.getLogger("weather_service")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

# Współrzędne: Warszawa (Mokotów/Ursynów)
LATITUDE = 52.1806
LONGITUDE = 21.0483


def get_current_outdoor_weather(
    lat: float = LATITUDE, lon: float = LONGITUDE
) -> Tuple[Optional[float], Optional[float], Optional[int]]:
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code"
        f"&timezone=auto"
    )

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "HamaTracker/1.0 (internal-logging-system)"},
    )

    # Kontekst pomijający ewentualne problemy z magazynem certyfikatów Pythona
    ctx = ssl.create_default_context()

    try:
        with urllib.request.urlopen(req, timeout=5, context=ctx) as response:
            if response.status != 200:
                logger.error(f"[Open-Meteo] Błąd HTTP: Status {response.status}")
                return None, None, None

            payload = json.loads(response.read().decode("utf-8"))
            current = payload.get("current", {})

            temp = current.get("temperature_2m")
            hum = current.get("relative_humidity_2m")
            wcode = current.get("weather_code")
            return temp, hum, wcode

    except Exception as e:
        logger.error(
            f"[Open-Meteo] Błąd podczas pobierania pogody: {e}", exc_info=True
        )
        return None, None, None


def get_weather_icon(code: Optional[int]) -> str:
    """Mapowanie kodu WMO na ikonę emoji."""
    if code is None:
        return "❓"
    if code == 0:
        return "☀️"  # Czyste niebo
    if code in (1, 2):
        return "🌤️"  # Częściowe zachmurzenie
    if code == 3:
        return "☁️"  # Pochmurno
    if code in (45, 48):
        return "🌫️"  # Mgła
    if code in (51, 53, 55, 61, 63, 65, 80, 81, 82):
        return "🌧️"  # Deszcz
    if code in (71, 73, 75, 77, 85, 86):
        return "❄️"  # Śnieg
    if code in (95, 96, 99):
        return "⛈️"  # Burza
    return "🌡️"