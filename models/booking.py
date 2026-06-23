from pydantic import BaseModel, EmailStr

class Booking(BaseModel):
    user_name: str 
    email: EmailStr
    source: str
    destination: str
    flight_name: str
    date: str
    seats: int