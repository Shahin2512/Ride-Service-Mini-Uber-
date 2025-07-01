from apscheduler.schedulers.background import BackgroundScheduler
from models import Ride, Driver, db
from services.driver_service import DriverService
from datetime import datetime, timezone

driver_service = DriverService()

def assign_drivers_job(app):
    with app.app_context():
        print("[Scheduler] Running driver assignment...")
        unassigned_rides = Ride.query.filter_by(status='create_ride').all()
        if not unassigned_rides:
            print("[Scheduler] No rides waiting for driver assignment.")
            return
        assignments_done = 0
        max_assignments = 10
        
        for ride in unassigned_rides:
            if assignments_done >= max_assignments:
                break
            radius_km = 2
            max_radius_km = 10
            driver_found = False

            while radius_km <= max_radius_km and not driver_found:
                eligible_drivers = driver_service.get_eligible_drivers(
                    rider_id=ride.rider_id,
                    pickup_lat=ride.pickup_lat,
                    pickup_lng=ride.pickup_lng,
                    radius_km=radius_km
                )

                for driver in eligible_drivers:
                    if driver.status != 'in_ride':
                        ride.driver_id = driver.id
                        ride.status = 'driver_assigned'
                        ride.driver_assigned_time = datetime.now(timezone.utc)
                        
                        driver.is_available = False
                        driver.status = 'in_ride'

                        db.session.commit()
                        print(f"[Scheduler] Driver {driver.id} assigned to Ride {ride.id}")
                        driver_found = True
                        assignments_done += 1
                        break

                radius_km += 2


def init_scheduler(app):
    scheduler = BackgroundScheduler()
    # Wrap the job in a lambda to pass the app
    scheduler.add_job(lambda: assign_drivers_job(app), trigger="interval", seconds=10)
    scheduler.start()
    return scheduler
