# pyright: strict

from utils.utilities import *

class ViewTmnl:
    def show_route_summary(self, route_plan: RoutePlan) -> None:
        print(" -- Route Summary --")
        print()
        print(f"Origin: {route_plan.origin}")
        print(f"Destination: {route_plan.destination}")
        print(f"Trip Start Time: {route_plan.departure_time}")
        print()
        print("Waypoint Summary:")
        for idx, waypoint in enumerate(route_plan.waypoints):
            print(f"{idx + 1}. ")
            print(f"{waypoint.location.name}")
            print(f"Rain Chance: {waypoint.rain_probability}")
            print(f"ETA: {waypoint.eta}")
            print()