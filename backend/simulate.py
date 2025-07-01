import random
from datetime import datetime, timedelta, timezone
from app import app, db
from models import Rider, Driver, Ride
from services.ride_service import RideService
from faker import Faker

ride_service = RideService()
fake = Faker()

def random_coords(center_lat=12.9716, center_lng=77.5946, spread=0.05):
    return (
        center_lat + random.uniform(-spread, spread),
        center_lng + random.uniform(-spread, spread)
    )

def seed_users():
    print("Seeding riders and drivers...")
    for i in range(10):
        lat, lng = random_coords()
        rider = Rider(name=fake.name(), current_lat=lat, current_lng=lng)
        db.session.add(rider)

    for i in range(15):
        lat, lng = random_coords()
        driver = Driver(name=fake.name(), current_lat=lat, current_lng=lng, is_available=True)
        db.session.add(driver)

    db.session.commit()

def simulate_rides(days=2):
    print("Simulating rides...")
    riders = Rider.query.all()

    for day in range(days):
        for rider in riders:
            for _ in range(random.randint(1, 2)):
                pickup_lat, pickup_lng = random_coords()
                drop_lat, drop_lng = random_coords()

                ride = Ride(
                    rider_id=rider.id,
                    pickup_lat=pickup_lat,
                    pickup_lng=pickup_lng,
                    drop_lat=drop_lat,
                    drop_lng=drop_lng,
                    created_at=datetime.now(timezone.utc) - timedelta(days=(1 - day)),
                    status='create_ride'
                )
                db.session.add(ride)
    db.session.commit()

def simulate_transitions():
    print("Simulating ride transitions...")
    rides = Ride.query.filter(Ride.status == 'driver_assigned').all()

    for ride in rides:
        now = datetime.now(timezone.utc)
        ride.driver_at_location_time = now + timedelta(minutes=2)
        ride.start_ride_time = now + timedelta(minutes=5)
        ride.end_ride_time = now + timedelta(minutes=20)

        ride.status = 'end_ride'
        ride_service.calculate_fare(ride)

    db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()
        from services.pricing_service import PricingService

        pricing_service = PricingService()
        default_pricing = [
            {'key': 'base_fare', 'value': 50},
            {'key': 'rate_per_km', 'value': 10},
            {'key': 'rate_per_minute', 'value': 1},
            {'key': 'waiting_charge_per_minute', 'value': 2}
        ]

        for item in default_pricing:
            pricing_service.update_pricing_config(item['key'], item['value'])

        seed_users()
        simulate_rides()
        print("✅ Rides created. Wait a few seconds for background driver assignment.")
        input("Press Enter to simulate transitions after assignment...")
        simulate_transitions()
        print("✅ Ride transitions complete.")
