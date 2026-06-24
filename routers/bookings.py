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

# ✅ Get all bookings
@router.get("/bookings")
def get_all_bookings(limit: int = 5, skip: int = 0):

    cursor = bookings_collection.find() \
        .sort("created_at", -1) \
        .skip(skip) \
        .limit(limit)

    bookings = []

    for booking in cursor:
        booking["_id"] = str(booking["_id"])
        bookings.append(booking)

    return {
        "count": len(bookings),
        "bookings": bookings
    }

# ✅ Get bookings by user
@router.get("/bookings/{user_name}")
def get_user_bookings(user_name: str):

    bookings = []

    for booking in bookings_collection.find({"user_name": user_name}):
        booking["_id"] = str(booking["_id"])
        bookings.append(booking)

    return {"bookings": bookings}

# ✅ Booking summary
@router.get("/bookings/{user_name}/summary")
def get_booking_summary(user_name: str):

    total = bookings_collection.count_documents({
        "user_name": user_name
    })

    confirmed = bookings_collection.count_documents({
        "user_name": user_name,
        "status": "confirmed"
    })

    cancelled = bookings_collection.count_documents({
        "user_name": user_name,
        "status": "cancelled"
    })

    remaining = max(0, 3 - confirmed)

    return {
        "user_name": user_name,
        "total_bookings": total,
        "confirmed": confirmed,
        "cancelled": cancelled,
        "remaining_slots": remaining
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