# pyright: strict

from model import MainModel
from view_tmnl import ViewTmnl

class MainController:
    def __init__(self, model: MainModel, view: ViewTmnl) -> None:
        self.m = model
        self.v = view
        pass
    
    def run(self) -> None:
        m = self.m
        v = self.v
        
        m.set_route_info()
        m.set_weather_for_coords()
        m.set_waypoints()
        m.set_route_plan()
        
        v.show_route_summary(m.route_plan)