from fastapi import APIRouter, HTTPException
from bson import ObjectId
from datetime import datetime
from utils.logger import logger
from database.connection import bookings_collection, flights_collection
from models.booking import Booking
import random

router = APIRouter()


# ✅ BOOK FLIGHT
@router.post("/book")
def book_flight(booking: Booking):

    # ✅ FIX: correct operator
    if booking.seats <= 0 or booking.seats > 3:
        raise HTTPException(
            status_code=400,
            detail="You can book between 1 and 3 seats"
        )

    # ✅ Find flight
    flight = flights_collection.find_one({
        "flight_name": booking.flight_name,
        "source": booking.source,
        "destination": booking.destination,
        "date": booking.date,
        "status": "active"
    })

    if not flight:
        raise HTTPException(404, "Flight not found")

    # ✅ Booking limit per user
    booking_count = bookings_collection.count_documents({
        "user_name": booking.user_name,
        "status": "confirmed"
    })

    if booking_count >= 3:
        raise HTTPException(400, "Maximum 3 bookings allowed")

    # ✅ Prevent duplicate booking
    existing_booking = bookings_collection.find_one({
        "user_name": booking.user_name,
        "flight_name": booking.flight_name,
        "date": booking.date,
        "status": "confirmed"
    })

    if existing_booking:
        raise HTTPException(400, "Already booked this flight")

    # ✅ Prevent past booking
    try:
        flight_datetime = datetime.strptime(
            f"{flight['date']} {flight['time']}",
            "%Y-%m-%d %H:%M"
        )

        if flight_datetime < datetime.now():
            raise HTTPException(400, "Cannot book past flights")

    except ValueError:
        raise HTTPException(400, "Invalid flight date/time")

    # ✅ Atomic seat update
    update_result = flights_collection.update_one(
        {
            "_id": flight["_id"],
            "seats": {"$gte": booking.seats}
        },
        {"$inc": {"seats": -booking.seats}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(400, "Not enough seats available")

    # ✅ Booking reference
    booking_ref = f"FL{random.randint(10000, 99999)}"

    # ✅ Create booking
    booking_data = {
        "booking_ref": booking_ref,
        "user_name": booking.user_name,
        "email": booking.email,
        "flight_id": str(flight["_id"]),
        "flight_name": flight["flight_name"],
        "source": flight["source"],
        "destination": flight["destination"],
        "date": flight["date"],
        "time": flight["time"],
        "booked_seats": booking.seats,
        "status": "confirmed",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    result = bookings_collection.insert_one(booking_data)

    return {
        "message": "Booking confirmed",
        "booking_ref": booking_ref,
        "booking_id": str(result.inserted_id)
    }


# ✅ GET ALL BOOKINGS
@router.get("/bookings")
def get_all_bookings(limit: int = 5, skip: int = 0):

    cursor = bookings_collection.find().sort("created_at", -1).skip(skip).limit(limit)

    bookings = []
    for booking in cursor:
        booking["_id"] = str(booking["_id"])
        bookings.append(booking)

    return {"count": len(bookings), "bookings": bookings}


# ✅ GET USER BOOKINGS
@router.get("/bookings/{user_name}")
def get_user_bookings(user_name: str):

    bookings = []
    for booking in bookings_collection.find({"user_name": user_name}):
        booking["_id"] = str(booking["_id"])
        bookings.append(booking)

    return {"bookings": bookings}


# ✅ CANCEL BOOKING
@router.delete("/booking/{booking_id}")
def cancel_booking(booking_id: str, reason: str):

    logger.info(f"Cancel request received: {booking_id}")

    try:
        booking_obj_id = ObjectId(booking_id)
    except:
        raise HTTPException(400, "Invalid booking id")

    booking = bookings_collection.find_one({"_id": booking_obj_id})

    if not booking:
        raise HTTPException(404, "Booking not found")

    if booking["status"] == "cancelled":
        raise HTTPException(400, "Already cancelled")

    # ✅ FIX: Clean 24-hour logic
    flight_datetime = datetime.strptime(
        f"{booking['date']} {booking['time']}",
        "%Y-%m-%d %H:%M"
    )

    time_diff = flight_datetime - datetime.now()

    if time_diff.total_seconds() <= 24 * 60 * 60:
        raise HTTPException(400, "Cannot cancel within 24 hours")

    # ✅ Cancel booking
    bookings_collection.update_one(
        {"_id": booking_obj_id},
        {
            "$set": {
                "status": "cancelled",
                "cancel_reason": reason,
                "cancelled_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
    )

    # ✅ Restore seats
    flights_collection.update_one(
        {"_id": ObjectId(booking["flight_id"])},
        {"$inc": {"seats": booking["booked_seats"]}}
    )

    logger.info("Booking cancelled")

    return {"message": "Booking cancelled successfully"}


# ✅ SUMMARY
@router.get("/bookings/{user_name}/summary")
def get_booking_summary(user_name: str):

    total = bookings_collection.count_documents({"user_name": user_name})

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
        "total": total,
        "confirmed": confirmed,
        "cancelled": cancelled,
        "remaining_slots": remaining
    }