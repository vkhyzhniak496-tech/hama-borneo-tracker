from datetime import datetime
from typing import List, Optional

from fastapi import Depends, FastAPI, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import Reading, get_db
import schemas

app = FastAPI(
    title="Hama Borneo Logger API",
    description="System rejestracji parametrów mikroklimatu",
    version="1.0.0",
)
templates = Jinja2Templates(directory="templates")

# ==========================================
# 1. WIDOKI HTML (dla przeglądarki)
# ==========================================


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def index(request: Request, db: Session = Depends(get_db)):
    readings = (
        db.query(Reading).order_by(Reading.timestamp.desc()).limit(50).all()
    )
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "readings": readings,
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
    entry = Reading(temperature=temperature, humidity=humidity, timestamp=ts)
    db.add(entry)
    db.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


# ==========================================
# 2. REST API (JSON)
# ==========================================


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
    entry = Reading(
        temperature=payload.temperature, humidity=payload.humidity, timestamp=ts
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@app.get(
    "/api/readings",
    response_model=List[schemas.ReadingResponse],
    summary="Pobierz listę ostatnich odczytów",
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

    uvicorn.run("main:app", host="0.0.0.0", port=8050, reload=True)