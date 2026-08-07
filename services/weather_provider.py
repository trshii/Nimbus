# pyright: strict

import requests
from typing import List
from datetime import datetime
from utils.utilities import Coordinate

class WeatherProvider:
    def __init__(self, timeout: float = 5.0) -> None:
        self.timeout = timeout
        self.url = "https://api.open-meteo.com/v1/forecast"
        
    def get_rain_probability(self, point: Coordinate, eta: datetime) -> int:
        """Queries Open-Meteo for a coordinate and snaps the ETA to the closest hour. Returns probability as int.

        Args:
            point (Coordinate): Coordinate
            eta (datetime): Current Time

        Returns:
            int: Returns probability as int n (n%)
        """
        lon, lat = point.lon, point.lat
        
        params = {
            "longitude": lon,
            "latitude": lat,
            "hourly": "precipitation_probability",
            "timezone": "Asia/Manila",
            "forecast_days": 2,
            "timeformat": "unixtime"
        }
        
        try:
            response = requests.get(url=self.url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error getting weather data: {e}")
            return -1
        
        hourly_times:List[int] = data["hourly"]["time"]
        hourly_probs:List[int] = data["hourly"]["precipitation_probability"]
        
        eta_unix = int(eta.timestamp())
        
        closest_hour_idx = min(
            range(len(hourly_times)),
            key=lambda i: abs(hourly_times[i] - eta_unix)
        )
        
        return hourly_probs[closest_hour_idx]