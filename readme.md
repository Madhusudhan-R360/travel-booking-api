## ✅ Update

Added feature branch workflow demonstration.


Travel Flight Booking Backend (FastAPI + MongoDB)

📌 Project Overview
This project is a backend system for a flight booking platform built using FastAPI and MongoDB (mongomock).
It simulates real-world airline booking functionality, including flight management, booking workflows, seat handling, and data validation.
The objective of this project is to gain hands-on experience in backend development, focusing on:

REST API design
Database interactions
Business logic implementation
System-level problem solving


🚀 Tech Stack

Backend Framework: FastAPI
Database: MongoDB (mongomock)
Language: Python
Architecture: Modular (routers, models, database, utils)


🏗️ Project Structure
project/
│
├── main.py
├── models/
│   ├── flight.py
│   └── booking.py
│
├── routers/
│   ├── flights.py
│   └── bookings.py
│
├── database/
│   └── connection.py
│
├── utils/
│   └── logger.py


✅ Core Features
✈️ Flight Management

Create Flight (POST /flights)
Get Flights (GET /flights)

Pagination (limit, skip)
Sorting (price ascending / descending)
Filtering (max price)


Search Flights (GET /flights/search)

Based on source, destination, and date
Case-insensitive search (regex)


Update Flight

Full update (PUT)
Partial update (PATCH)


Cancel Flight (PUT /flights/{id}/cancel)

Soft delete using status
Cancellation timestamp tracking


📦 Booking System

Book Flight (POST /book)
Get All Bookings (GET /bookings)
Get User Bookings (GET /bookings/{user})
Cancel Booking (DELETE /booking/{id})

Status update (confirmed → cancelled)
Seat restoration
Cancellation timestamp + reason




🧠 Business Logic Implemented

Prevent duplicate flights
Prevent booking cancelled flights
Prevent booking past flights
Limit number of bookings per user
Prevent duplicate bookings for same flight
Validate inputs (price, seats, route)
Maintain seat availability consistency


⚙️ Advanced Features

✅ Pydantic Models

FlightCreate, Booking → Input validation
FlightResponse → Controlled API output

Ensures:

Type validation
Data integrity
Structured API contracts


✅ Atomic Seat Updates
Python"$inc": {"seats": -booking.seats}Show more lines

Prevents race conditions
Ensures no overbooking
Maintains consistency during concurrent requests


✅ Denormalization
Flight details are embedded inside bookings:

Avoids additional DB lookups
Improves read performance


✅ Logging
Implemented using Python logging module:

Tracks API events
Helps debugging
Enables monitoring


✅ Indexing
Indexes added on:

source
destination
date
price
user_name

Improves query performance and retrieval speed.

✅ Pagination
Python.skip() and .limit()Show more lines

Efficient handling of large datasets
Supports scalable data retrieval


✅ Sorting & Filtering

Sort flights by price
Filter based on price range

Improves user search experience.

✅ Case-Insensitive Search
Implemented using MongoDB regex:
Python"$regex": "^value$", "$options": "i"Show more lines

Allows flexible search input
Handles casing variations


✅ Status-Based Design

Flights → active / cancelled
Bookings → confirmed / cancelled

Ensures proper lifecycle management.

✅ Timestamp Tracking

created_at → booking creation
cancelled_at → cancellation tracking

Supports audit and debugging.

📊 API Endpoints
✈️ Flights

POST /flights
GET /flights
GET /flights/search
PUT /flights/{id}
PATCH /flights/{id}
PUT /flights/{id}/cancel


📦 Bookings

POST /book
GET /bookings
GET /bookings/{user}
DELETE /booking/{id}


⚙️ Utility

GET / → Service welcome endpoint
GET /health → Health status check


🛡️ Error Handling
Uses HTTPException with proper status codes:

400 → Invalid request
404 → Resource not found

Ensures consistent API responses.

🚀 Performance Considerations

Pagination for large datasets
MongoDB indexing for faster queries
Atomic operations for consistency
Optimized query construction


🧠 Key Learnings

Designing REST APIs with FastAPI
Structuring modular backend applications
Working with MongoDB collections
Implementing business rules and validations
Handling concurrent updates safely
Optimizing queries using indexing


⚠️ Note
This project uses mongomock (in-memory MongoDB) due to environment constraints.
For production:

Replace with real MongoDB (Atlas/local)
Add authentication & authorization
Secure API endpoints
Use environment configuration


📌 Future Improvements

Implement JWT-based authentication
Add role-based access control
Introduce service layer architecture
Integrate with real MongoDB
Deploy using Docker / Cloud


✅ Final Summary
This project demonstrates a complete backend system for flight booking with:

Flight lifecycle management
Booking workflows
Data validation and constraints
Performance optimizations
Clean modular architecture