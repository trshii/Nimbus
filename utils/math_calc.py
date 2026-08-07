# pyright: strict

import math
from typing import List
from utils.utilities import Coordinate

def haversine_distance(p1: Coordinate, p2: Coordinate) -> float:
    """Calculates the distance between two coordinates in kilometers."""
    R = 6371.0
    
    lon1, lat1 = p1.lon, p1.lat
    lon2, lat2 = p2.lon, p2.lat
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    
    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def filter_waypoints(
    coordinates: List[Coordinate], 
    threshold_km: float = 2.0
    ) -> List[Coordinate]:
    
    if not coordinates:
        return []
    
    milestones = [coordinates[0]]
    last_kept_point = coordinates[0]
    
    for i in range(1, len(coordinates) - 1):
        current_point = coordinates[i]
        
        dist = haversine_distance(last_kept_point, current_point)
        
        if dist >= threshold_km:
            milestones.append(current_point)
            last_kept_point = current_point
            
    if len(coordinates) > 1 and coordinates[-1] != last_kept_point:
        milestones.append(coordinates[-1])

    return milestones