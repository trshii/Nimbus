# pyright: strict

from dataclasses import dataclass
from datetime import datetime
from typing import List
from enum import auto, Enum

@dataclass
class Coordinate:
    longitude: float
    latitude: float
    
@dataclass
class Waypoint:
    location: Coordinate
    eta: datetime
    rain_probability: float
    
@dataclass 
class RoutePlan:
    origin: str
    destination: str
    departure_time: datetime
    waypoints: List[Waypoint]
    
class TravelMode(Enum):
    DRIVING = auto()
    CYCLING = auto()
    WALKING = auto()