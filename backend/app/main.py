from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.models import Base, engine
from app.routes.ingestion import router as ingestion_router
from app.routes.alerts import router as alerts_router
from app.ingestion.syslog_receiver import start_syslog_thread
from app.correlation.engine import start_correlation_thread


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    start_syslog_thread()
    start_correlation_thread()
    yield


app = FastAPI(title="SIEM Dashboard API", lifespan=lifespan)

app.include_router(ingestion_router)
app.include_router(alerts_router)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "siem-backend"}