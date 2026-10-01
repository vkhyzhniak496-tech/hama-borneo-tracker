from datetime import datetime
from pathlib import Path
from sqlalchemy import Column, DateTime, Float, Integer, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

RESOURCES_DIR = Path(__file__).resolve().parent / "resources"
RESOURCES_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = RESOURCES_DIR / "hama_borneo.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Reading(Base):
    __tablename__ = "readings"

    id = Column(Integer, primary_key=True, index=True)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    outdoor_temperature = Column(Float, nullable=True)
    outdoor_humidity = Column(Float, nullable=True)
    weather_code = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.now)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()