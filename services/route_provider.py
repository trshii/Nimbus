#pyright: strict

import requests
from utils.utilities import *
from utils.adapter import ORSProfileAdapter
from typing import List, Any, Dict

class RouteProvider:
    def __init__(self) -> None:
        pass
        
    def get_open_route(self, api_key: str, mode: TravelMode, origin: List[float], destination: List[float]) -> Dict[str, Any] | None:
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
            "instructions": False,
            "elevation": False
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching route: {e}")
            return None
        
        