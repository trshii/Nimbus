# pyright: strict

import requests
from typing import List, Dict, Any
from datetime import datetime
from utils.utilities import Coordinate

class WeatherProvider:
    def __init__(self, timeout: float = 5.0) -> None:
        self.timeout = timeout
        self.url = "https://api.open-meteo.com/v1/forecast"
        self.data: Dict[str, Any] = {}
        
    def get_rain_probability(self, point: Coordinate, eta: datetime) -> int:
        """Queries Open-Meteo for a coordinate and snaps the ETA to the closest hour. Returns probability as int.

        Args:
            point (Coordinate): Coordinate
            eta (datetime): ETA to point

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
    
    def get_rain_probabillity_optimized(self, 
                                        points: List[Coordinate], 
                                        start_time: datetime, 
                                        end_time: datetime
                                        ) -> Dict[Coordinate, int]:
        """Generates a Dict, kv being Coordinate corresponding to Rain% at the eta of that point

        Args:
            points (List[Coordinate]): List of coords
            trip_start (datetime): Trip Start Time
            eta_end (datetime): Trip Estimated End Time

        Returns:
            Dict[Coordinate, int]: Dict of coords corresponding to rain% 
        """
        
        lats = ",".join(str(p.lat) for p in points)
        lons = ",".join(str(p.lon) for p in points)
        
        start_str = start_time.strftime("%Y-%m-%dT%H:00")
        end_str = end_time.strftime("%Y-%m-%dT%H:00")
        
        params: Dict[str, Any] = {
                "latitude": lats,
                "longitude": lons,
                "hourly": "precipitation_probability",
                "start_hour": start_str,
                "end_hour": end_str,
                "timezone": "Asia/Manila"
            }
        
        response = requests.get(self.url, params=params)
        response.raise_for_status()
        data = response.json()
        
        results: Dict[Coordinate, int] = {}
        
        # ensure data is always iterable (in case of single point returns)
        if isinstance(data, dict) and "hourly" in data:
            data: List[Dict[str, Any]] = [data]
            
        for idx, point in enumerate(points):
            loc_weather = data[idx]["hourly"]
            
            times = loc_weather["time"]
            precip_prob = loc_weather["precipitation_probability"]
            
            closest_idx = 0
            min_time_diff = float("inf")
            
            for i, time_str in enumerate(times):
                forecast_time = datetime.fromisoformat(time_str)
                
                assert isinstance(point.eta, datetime)
                diff_seconds = abs((forecast_time - point.eta).total_seconds())
                
                if diff_seconds < min_time_diff:
                    min_time_diff = diff_seconds
                    closest_idx = i
                    
            matched_precip_prob = precip_prob[closest_idx]
            
            results[point] = matched_precip_prob
            
        return results