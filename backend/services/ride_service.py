from models import Ride,Driver, db
from datetime import datetime , timezone
from services.driver_service import DriverService
from services.pricing_service import PricingService

driver_service = DriverService()
pricing_service = PricingService()

class RideService:
    def create_ride(self, data):
        ride = Ride(
            rider_id=data['rider_id'],
            pickup_lat=data['pickup_lat'],
            pickup_lng=data['pickup_lng'],
            drop_lat=data['drop_lat'],
            drop_lng=data['drop_lng'],
            status='create_ride'
        )
        db.session.add(ride)
        db.session.commit()
        return ride
    
    def update_ride_status(self, ride_id, new_status):
        ride = Ride.query.get(ride_id)
        if not ride:
            return None
        
        if new_status == 'driver_assigned':
            ride.driver_assigned_time = datetime.now(timezone.utc)
        elif new_status == 'driver_at_location':
            ride.driver_at_location_time = datetime.now(timezone.utc)
        elif new_status == 'start_ride':
            ride.start_ride_time = datetime.now(timezone.utc)
        elif new_status == 'end_ride':
            ride.end_ride_time = datetime.now(timezone.utc)
            self.calculate_fare(ride)
            # Mark driver as available
            if ride.driver_id:
                driver = Driver.query.get(ride.driver_id)
                if driver:
                    driver.is_available = True
                    db.session.commit()
        
        ride.status = new_status
        db.session.commit()
        return ride
    
    def calculate_fare(self, ride):
        if not all([ride.start_ride_time, ride.end_ride_time, ride.driver_at_location_time]):
            return 0
        
        # Calculate duration in minutes
        duration = (ride.end_ride_time - ride.start_ride_time).total_seconds() / 60
        ride.duration = duration
        
        # Calculate waiting time in minutes
        if ride.driver_at_location_time and ride.start_ride_time:
            waiting_time = (ride.start_ride_time - ride.driver_at_location_time).total_seconds() / 60
            ride.waiting_time = waiting_time
        
        # Simulate distance (in a real app, we'd use actual distance)
        ride.distance = self.calculate_distance(
            ride.pickup_lat, ride.pickup_lng,
            ride.drop_lat, ride.drop_lng
        )
        
        # Calculate fare
        fare = pricing_service.calculate_fare(
            distance=ride.distance,
            duration=ride.duration,
            waiting_time=ride.waiting_time
        )
        ride.fare = fare
        db.session.commit()
        return fare
    
    def calculate_distance(self, lat1, lng1, lat2, lng2):
        # Simplified distance calculation (Haversine would be better)
        return ((lat1 - lat2)**2 + (lng1 - lng2)**2)**0.5 * 111  # approx km