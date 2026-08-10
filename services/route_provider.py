#pyright: strict

import requests
from utils.utilities import *
from utils.adapter import ORSProfileAdapter
from typing import List, Any, Dict

class RouteProvider:
    def __init__(self) -> None:
        pass
        
    def get_open_route(self, 
                       api_key: str, 
                       mode: TravelMode, 
                       origin: List[float], 
                       destination: List[float]
                       ) -> Dict[str, Any] | None:
        """Fetches Route data from OpenRouteService, returns data via dict

        Args:
            api_key (str): API Key
            profile (TravelMode): Enum class TravelMode
            origin (List[int]): [Longitude, Latitude]
            destination (List[int]): [Longitude, Latitude]

        Returns:
            Dict[str, Any]: _description_
        """
        
        ors_adapter = ORSProfileAdapter()
        profile: str = ors_adapter.get_travel_str(mode)
        url = f"https://api.heigit.org/openrouteservice/v2/directions/{profile}"
        
        headers = {
            "Authorization": api_key,
            "Accept": "application/json, application/geo+json"
        }
        
        payload = {
            "coordinates": [origin, destination],
            "instructions": True,
            "elevation": False
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching route: {e}")
            return None
        
    def get_route_steps(self, data: Dict[str, Any]) -> Dict[int, str]:
        route = data['routes'][0]
        
        route_waypts_steps: List[Dict[str, Any]] = route['segments'][0]['steps']
        
        route_waypts_len = route['way_points'][-1] + 1
        
        route_waypts_idx_name_map: Dict[int, str] = {}
        
        for step in route_waypts_steps:
            start_idx, end_idx = step["way_points"]
            step_name: str = step["name"].split(",")[0].strip()
            
            for i in range(start_idx, end_idx):
                route_waypts_idx_name_map[i] = step_name
                
        if route_waypts_steps:
            last_step = route_waypts_steps[-1]
            last_idx = last_step["way_points"][1]
            route_waypts_idx_name_map[last_idx] = last_step["name"]

        assert len(route_waypts_idx_name_map) == route_waypts_len
        
        return route_waypts_idx_name_map

    def get_route_summary(self, data: Dict[str, Any]) -> Dict[str, float]:
        route_summ: Dict[str, float] = data['routes'][0]['summary']
        return route_summ

        
        