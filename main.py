from datetime import datetime
from typing import List, Optional

from fastapi import Depends, FastAPI, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import Reading, get_db
import schemas
from weather import get_current_outdoor_weather, get_weather_icon

app = FastAPI(title="Hama Borneo Logger API", version="1.1.0")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def index(request: Request, db: Session = Depends(get_db)):
    readings = (
        db.query(Reading).order_by(Reading.timestamp.desc()).limit(50).all()
    )

    # Przygotowujemy dane wzbogacone o ikony
    readings_view = []
    for r in readings:
        readings_view.append(
            {
                "id": r.id,
                "timestamp": r.timestamp,
                "temperature": r.temperature,
                "humidity": r.humidity,
                "outdoor_temperature": r.outdoor_temperature,
                "outdoor_humidity": r.outdoor_humidity,
                "icon": get_weather_icon(r.weather_code),
                "delta_temp": (
                    round(r.temperature - r.outdoor_temperature, 1)
                    if r.outdoor_temperature is not None
                    else None
                ),
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
    db: Session = Depends(get_db),
):
    ts = (
        datetime.fromisoformat(reading_time)
        if reading_time
        else datetime.now()
    )
    out_temp, out_hum, wcode = get_current_outdoor_weather()

    entry = Reading(
        temperature=temperature,
        humidity=humidity,
        outdoor_temperature=out_temp,
        outdoor_humidity=out_hum,
        weather_code=wcode,
        timestamp=ts,
    )
    db.add(entry)
    db.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


# --- REST API ---


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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8050, reload=False)