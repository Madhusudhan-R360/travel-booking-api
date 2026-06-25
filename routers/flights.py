from fastapi import APIRouter, HTTPException
from datetime import datetime
from bson import ObjectId
from typing import List, Optional
from bson.errors import InvalidId

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
        raise HTTPException(400, "Flight already exists")

    try:
        flight_datetime = datetime.strptime(
            f"{flight.date} {flight.time}",
            "%Y-%m-%d %H:%M"
        )

        if flight_datetime < datetime.now():
            raise HTTPException(400, "Cannot add past flight")

    except ValueError:
        raise HTTPException(400, "Invalid date/time format")

    data = flight.dict()
    data["status"] = "active"

    if price > 100000:
        raise HTTPException(400, "Price too high")

    result = flights_collection.insert_one(data)
    return{"message":"Flight added succesfully"}
    return {"id": str(result.inserted_id)}


# ✅ Get Flights
@router.get("/flights", response_model=List[FlightResponse])
def get_flights(limit: int = 5, skip: int = 0,
                sort: Optional[str] = None,
                max_price: Optional[int] = None):

    query = {"status": "active", "seats": {"$gt": 0}}

    if max_price:
        query["price"] = {"$lte": max_price}

    cursor = flights_collection.find(query)

    if sort == "price_asc":
        cursor = cursor.sort("price", 1)
    elif sort == "price_desc":
        cursor = cursor.sort("price", -1)

    cursor = cursor.skip(skip).limit(limit)

    flights = []
    for f in cursor:
        f["_id"] = str(f["_id"])

        f["availability"] = (
            f"Only {f.get('seats')} left"
            if f.get("seats", 0) <= 3 else "Available"
        )

        flights.append(f)

    return flights


# ✅ Search Flights
@router.get("/flights/search")
def search_flights(source: str, destination: str, date: str):

    if source.lower() == destination.lower():
        raise HTTPException(400, "Same source & destination")

    query = {
        "source": {"$regex": f"^{source}$", "$options": "i"},
        "destination": {"$regex": f"^{destination}$", "$options": "i"},
        "date": date,
        "status": "active",
        "seats": {"$gt": 0}
    }

    flights = []

    for f in flights_collection.find(query):
        f["_id"] = str(f["_id"])

        f["availability"] = (
            f"Only {f.get('seats')} left"
            if f.get("seats", 0) <= 3 else "Available"
        )

        flights.append(f)

    return {"flights": flights} if flights else {"message": "No flights found"}


# ✅ Update Flight
@router.put("/flights/{flight_id}")
def update_flight(flight_id: str, flight: FlightCreate):

    try:
        obj_id = ObjectId(flight_id)
    except InvalidId:
        raise HTTPException(400, "Invalid ID format")

    result = flights_collection.update_one(
        {"_id": obj_id},
        {"$set": flight.dict()}
    )

    if result.matched_count == 0:
        raise HTTPException(404, "Flight not found")

    return {"message": "Updated"}


# ✅ Partial Update Flight
@router.patch("/flights/{flight_id}")
def update_flight_partial(
    flight_id: str,
    price: Optional[int] = None,
    seats: Optional[int] = None
):

    try:
        obj_id = ObjectId(flight_id)
    except InvalidId:
        raise HTTPException(400, "Invalid flight ID")

    update_data = {}

    if price is not None:
        if price <= 0:
            raise HTTPException(400, "Price must be greater than 0")
        update_data["price"] = price

    if seats is not None:
        if seats <= 0:
            raise HTTPException(400, "Seats must be greater than 0")
        update_data["seats"] = seats

    if not update_data:
        raise HTTPException(400, "No fields provided to update")

    result = flights_collection.update_one(
        {"_id": obj_id},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(404, "Flight not found")

    return {"message": "Flight updated partially"}

# ✅ Cancel Flight
@router.put("/flights/{flight_id}/cancel")
def cancel_flight(flight_id: str):

    try:
        obj_id = ObjectId(flight_id)
    except InvalidId:
        raise HTTPException(400, "Invalid ID")

    result = flights_collection.update_one(
        {"_id": obj_id},
        {"$set": {"status": "cancelled"}}
    )

    if result.matched_count == 0:
        raise HTTPException(404, "Flight not found")

    bookings_collection.update_many(
        {"flight_id": str(obj_id)},
        {"$set": {"status": "cancelled"}}
    )

    return {"message": "Flight cancelled"}