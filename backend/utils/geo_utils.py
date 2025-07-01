from geopy.distance import geodesic

def calculate_distance(lat1, lng1, lat2, lng2):
    """Calculate distance between two points in kilometers using geodesic"""
    return geodesic((lat1, lng1), (lat2, lng2)).km