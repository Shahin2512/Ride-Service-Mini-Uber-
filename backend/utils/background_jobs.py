from apscheduler.schedulers.background import BackgroundScheduler
from models import Ride, Driver, db
from services.driver_service import DriverService
from datetime import datetime, timedelta , timezone
import time

driver_service = DriverService()

def assign_drivers_to_rides(app):
    """Assign drivers to unassigned rides"""
    with app.app_context():
        unassigned_rides = Ride.query.filter_by(status='create_ride').all()
        
        for ride in unassigned_rides:
            
            # time_since_creation = (datetime.now(timezone.utc) - ride.created_at).total_seconds()
            # search_radius_km = 2 + (2 * (time_since_creation // 10)) 
            if ride.created_at.tzinfo is None:
                created_at = ride.created_at.replace(tzinfo=timezone.utc)
            else:
                created_at = ride.created_at
                
            time_since_creation = (datetime.now(timezone.utc) - created_at).total_seconds()
            search_radius_km = 2 + (2 * (time_since_creation // 10))
            
            if search_radius_km > 10:  # Max search radius
                continue
            
            eligible_drivers = driver_service.get_eligible_drivers(
                ride.rider_id,
                ride.pickup_lat, ride.pickup_lng,
                search_radius_km
            )
            
            if eligible_drivers:
                # Assign first available driver
                driver = eligible_drivers[0]
                ride.driver_id = driver.id
                ride.status = 'driver_assigned'
                ride.driver_assigned_time = datetime.now(timezone.utc)
                
                # Mark driver as unavailable
                driver.is_available = False
                db.session.commit()

def init_scheduler(app):
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=assign_drivers_to_rides,
        args=[app],
        trigger="interval", 
        seconds=5
    )
    scheduler.start()
    return scheduler
    