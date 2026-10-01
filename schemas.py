from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


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


class ReadingResponse(ReadingCreate):
    id: int
    outdoor_temperature: Optional[float] = None
    outdoor_humidity: Optional[float] = None
    weather_code: Optional[int] = None
    timestamp: datetime

    class Config:
        from_attributes = True