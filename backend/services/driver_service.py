from models import Driver, Ride, db
from datetime import datetime, timedelta , timezone

class DriverService:
    def create_driver(self, data):
        driver = Driver(
            name=data['name'],
            current_lat=data.get('current_lat', 0),
            current_lng=data.get('current_lng', 0),
            is_available=data.get('is_available', True)
        )
        db.session.add(driver)
        db.session.commit()
        return driver
    
    def get_available_drivers(self):
        return Driver.query.filter_by(is_available=True).all()
    
    def update_driver_availability(self, driver_id, is_available):
        driver = Driver.query.get(driver_id)
        if driver:
            driver.is_available = is_available
            db.session.commit()
        return driver
    
    def increment_cancel_count(self, driver_id):
        driver = Driver.query.get(driver_id)
        if driver:
            driver.cancel_count += 1
            driver.last_cancel_time = datetime.now(timezone.utc)
            db.session.commit()
        return driver
    
    def get_eligible_drivers(self, rider_id, pickup_lat, pickup_lng, radius_km):
        """Get drivers eligible for assignment based on rules"""
        # Get drivers who:
        # 1. Are available
        # 2. Haven't had a ride with this rider in last 30 minutes
        # 3. Haven't cancelled last 2 rides
        
        thirty_minutes_ago = datetime.now(timezone.utc) - timedelta(minutes=30)
        
        # Get drivers who had recent rides with this rider
        recent_drivers_subquery = db.session.query(Ride.driver_id).filter(
            Ride.rider_id == rider_id,
            Ride.end_ride_time >= thirty_minutes_ago
        ).subquery()
        
        # Get drivers who cancelled last 2 rides
        high_cancel_drivers = [d.id for d in Driver.query.filter(
            Driver.cancel_count >= 2,
            Driver.last_cancel_time >= thirty_minutes_ago
        ).all()]
        
        # Get available drivers not in the above lists
        eligible_drivers = Driver.query.filter(
            Driver.is_available == True,
            Driver.id.notin_(recent_drivers_subquery),
            Driver.id.notin_(high_cancel_drivers)
        ).all()
        
        # Filter by distance (simplified for this example)
        # In a real app, we'd use geospatial queries
        eligible_with_distance = []
        for driver in eligible_drivers:
            distance = self.calculate_distance(
                pickup_lat, pickup_lng,
                driver.current_lat, driver.current_lng
            )
            if distance <= radius_km:
                eligible_with_distance.append((driver, distance))
        
        # Sort by distance
        eligible_with_distance.sort(key=lambda x: x[1])
        return [driver for driver, distance in eligible_with_distance]
    
    def calculate_distance(self, lat1, lng1, lat2, lng2):
        # Simplified distance calculation (Haversine would be better)
        return ((lat1 - lat2)**2 + (lng1 - lng2)**2)**0.5 * 111  # approx km