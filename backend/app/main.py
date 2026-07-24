from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.models import Base, engine
from app.routes.ingestion import router as ingestion_router
from app.ingestion.syslog_receiver import start_syslog_thread


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    start_syslog_thread()
    yield


app = FastAPI(title="SIEM Dashboard API", lifespan=lifespan)

app.include_router(ingestion_router)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "siem-backend"}