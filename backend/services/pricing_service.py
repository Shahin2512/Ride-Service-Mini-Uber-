from models import PricingConfig, db

class PricingService:
    def update_pricing_config(self, key, value):
        config = PricingConfig.query.filter_by(key=key).first()
        if config:
            config.value = value
        else:
            config = PricingConfig(key=key, value=value)
            db.session.add(config)
        db.session.commit()
        return config
    
    def get_pricing_config(self, key):
        config = PricingConfig.query.filter_by(key=key).first()
        return config.value if config else None
    
    def calculate_fare(self, distance, duration, waiting_time=0):
        base_fare = float(self.get_pricing_config('base_fare') or 50)
        rate_per_km = float(self.get_pricing_config('rate_per_km') or 10)
        rate_per_minute = float(self.get_pricing_config('rate_per_minute') or 1)
        waiting_charge_per_minute = float(self.get_pricing_config('waiting_charge_per_minute') or 2)
        
        fare = (
            base_fare +
            (distance * rate_per_km) +
            (duration * rate_per_minute) +
            (waiting_time * waiting_charge_per_minute)
        )
        return round(fare, 2)