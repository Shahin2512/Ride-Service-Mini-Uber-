from datetime import datetime , timezone
from database import db
from sqlalchemy import Column, DateTime 

class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    current_lat = db.Column(db.Float, nullable=False)
    current_lng = db.Column(db.Float, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(20), default='available')  # available, in_ride, offline
    cancel_count = db.Column(db.Integer, default=0)
    last_cancel_time = db.Column(db.DateTime)
    
    rides = db.relationship('Ride', backref='driver', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'current_lat': self.current_lat,
            'current_lng': self.current_lng,
            'is_available': self.is_available,
            'status': self.status,
            'cancel_count': self.cancel_count
        }

class Rider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    current_lat = db.Column(db.Float)
    current_lng = db.Column(db.Float)
    
    rides = db.relationship('Ride', backref='rider', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'current_lat': self.current_lat,
            'current_lng': self.current_lng
        }

class Ride(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rider_id = db.Column(db.Integer, db.ForeignKey('rider.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'))
    pickup_lat = db.Column(db.Float, nullable=False)
    pickup_lng = db.Column(db.Float, nullable=False)
    drop_lat = db.Column(db.Float, nullable=False)
    drop_lng = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='create_ride')  # create_ride, driver_assigned, driver_at_location, start_ride, end_ride, cancelled
    #created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    driver_assigned_time = db.Column(db.DateTime)
    driver_at_location_time = db.Column(db.DateTime)
    start_ride_time = db.Column(db.DateTime)
    end_ride_time = db.Column(db.DateTime)
    distance = db.Column(db.Float)  # in km
    duration = db.Column(db.Float)  # in minutes
    waiting_time = db.Column(db.Float)  # in minutes
    fare = db.Column(db.Float)
    
    def to_dict(self):
        return {
            'id': self.id,
            'rider_id': self.rider_id,
            'driver_id': self.driver_id,
            'pickup_lat': self.pickup_lat,
            'pickup_lng': self.pickup_lng,
            'drop_lat': self.drop_lat,
            'drop_lng': self.drop_lng,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'driver_assigned_time': self.driver_assigned_time.isoformat() if self.driver_assigned_time else None,
            'driver_at_location_time': self.driver_at_location_time.isoformat() if self.driver_at_location_time else None,
            'start_ride_time': self.start_ride_time.isoformat() if self.start_ride_time else None,
            'end_ride_time': self.end_ride_time.isoformat() if self.end_ride_time else None,
            'distance': self.distance,
            'duration': self.duration,
            'waiting_time': self.waiting_time,
            'fare': self.fare
        }

class PricingConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Float, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value
        }