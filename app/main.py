from fastapi import FastAPI
from app.config import settings
from app.routers import auth, bookings

app = FastAPI(title="Service Booking Platform API")

app.include_router(auth.router)
app.include_router(bookings.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
