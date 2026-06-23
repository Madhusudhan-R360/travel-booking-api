from fastapi import APIRouter, HTTPException
from datetime import datetime
from bson import ObjectId
from typing import List

from models.flight import FlightResponse, FlightCreate
from database.connection import flights_collection, bookings_collection

router = APIRouter()


# ✅ Create Flight
@router.post("/flights")
def add_flight(flight: FlightCreate):

    existing = flights_collection.find_one({
        "flight_name": flight.flight_name,
        "source": flight.source,
        "destination": flight.destination,
        "date": flight.date,
        "status": "active"
    })

    if existing:
        raise HTTPException(400, "Flight already exists for this route and date")

    try:
        flight_datetime = datetime.strptime(
            f"{flight.date} {flight.time}",
            "%Y-%m-%d %H:%M"
        )

        if flight_datetime < datetime.now():
            raise HTTPException(400, "Cannot add past flight")

    except ValueError:
        raise HTTPException(400, "Invalid date/time format")

    flight_data = flight.dict()
    flight_data["status"] = "active"

    result = flights_collection.insert_one(flight_data)

    return {
        "message": "Flight added",
        "id": str(result.inserted_id)
    }


# ✅ Get Flights
@router.get("/flights", response_model=List[FlightResponse])
def get_flights(limit: int = 5, skip: int = 0, sort: str = None, max_price: int = None):

    query = {
        "status": "active",
        "seats": {"$gt": 0}
    }

    if max_price is not None:
        query["price"] = {"$lte": max_price}

    sort_order = None
    if sort == "price_asc":
        sort_order = ("price", 1)
    elif sort == "price_desc":
        sort_order = ("price", -1)

    flights = []
    cursor = flights_collection.find(query)

    if sort_order:
        cursor = cursor.sort(*sort_order)

    cursor = cursor.skip(skip).limit(limit)

    for flight in cursor:
        flight.pop("_id", None)

        # ✅ availability info
        if flight["seats"] <= 3:
            flight["availability"] = f"Only {flight['seats']} seats left"
        else:
            flight["availability"] = "Available"

        flights.append(flight)

    return flights   # ✅ IMPORTANT


# ✅ Search Flights
@router.get("/flights/search/")
def search_flights(source: str, destination: str, date: str):

    if source.lower() == destination.lower():
        raise HTTPException(400, "Source and destination cannot be the same")

    query = {
        "source": {"$regex": f"^{source}$", "$options": "i"},
        "destination": {"$regex": f"^{destination}$", "$options": "i"},
        "date": date,
        "status": "active",
        "seats": {"$gt": 0}
    }

    flights = []

    for flight in flights_collection.find(query):
        flight.pop("_id", None)

        if flight["seats"] <= 3:
            flight["availability"] = f"Only {flight['seats']} seats left"
        else:
            flight["availability"] = "Available"

        flights.append(flight)

    if not flights:
        return {"message": "No flights found for this route on given date"}

    return {"flights": flights}   # ✅ IMPORTANT


# ✅ Full Update
@router.put("/flights/{flight_id}")
def update_flight(flight_id: str, flight: FlightCreate):

    try:
        obj_id = ObjectId(flight_id)
    except:
        raise HTTPException(400, "Invalid flight ID")

    update_data = flight.dict()
    update_data["status"] = "active"

    result = flights_collection.update_one(
        {"_id": obj_id},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(404, "Flight not found")

    return {"message": "Flight updated successfully"}


# ✅ Partial Update
@router.patch("/flights/{flight_id}")
def update_flight_partial(flight_id: str, price: int = None, seats: int = None):

    try:
        obj_id = ObjectId(flight_id)
    except:
        raise HTTPException(400, "Invalid flight ID")

    update_data = {}

    if price is not None:
        if price <= 0:
            raise HTTPException(400, "Price must be > 0")
        update_data["price"] = price

    if seats is not None:
        if seats <= 0:
            raise HTTPException(400, "Seats must be > 0")
        update_data["seats"] = seats

    if not update_data:
        raise HTTPException(400, "No valid fields to update")

    result = flights_collection.update_one(
        {"_id": obj_id},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(404, "Flight not found")

    return {"message": "Flight updated partially"}


# ✅ Cancel Flight (with booking cascade)
@router.put("/flights/{flight_id}/cancel")
def cancel_flight(flight_id: str):

    try:
        flight_object_id = ObjectId(flight_id)
    except:
        raise HTTPException(400, "Invalid flight ID")

    result = flights_collection.update_one(
        {"_id": flight_object_id},
        {
            "$set": {
                "status": "cancelled",
                "cancelled_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
    )

    if result.matched_count == 0:
        raise HTTPException(404, "Flight not found")

    # ✅ Cancel all related bookings
    bookings_collection.update_many(
        {
            "flight_id": str(flight_object_id)
        },
        {
            "$set": {
                "status": "cancelled",
                "cancel_reason": "Flight cancelled by airline",
                "cancelled_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
    )

    return {"message": "Flight cancelled successfully"}
