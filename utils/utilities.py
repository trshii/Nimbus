# pyright: strict

from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple, Optional
from enum import auto, Enum

type coord = Tuple[float, float]

@dataclass
class Coordinate:
    lon: float
    lat: float
    idx: Optional[int]
    name: Optional[str]
    eta: Optional[datetime]
    
    @property
    def coord_list(self) -> list[float]:
        return [self.lon, self.lat]
    
@dataclass
class Waypoint:
    location: Coordinate
    rain_probability: float
    eta: datetime
    
@dataclass 
class RoutePlan:
    origin: str
    destination: str
    departure_time: datetime
    waypoints: List[Waypoint]
    full_geometry: List[Tuple[float, float]]
    
class TravelMode(Enum):
    DRIVING = auto()
    CYCLING = auto()
    WALKING = auto()