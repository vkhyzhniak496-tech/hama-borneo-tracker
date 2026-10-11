from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field

WindowState = Literal["closed", "micro", "tilt", "open"]

class ReadingCreate(BaseModel):
    temperature: float = Field(
        ...,
        ge=-40.0,
        le=70.0,
        description="Temperatura wewnątrz (°C)",
        examples=[22.4],
    )
    humidity: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Wilgotność wewnątrz (%)",
        examples=[48.0],
    )
    timestamp: Optional[datetime] = Field(
        default=None, description="Data i czas odczytu (opcjonalny)"
    )
    window_state: WindowState = Field(default="micro", description="Stan okna: closed, micro, tilt, open")
    door_open: bool = Field(default=False, description="Czy drzwi do pokoju są otwarte?")


class ReadingResponse(ReadingCreate):
    id: int
    outdoor_temperature: Optional[float] = None
    outdoor_humidity: Optional[float] = None
    weather_code: Optional[int] = None
    timestamp: datetime

    class Config:
        from_attributes = True