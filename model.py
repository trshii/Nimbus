# pyright: strict

import polyline
from services.route_provider import RouteProvider
from services.weather_provider import WeatherProvider
from datetime import datetime
from utils.math_calc import filter_waypoints
from utils.utilities import *
from typing import *

class MainModel:
    def __init__(self, 
                 api_key: str, 
                 curr_time: datetime, 
                 travel_mode: TravelMode = TravelMode.DRIVING) -> None:
        self.origin: Coordinate = Coordinate(lon=121.0676, 
                                             lat=14.5542, 
                                             name="Buting, Pasig City",
                                             idx=None)
        self.destination: Coordinate = Coordinate(lon=121.0633, 
                                                  lat=14.6549, 
                                                  name="UP Campus, Diliman, QC",
                                                  idx=None)
        self.mode: TravelMode = travel_mode
        
        # api info
        self.api_key = api_key
        self.route_api = RouteProvider()
        self.weather_api = WeatherProvider()
        
        # route info
        self.route_coord_list: List[Coordinate] = []
        self.rain_probability: List[float] = []
        self.waypoints: List[Waypoint] = []
        self.curr_time: datetime = curr_time
        self.route_summary: Dict[str, Any] = {}
        self.route_duration: float | None = None 
        self.route_distance: float | None = None
        
        
    def set_route_info(self) -> None:
        """Sets route information into model properties

        Raises:
            ValueError: Route not fetched properly
        """
        self.raw_route_plan: Dict[str, Any] | None = self.route_api.get_open_route(
                                                    self.api_key, 
                                                    self.mode, 
                                                    self.origin.coord_list, 
                                                    self.destination.coord_list
                                                    )
        
        if self.raw_route_plan is None:
            raise ValueError("Route not fetched properly!")
        
        # sets route information
        self.route_summary = self.route_api.get_route_summary(self.raw_route_plan)
        self.route_duration = self.route_summary['duration']
        self.route_distance = self.route_summary['distance']
        
        # convert route plan geometry polyline to List[Tuple[lon, lat]]
        encoded_geometry = self.raw_route_plan['routes'][0]['geometry']
        decoded_geometry: List[coord] = polyline.decode(encoded_geometry)
        # print(f"Initial Node Count: {len(decoded_geometry)}")
        
        idx_to_name_map = self.route_api.get_route_steps(self.raw_route_plan)
        
        # convert coordinates into Coordinate dataclass
        for idx, (lat, lon) in enumerate(decoded_geometry):
            name = idx_to_name_map[idx]
            point = Coordinate(lon, lat, name=name, idx=idx)
            self.route_coord_list.append(point)
        self.node_count = len(self.route_coord_list)
        
        # filter waypoints to show points > 2km from curr node
        self.route_coord_list = filter_waypoints(self.route_coord_list)
        self.route_coord_list[0].name = self.origin.name
        self.route_coord_list[-1].name = self.destination.name
        
        # print(f"Filtered Node Count (2km Threshold): {len(self.route_coord_list)}")
        # print(f"Coordinates: {self.route_coord_list}")
        
    def set_weather_for_coords(self) -> None:
        weather_api = WeatherProvider()
        for point in self.route_coord_list:
            prob = weather_api.get_rain_probability(point, self.curr_time)
            self.rain_probability.append(prob)
            
        # print(f"Rain probability for each point: {self.rain_probability}")
            
    def set_waypoints(self) -> None:
        for idx, point in enumerate(self.route_coord_list):
            waypoint = Waypoint(point, self.rain_probability[idx])
            self.waypoints.append(waypoint)
            
    def set_route_plan(self) -> None:
        if self.origin.name is None:
            raise ValueError("Origin has invalid name!")
        if self.destination.name is None:
            raise ValueError("Destination has invalid name!")
        
        self.route_plan: RoutePlan = RoutePlan(self.origin.name, 
                                               self.destination.name, 
                                               self.curr_time, 
                                               self.waypoints)
        
