from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.models import Base, engine
from app.routes.ingestion import router as ingestion_router
from app.routes.alerts import router as alerts_router
from app.routes.logs import router as logs_router
from app.ingestion.syslog_receiver import start_syslog_thread
from app.correlation.engine import start_correlation_thread


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    start_syslog_thread()
    start_correlation_thread()
    yield


app = FastAPI(title="SIEM Dashboard API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingestion_router)
app.include_router(alerts_router)
app.include_router(logs_router)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "siem-backend"}
