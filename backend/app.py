from flask import Flask, jsonify, request
from database import db
import requests
from models import Driver, Rider, Ride, PricingConfig
from services.driver_service import DriverService
from services.ride_service import RideService
from services.pricing_service import PricingService
from utils.background_jobs import init_scheduler
import config as config
from flask_cors import CORS

app = Flask(__name__)
# Configure CORS

CORS(app, resources={
    r"/*": {
        "origins": "http://127.0.0.1:5500",
        "supports_credentials": True
    }
})
app.config.from_object(config.Config)
db.init_app(app)

# Initialize scheduler for background jobs
scheduler = init_scheduler(app)

# Services
driver_service = DriverService()
ride_service = RideService()
pricing_service = PricingService()


@app.route('/')
def home():
    return "Ride Service Backend"

@app.route('/rides/<int:ride_id>/update_status', methods=['OPTIONS'])
def update_ride_status_options(ride_id):
    response = jsonify({'message': 'Preflight request accepted'})
    response.headers.add('Access-Control-Allow-Origin', 'http://127.0.0.1:5500')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    return response, 200

# Driver endpoints
@app.route('/drivers', methods=['GET'])
def get_drivers():
    drivers = Driver.query.all()
    return jsonify([driver.to_dict() for driver in drivers])

@app.route('/drivers/<int:driver_id>', methods=['GET'])
def get_driver(driver_id):
    driver = Driver.query.get_or_404(driver_id)
    return jsonify(driver.to_dict())

@app.route('/drivers', methods=['POST'])
def create_driver():
    data = request.get_json()
    driver = driver_service.create_driver(data)
    return jsonify(driver.to_dict()), 201

# Rider endpoints
@app.route('/riders', methods=['GET'])
def get_riders():
    riders = Rider.query.all()
    return jsonify([rider.to_dict() for rider in riders])

@app.route('/riders/<int:rider_id>', methods=['GET'])
def get_rider(rider_id):
    rider = Rider.query.get_or_404(rider_id)
    return jsonify(rider.to_dict())

@app.route('/riders', methods=['POST'])
def create_rider():
    data = request.get_json()
    rider = Rider(
        name=data['name'],
        current_lat=data.get('current_lat', 0),
        current_lng=data.get('current_lng', 0)
    )
    db.session.add(rider)
    db.session.commit()
    return jsonify(rider.to_dict()), 201

# Ride endpoints
@app.route('/rides', methods=['GET'])
def get_rides():
    rides = Ride.query.all()
    return jsonify([ride.to_dict() for ride in rides])

@app.route('/rides/<int:ride_id>', methods=['GET'])
def get_ride(ride_id):
    ride = Ride.query.get_or_404(ride_id)
    return jsonify(ride.to_dict())

@app.route('/rides', methods=['POST'])
def create_ride():
    data = request.get_json()
    ride = ride_service.create_ride(data)
    return jsonify(ride.to_dict()), 201

@app.route('/rides/<int:ride_id>/update_status', methods=['POST'])
def update_ride_status(ride_id):
    data = request.get_json()
    ride = ride_service.update_ride_status(ride_id, data['status'])
    response = jsonify(ride.to_dict())
    response.headers.add('Access-Control-Allow-Origin', 'http://127.0.0.1:5500')
    return response

# Pricing endpoints
@app.route('/pricing', methods=['GET'])
def get_pricing_configs():
    configs = PricingConfig.query.all()
    return jsonify([config.to_dict() for config in configs])

@app.route('/pricing', methods=['POST'])
def update_pricing_config():
    data = request.get_json()
    config = pricing_service.update_pricing_config(data['key'], data['value'])
    return jsonify(config.to_dict()), 201


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Initialize default pricing if not exists
        if not PricingConfig.query.first():
            default_pricing = [
                {'key': 'base_fare', 'value': 50},
                {'key': 'rate_per_km', 'value': 10},
                {'key': 'rate_per_minute', 'value': 1},
                {'key': 'waiting_charge_per_minute', 'value': 2}
            ]
            for item in default_pricing:
                pricing_service.update_pricing_config(item['key'], item['value'])
    app.run(debug=True)