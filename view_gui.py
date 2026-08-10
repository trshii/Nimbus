# pyright: strict

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from utils.utilities import RoutePlan
from utils.math_calc import DEFAULT_WAYPOINT_THRESHOLD_KM


def _rain_color(prob: float) -> str:
    if prob < 0:
        return "gray"       # fetch failed
    if prob < 30:
        return "green"
    if prob < 60:
        return "orange"
    return "red"


class ViewGUI:
    """Drop-in replacement for ViewTmnl. Same interface (show_route_summary),
    renders to the Streamlit page instead of stdout."""
    
    def __init__(self):
        # Create a dedicated placeholder in the UI for the results.
        # Everything rendered by this class will go inside this box.
        self._ui_container = st.empty()

    def clear_view(self) -> None:
        """Clears the map and summary tables from the screen."""
        self._ui_container.empty()

    def show_route_summary(self, route_plan: RoutePlan) -> None:
        # 1. Clear any existing UI in the placeholder
        self.clear_view()
        
        # 2. Render all new elements INSIDE the placeholder
        with self._ui_container.container():
            col1, col2, col3 = st.columns(3)
            col1.metric("Origin", route_plan.origin)
            col2.metric("Destination", route_plan.destination)
            col3.metric("Departure", route_plan.departure_time.strftime("%H:%M, %b %d"))

            st.subheader("Route Map")
            wps = route_plan.waypoints
            center = wps[len(wps) // 2].location
            fmap = folium.Map(location=[center.lat, center.lon], zoom_start=12)

            path = [(wp.location.lat, wp.location.lon) for wp in wps]
            folium.PolyLine(path, color="#3b82f6", weight=4, opacity=0.7).add_to(fmap)

            # Coverage-zone radius: half the min waypoint spacing, so neighboring
            # zones tile the route without heavily overlapping each other.
            zone_radius_m = (DEFAULT_WAYPOINT_THRESHOLD_KM / 2) * 1000

            for idx, wp in enumerate(wps, start=1):
                loc = wp.location
                color = _rain_color(wp.rain_probability)
                popup = f"{idx}. {loc.name}<br>Rain chance: {wp.rain_probability}%"
                tooltip = f"{idx}. {loc.name} — {wp.rain_probability}%"

                # Low-opacity area = zone this weather sample stands in for
                folium.Circle(
                    location=[loc.lat, loc.lon],
                    radius=zone_radius_m,
                    color=color,
                    weight=1,
                    opacity=0.4,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.15,
                    popup=popup,
                    tooltip=tooltip,
                ).add_to(fmap)

                # Solid dot = the actual waypoint at the circle's center
                folium.CircleMarker(
                    location=[loc.lat, loc.lon],
                    radius=5,
                    color=color,
                    weight=1,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.9,
                    popup=popup,
                    tooltip=tooltip,
                ).add_to(fmap)

            # Note: We use a dynamic key based on the route to prevent Streamlit 
            # from throwing duplicate key errors if the map rapidly re-renders.
            map_key = f"route_map_{route_plan.origin}_{route_plan.departure_time.timestamp()}"
            st_folium(fmap, width=None, height=450, key=map_key)

            st.subheader("Waypoint Summary")
            rows = [
                {
                    "#": idx,
                    "Location": wp.location.name,
                    "Rain Chance (%)": wp.rain_probability,
                }
                for idx, wp in enumerate(wps, start=1)
            ]
            df = pd.DataFrame(rows)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Rain Chance (%)": st.column_config.ProgressColumn(
                        "Rain Chance (%)", min_value=0, max_value=100, format="%d%%"
                    )
                },
            )