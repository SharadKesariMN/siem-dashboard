from fastapi import FastAPI

app = FastAPI(title="SIEM Dashboard API")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "siem-backend"}
