from pydantic import BaseModel, validator
from typing import Optional

# ✅ INPUT MODEL (request)
class FlightCreate(BaseModel):
    flight_name: str
    price: int
    seats: int
    source: str
    destination: str
    date: str
    time: str

    @validator("price")
    def price_must_be_positive(cls, value):
        if value <= 0:
            raise ValueError("Price must be greater than 0")
        return value

    @validator("seats")
    def seats_must_be_positive(cls, value):
        if value <= 0:
            raise ValueError("Seats must be greater than 0")
        return value

    @validator("destination")
    def source_destination_check(cls, destination, values):
        source = values.get("source")
        if source and source.lower() == destination.lower():
            raise ValueError("Source and destination cannot be the same")
        return destination


# ✅ OUTPUT MODEL (response)
class FlightResponse(BaseModel):
    flight_name: str
    price: int
    seats: int
    source: str
    destination: str
    date: str
    time: str
    status: str
    cancelled_at: Optional[str] = None