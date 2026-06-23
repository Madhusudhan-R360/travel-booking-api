import mongomock

client = mongomock.MongoClient()
db = client["travel_db"]

flights_collection = db["flights"]
bookings_collection = db["bookings"]

# ✅ Indexes for faster queries

flights_collection.create_index("source")
flights_collection.create_index("destination")
flights_collection.create_index("date")
flights_collection.create_index("price")

bookings_collection.create_index("user_name")