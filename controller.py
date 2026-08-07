# pyright: strict

import polyline
from services.route_provider import RouteProvider
from services.weather_provider import WeatherProvider
from utils.math_calc import filter_waypoints
from utils.utilities import *
from typing import *

class MainController:
    def __init__(self, api_key: str) -> None:
        self.origin: Coordinate = Coordinate(121.0676, 14.5542)
        self.destination: Coordinate = Coordinate(121.0633, 14.6549)
        self.mode: TravelMode = TravelMode.DRIVING
        self.api_key = api_key
        self.route_coord_list: List[Coordinate] = []
        
    def get_route(self) -> None:
        route_api = RouteProvider()
        self.route_plan: Dict[str, Any] | None = route_api.get_open_route(
                                                    self.api_key, 
                                                    self.mode, 
                                                    self.origin.coord_list, 
                                                    self.destination.coord_list
                                                    )
        
        if self.route_plan is None:
            raise ValueError("Route not fetched properly!")
        
        # convert route plan geometry polyline to List[Tuple[lon, lat]]
        
        encoded_geometry = self.route_plan['routes'][0]['geometry']
        decoded_geometry: List[coord] = polyline.decode(encoded_geometry)
        for lon, lat in decoded_geometry:
            point = Coordinate(lon, lat)
            self.route_coord_list.append(point)
        
        self.node_count = len(self.route_coord_list)
        self.route_coord_list = filter_waypoints(self.route_coord_list)
        
        