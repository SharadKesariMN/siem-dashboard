from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.models import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup if they don't exist
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="SIEM Dashboard API", lifespan=lifespan)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "siem-backend"}