# ✈️ Travel Booking API (Full-Stack Backend Project)

A fully functional **Travel Booking System** built using **FastAPI**, containerized using **Docker**, and managed with **Git & GitHub**.  
This project simulates real-world backend operations like flight management, bookings, cancellations, and validations.

---

## 🚀 Features

### ✈️ Flight Management
- Add new flights
- Fetch available flights with filters (price, pagination)
- Search flights by source, destination, and date
- Update flight details (PUT & PATCH)
- Cancel flights with booking cascade

---

### 📦 Booking System
- Book flights with seat validation
- Prevent duplicate bookings
- Max booking limit per user
- Cancel bookings with seat restoration
- 24-hour cancellation restriction

---

### 📊 Booking Insights
- Get all bookings (pagination)
- Get bookings by user
- Booking summary:
  - Total bookings
  - Confirmed / Cancelled
  - Remaining booking slots

---

## 🏗️ Tech Stack

- **Backend:** FastAPI (Python)
- **Database:** MongoDB / Mongomock (for testing)
- **Containerization:** Docker
- **Version Control:** Git & GitHub
- **API Testing:** Swagger UI / Postman

---

## 🐳 Docker Setup

### ✅ Build Image

```bash
docker build -t travel-api .

#Run the docker container
docker run -d -p 8000:8000 travel-api

#Access API
http://localhost:8000/docs

---

API Endpoints

#Flights
POST   /flights
GET    /flights
GET    /flights/search
PUT    /flights/{flight_id}
PATCH  /flights/{flight_id}
PUT    /flights/{flight_id}/cancel

#Bookings
POST   /book
GET    /bookings
GET    /bookings/{user_name}
GET    /bookings/{user_name}/summary
DELETE /booking/{booking_id}

#Key Learnings
1. Designing RESTful APIs using FastAPI
2. Implementing business validations & constraints
3. Handling MongoDB ObjectId correctly
4. Debugging real-world issues (CORS, Docker, Git)
5. Using Docker for containerized deployments
6. Managing Git workflows (branching, PR, merge)
 
 #Project Structure
travel-booking-api/
│
├── routers/
│   ├── flights.py
│   └── bookings.py
│
├── models/
│   ├── flight.py
│   └── booking.py
│
├── database/
│   └── connection.py
│
├── main.py
├── Dockerfile
├── requirements.txt
└── README.md

#Future Enhancements
🔐 User authentication (JWT)
💳 Payment integration
📅 Advanced filtering (date, price range)
🌐 Frontend (React UI)
☁️ Deployment (AWS / Azure)

#Author
Madhusudhan M

#Notes
This project was built as part of backend engineering practice focusing on:
1. Real-world API design
2. Docker & DevOps basics
3. Git collaboration workflows