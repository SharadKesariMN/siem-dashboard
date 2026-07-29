import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.models import Base, engine
from app.routes.ingestion import router as ingestion_router
from app.routes.alerts import router as alerts_router
from app.routes.logs import router as logs_router
from app.routes.stats import router as stats_router
from app.ingestion.syslog_receiver import start_syslog_thread
from app.correlation.engine import start_correlation_thread
from app.auth import verify_credentials


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    start_syslog_thread()
    start_correlation_thread()
    yield


app = FastAPI(title="SIEM Dashboard API", lifespan=lifespan)

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(alerts_router, dependencies=[Depends(verify_credentials)])
app.include_router(logs_router, dependencies=[Depends(verify_credentials)])
app.include_router(stats_router, dependencies=[Depends(verify_credentials)])

# Ingestion stays open so log sources (syslog, scripts) can push data without a browser login prompt
app.include_router(ingestion_router)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "siem-backend"}
