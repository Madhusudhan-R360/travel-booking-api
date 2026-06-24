from fastapi import APIRouter, HTTPException
from bson import ObjectId
from datetime import datetime
from bson.errors import InvalidId
import random

from database.connection import bookings_collection, flights_collection
from models.booking import Booking

router = APIRouter()


# ✅ Book flight
@router.post("/book")
def book_flight(booking: Booking):

    if booking.seats <= 0 or booking.seats > 3:
        raise HTTPException(400, "Seats must be 1–3")

    flight = flights_collection.find_one({
        "flight_name": booking.flight_name,
        "source": booking.source,
        "destination": booking.destination,
        "date": booking.date,
        "status": "active"
    })

    if not flight:
        raise HTTPException(404, "Flight not found")

    # ✅ Atomic seat check
    update = flights_collection.update_one(
        {"_id": flight["_id"], "seats": {"$gte": booking.seats}},
        {"$inc": {"seats": -booking.seats}}
    )

    if update.modified_count == 0:
        raise HTTPException(400, "No seats available")

    booking_ref = f"FL{random.randint(10000, 99999)}"

    data = {
        "booking_ref": booking_ref,
        "user_name": booking.user_name,
        "email": booking.email,
        "flight_id": str(flight["_id"]),
        "date": flight["date"],
        "time": flight["time"],
        "booked_seats": booking.seats,
        "status": "confirmed",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    result = bookings_collection.insert_one(data)

    return {
        "booking_id": str(result.inserted_id),
        "booking_ref": booking_ref
    }


# ✅ Cancel booking
@router.delete("/booking/{booking_id}")
def cancel_booking(booking_id: str):

    try:
        obj_id = ObjectId(booking_id)
    except InvalidId:
        raise HTTPException(400, "Invalid booking ID")

    booking = bookings_collection.find_one({"_id": obj_id})

    if not booking:
        raise HTTPException(404, "Not found")

    if booking["status"] == "cancelled":
        raise HTTPException(400, "Already cancelled")

    bookings_collection.update_one(
        {"_id": obj_id},
        {"$set": {"status": "cancelled"}}
    )

    flights_collection.update_one(
        {"_id": ObjectId(booking["flight_id"])},
        {"$inc": {"seats": booking["booked_seats"]}}
    )

    return {"message": "Cancelled"}