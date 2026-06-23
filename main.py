from fastapi import FastAPI
from routers import flights, bookings
from datetime import datetime
app = FastAPI()

app.include_router(flights.router)
app.include_router(bookings.router)

@app.get("/")
def home():
    return {"message": "Welcome to Travel API"}

@app.get("/health")
def health_check():
    return {
        "status": "UP",
        "service": "Travel Booking API",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }