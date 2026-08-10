# pyright: strict

import streamlit as st
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
        self._ui_container = st.empty()

    def clear_view(self) -> None:
        """Clears the map and summary tables from the screen."""
        self._ui_container.empty()

    def show_route_summary(self, route_plan: RoutePlan) -> None:
        # 1. Clear any existing UI in the placeholder
        self.clear_view()
        
        # 2. Render all new elements INSIDE the placeholder
        with self._ui_container.container():
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Origin", route_plan.origin)
            col2.metric("Destination", route_plan.destination)
            col3.metric("Departure", route_plan.departure_time.strftime("%H:%M, %b %d"))
            
            wps = route_plan.waypoints
            arrival_time = wps[-1].location.eta
            col4.metric("Arrival", arrival_time.strftime("%H:%M, %b %d"))

            st.subheader("Route Map")
            center = wps[len(wps) // 2].location
            fmap = folium.Map(location=[center.lat, center.lon], zoom_start=12)

            optimized_geometry = route_plan.full_geometry[::3]
            folium.PolyLine(optimized_geometry, color="#3b82f6", weight=4, opacity=0.7).add_to(fmap)

            zone_radius_m = (DEFAULT_WAYPOINT_THRESHOLD_KM / 2) * 1000

            for idx, wp in enumerate(wps, start=1):
                loc = wp.location
                color = _rain_color(wp.rain_probability)
                formatted_eta = loc.eta.strftime("%I:%M %p")
                
                popup = f"{idx}. {loc.name}<br>ETA: {formatted_eta}<br>Rain chance: {wp.rain_probability}%"
                tooltip = f"{idx}. {loc.name} — {formatted_eta} — {wp.rain_probability}%"

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

            map_key = f"route_map_{route_plan.origin}_{route_plan.departure_time.timestamp()}"
            st_folium(fmap, width=None, height=450, key=map_key)

            st.subheader("Waypoint Summary")
            
            table_rows = ""
            for idx, wp in enumerate(wps, start=1):
                pop = wp.rain_probability
                color = _rain_color(pop)
                eta = wp.location.eta.strftime("%I:%M %p")
                
                # Removed hardcoded 'color: white' to let it inherit var(--text-color)
                # Used var(--secondary-background-color) for the empty progress bar track
                # Used rgba(128,128,128,0.2) for a theme-agnostic subtle border
                table_rows += f"""
                <tr style="border-bottom: 1px solid rgba(128, 128, 128, 0.2);">
                    <td style="padding: 12px 8px; font-weight: bold;">{idx}</td>
                    <td style="padding: 12px 8px;">{wp.location.name}</td>
                    <td style="padding: 12px 8px;">{eta}</td>
                    <td style="padding: 12px 8px;">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <span style="min-width: 36px; color: {color}; font-weight: bold; text-align: right;">{pop}%</span>
                            <div style="background-color: var(--secondary-background-color); border-radius: 6px; width: 100%; height: 10px; overflow: hidden;">
                                <div style="background-color: {color}; width: {pop}%; height: 100%; border-radius: 6px;"></div>
                            </div>
                        </div>
                    </td>
                </tr>
                """

            # Bound the entire table to var(--text-color)
            raw_html = f"""
            <table style="width: 100%; text-align: left; border-collapse: collapse; margin-top: 8px; color: var(--text-color);">
                <thead>
                    <tr style="border-bottom: 2px solid rgba(128, 128, 128, 0.3); font-size: 0.9rem;">
                        <th style="padding: 10px 8px;">#</th>
                        <th style="padding: 10px 8px;">Location</th>
                        <th style="padding: 10px 8px;">ETA</th>
                        <th style="padding: 10px 8px; width: 35%;">Rain Chance</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
            """
            
            # Remove all leading spaces from every line to prevent Markdown code-block triggering
            clean_html = "\n".join(line.strip() for line in raw_html.splitlines() if line.strip())
            
            st.markdown(clean_html, unsafe_allow_html=True)