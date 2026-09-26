from fastapi import FastAPI
from app.config import settings

app = FastAPI(title="Service Booking Platform API")

@app.get("/health")
def health_check():
    return {"status": "ok"}
