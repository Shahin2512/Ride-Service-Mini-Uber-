# 🚖 Ride Service Backend – Mini Uber Clone

A simplified ride-hailing backend system built with Flask that simulates the complete lifecycle of a ride, including driver allocation, pricing, and performance metrics.  
This project demonstrates backend logic for ride creation, driver matching, dynamic fare computation, and monitoring.

---

## 🛠 Tech Stack

| Layer        | Technology          |
|-------------|----------------------|
| Backend API | **Flask (Python)**   |
| Database    | **NeonDB / PostgreSQL** via SQLAlchemy |
| Scheduler   | **APScheduler** for background jobs |
| Frontend    | **HTML + JS + CSS** (static) |
| ORM         | **SQLAlchemy**       |
| Geolocation | Approximate lat/lng math (or optionally Haversine) |

## 🔧 Setup & Run Instructions

![Screenshot 2025-07-02 005458](https://github.com/user-attachments/assets/101b42b8-90e0-4828-ae0d-126591949f1e)


### Clone the Repository

```bash
git clone https://github.com/username/ride-service.git
cd ride-service/backend 

pip install -r ../requirements.txt
Run the Backend: 
python app.py
python simulate.py



