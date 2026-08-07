# pyright: strict

from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple
from enum import auto, Enum

type coord = Tuple[float, float]

@dataclass
class Coordinate:
    lon: float
    lat: float
    
    @property
    def coord_list(self) -> list[float]:
        return [self.lon, self.lat]
    
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