#pyright: strict

from utils.utilities import TravelMode

class ORSProfileAdapter:
    def __init__(self) -> None:
        self._mode_map = {
            TravelMode.DRIVING: "driving-car",
            TravelMode.CYCLING: "cycling-regular",
            TravelMode.WALKING: "foot-walking"
        }
        
    def get_travel_str(self, mode: TravelMode) -> str:
        if mode not in self._mode_map:
            raise ValueError(f"No OpenRouteService profile mapped for: {mode.name}")
        return self._mode_map[mode]