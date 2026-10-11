from datetime import datetime
from typing import List, Optional

from fastapi import Depends, FastAPI, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import Reading, get_db
import schemas
from weather import get_current_outdoor_weather, get_weather_icon, calculate_absolute_humidity

app = FastAPI(title="Hama Borneo Logger API", version="1.1.0")
templates = Jinja2Templates(directory="templates")

# Słownik ikon do widoku
WINDOW_ICONS = {
    "closed": "🪟⏹",
    "micro": "🪟≈",
    "tilt": "🪟◺",
    "open": "🪟◽",
}

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def index(request: Request, db: Session = Depends(get_db)):
    readings = (
        db.query(Reading).order_by(Reading.timestamp.desc()).limit(50).all()
    )

    readings_view = []
    for r in readings:
        indoor_ah = calculate_absolute_humidity(r.temperature, r.humidity)
        outdoor_ah = calculate_absolute_humidity(r.outdoor_temperature, r.outdoor_humidity)

        vent_status = None
        if indoor_ah is not None and outdoor_ah is not None:
            vent_status = "drying" if outdoor_ah < indoor_ah else "humidifying"

        readings_view.append(
            {
                "id": r.id,
                "timestamp": r.timestamp,
                "temperature": r.temperature,
                "humidity": r.humidity,
                "indoor_ah": indoor_ah,
                "outdoor_temperature": r.outdoor_temperature,
                "outdoor_humidity": r.outdoor_humidity,
                "outdoor_ah": outdoor_ah,
                "vent_status": vent_status,
                "icon": get_weather_icon(r.weather_code),
                "delta_temp": (
                    round(r.temperature - r.outdoor_temperature, 1)
                    if r.outdoor_temperature is not None
                    else None
                ),
                # Nowe pola:
                "window_state": r.window_state or "micro",
                "window_icon": WINDOW_ICONS.get(r.window_state, "🪟≈"),
                "door_open": bool(r.door_open),
            }
        )

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "readings": readings_view,
            "now": datetime.now().strftime("%Y-%m-%dT%H:%M"),
        },
    )


@app.post("/add", include_in_schema=False)
def form_add_reading(
    temperature: float = Form(...),
    humidity: float = Form(...),
    reading_time: Optional[str] = Form(None),
    window_state: str = Form("micro"),
    door_open: Optional[str] = Form(None),  # Checkbox w HTML wysyła "on" lub brak wartości
    db: Session = Depends(get_db),
):
    ts = (
        datetime.fromisoformat(reading_time)
        if reading_time
        else datetime.now()
    )
    out_temp, out_hum, wcode = get_current_outdoor_weather()

    is_door_open = door_open in ("on", "true", "1")

    entry = Reading(
        temperature=temperature,
        humidity=humidity,
        outdoor_temperature=out_temp,
        outdoor_humidity=out_hum,
        weather_code=wcode,
        timestamp=ts,
        window_state=window_state,
        door_open=is_door_open,
    )
    db.add(entry)
    db.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@app.post(
    "/api/readings",
    response_model=schemas.ReadingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Dodaj nowy odczyt (JSON)",
)
def create_reading(
    payload: schemas.ReadingCreate, db: Session = Depends(get_db)
):
    ts = payload.timestamp or datetime.now()
    out_temp, out_hum, wcode = get_current_outdoor_weather()

    entry = Reading(
        temperature=payload.temperature,
        humidity=payload.humidity,
        outdoor_temperature=out_temp,
        outdoor_humidity=out_hum,
        weather_code=wcode,
        timestamp=ts,
        window_state=payload.window_state,
        door_open=payload.door_open,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

@app.get(
    "/api/readings",
    response_model=List[schemas.ReadingResponse],
    summary="Pobierz listę odczytów",
)
def get_readings(
    limit: int = 50, offset: int = 0, db: Session = Depends(get_db)
):
    return (
        db.query(Reading)
        .order_by(Reading.timestamp.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

@app.post("/delete/{reading_id}", include_in_schema=False)
def delete_reading(reading_id: int, db: Session = Depends(get_db)):
    reading = db.query(Reading).filter(Reading.id == reading_id).first()
    if reading:
        db.delete(reading)
        db.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8050, reload=False)