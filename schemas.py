from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# Schemat danych przychodzących od klienta
class ReadingCreate(BaseModel):
    temperature: float = Field(
        ...,
        ge=-40.0,
        le=70.0,
        description="Temperatura w °C",
        examples=[22.4],
    )
    humidity: float = Field(
        ..., ge=0.0, le=100.0, description="Wilgotność w %", examples=[48.0]
    )
    timestamp: Optional[datetime] = Field(
        default=None, description="Data i czas odczytu (opcjonalny)"
    )


# Schemat danych zwracanych z bazy / API
class ReadingResponse(ReadingCreate):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True