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

    # ✅ Validate seats per booking
    if booking.seats <= 0 or booking.seats > 3:
        raise HTTPException(
            status_code=400,
            detail="You can book between 1 and 3 seats per booking"
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
        raise HTTPException(status_code=404, detail="Flight not found")

    # ✅ Booking limit per user
    booking_count = bookings_collection.count_documents({
        "user_name": booking.user_name,
        "status": "confirmed"
    })

    if booking_count >= 3:
        raise HTTPException(
            status_code=400,
            detail="You can have a maximum of 3 bookings"
        )

    # ✅ Prevent duplicate booking
    existing_booking = bookings_collection.find_one({
        "user_name": booking.user_name,
        "flight_name": booking.flight_name,
        "source": booking.source,
        "destination": booking.destination,
        "date": booking.date,
        "status": "confirmed"
    })

    if existing_booking:
        raise HTTPException(
            status_code=400,
            detail="You have already booked this flight"
        )

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
        {
            "$inc": {"seats": -booking.seats}
        }
    )

    if update_result.modified_count == 0:
        raise HTTPException(400, "Not enough seats available")

    # ✅ Generate booking reference
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

    bookings = []

    cursor = bookings_collection.find().sort("created_at", -1).skip(skip).limit(limit)

    for booking in cursor:
        booking["_id"] = str(booking["_id"])
        bookings.append(booking)

    return {
        "count": len(bookings),
        "bookings": bookings
    }


# ✅ GET BOOKINGS BY USER
@router.get("/bookings/{user_name}")
def get_user_bookings(user_name: str):

    bookings = []

    for booking in bookings_collection.find({"user_name": user_name}):
        booking["_id"] = str(booking["_id"])
        bookings.append(booking)

    return {"bookings": bookings}


# ✅ CANCEL BOOKING (with 24-hour rule)
@router.delete("/booking/{booking_id}")
def cancel_booking(booking_id: str, reason: str):

    logger.info(f"Cancel request received for booking: {booking_id}")

    # ✅ Validate ObjectId
    try:
        booking_obj_id = ObjectId(booking_id)
    except:
        raise HTTPException(400, "Invalid booking id")

    booking = bookings_collection.find_one({"_id": booking_obj_id})

    if not booking:
        raise HTTPException(404, "Booking not found")

    if booking["status"] == "cancelled":
        raise HTTPException(400, "Booking already cancelled")

    # ✅ Safe 24-hour cancellation check
    try:
        flight_datetime = datetime.strptime(
            f"{booking.get('date')} {booking.get('time')}",
            "%Y-%m-%d %H:%M"
        )

        time_difference = flight_datetime - datetime.now()

        if time_difference.total_seconds() <= 24 * 60 * 60:
            raise HTTPException(
                400,
                "Cannot cancel booking within 24 hours of departure"
            )

    except ValueError:
        raise HTTPException(400, "Invalid date/time format in booking")

    except Exception:
        raise HTTPException(500, "Booking data missing required fields")

    # ✅ Cancel booking
    bookings_collection.update_one(
        {"_id": booking_obj_id},
        {
            "$set": {
                "status": "cancelled",
                "cancelled_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "cancel_reason": reason
            }
        }
    )

    # ✅ Restore seats
    flights_collection.update_one(
        {"_id": ObjectId(booking["flight_id"])},
        {"$inc": {"seats": booking["booked_seats"]}}
    )

    logger.info("Booking cancelled successfully")

    return {"message": "Booking cancelled successfully"}


# ✅ BOOKING SUMMARY
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

    remaining = 3 - confirmed
    if remaining < 0:
        remaining = 0

    return {
        "user_name": user_name,
        "total_bookings": total,
        "confirmed": confirmed,
        "cancelled": cancelled,
        "remaining_slots": remaining   # ✅ bonus improvement
    }
