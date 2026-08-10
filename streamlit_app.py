import os
from datetime import datetime, date, time
from typing import Dict, Any, List

import textwrap
import streamlit as st
import folium
from streamlit_folium import st_folium
from dotenv import load_dotenv

from model import MainModel
from controller import MainController
from view_gui import ViewGUI
from services.geocoder_provider import GeocoderProvider
from utils.utilities import Coordinate, TravelMode

load_dotenv()

st.set_page_config(page_title="Nimbus", page_icon="🌦️", layout="wide")

# In streamlit_app.py, near the top of the file

@st.dialog("Welcome to Nimbus! ⛅")
def tutorial_modal():
    st.write("Plan your ride routes and avoid the rain. Here is how it works:")
    
    st.markdown("""
    * **Set Locations:** Use the sidebar to search for your start and end points (Address needs to be specific according to OpenStreetMap). You can also click directly on the map to drop a pin.
    * **Set the Time:** Choose your exact departure time (Note that traffic is not taken into account yet).
    * **Ride Ready:** Click **Plan Route**. Nimbus will calculate your ETA and check the weather at every waypoint, so you know exactly what to expect before you go out.
    """)
    
    # A button to close the modal
    if st.button("Let's Ride!", type="primary", width="stretch"):
        st.session_state.tutorial_viewed = True
        st.rerun()
        
if "tutorial_viewed" not in st.session_state:
    st.session_state.tutorial_viewed = False

if not st.session_state.tutorial_viewed:
    tutorial_modal()
    
if "last_processed_click" not in st.session_state:
    st.session_state.last_processed_click = None

# ---- Header: title + description (left) / credentials + logos (right) ----
header_left, header_right = st.columns([3, 2])



with header_left:
    st.markdown("## 🌦️ Nimbus")
    # TODO: swap this line for your own one-line tagline
    st.caption("Plan a route and see rain probability along each waypoint (Does not support live traffic data).")

with header_right:
    st.markdown(
        textwrap.dedent(
            """
            <div style="display:flex; flex-direction:column; align-items:flex-end;
                        justify-content:center; height:100%; padding-top:8px;">
                <div style="font-size:0.7rem; color:#888; margin-bottom:6px;">Contact Me</div>
                <div style="display:flex; gap:12px;">
                    <!-- GitHub -->
                    <a href="https://github.com/trshii" target="_blank" rel="noopener noreferrer"
                       style="width:28px; height:28px; border-radius:50%; background:#e2e8f0;
                              display:flex; align-items:center; justify-content:center; text-decoration:none;">
                        <img src="https://api.iconify.design/mdi:github.svg?color=%2364748b" width="18" height="18" alt="GitHub"/>
                    </a>
                    <!-- Facebook -->
                    <a href="https://facebook.com/treixee.cruz" target="_blank" rel="noopener noreferrer"
                       style="width:28px; height:28px; border-radius:50%; background:#e2e8f0;
                              display:flex; align-items:center; justify-content:center; text-decoration:none;">
                        <img src="https://api.iconify.design/mdi:facebook.svg?color=%2364748b" width="18" height="18" alt="Facebook"/>
                    </a>
                    <!-- Gmail -->
                    <a href="mailto:treixee@gmail.com" target="_blank" rel="noopener noreferrer"
                       style="width:28px; height:28px; border-radius:50%; background:#e2e8f0;
                              display:flex; align-items:center; justify-content:center; text-decoration:none;">
                        <img src="https://api.iconify.design/mdi:gmail.svg?color=%2364748b" width="18" height="18" alt="Gmail"/>
                    </a>
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

# ---- API key: your key, not the visitor's. No field shown in the UI. ----
try:
    API_KEY = st.secrets.get("ORS_API_KEY", os.getenv("ORS_API_KEY", ""))
except Exception:
    API_KEY = os.getenv("ORS_API_KEY", "")

if not API_KEY:
    st.error("Server is missing ORS_API_KEY. Set it in .env (local) or Secrets (Streamlit Cloud).")
    st.stop()

# ORS also backs the Pelias geocoding endpoints, so we reuse the same key.
geocoder = GeocoderProvider(API_KEY)

# ---- Session state ----
if "origin" not in st.session_state:
    st.session_state.origin = {"lat": 14.5542, "lon": 121.0676, "name": "Buting, Pasig City"}
if "destination" not in st.session_state:
    st.session_state.destination = {"lat": 14.6549, "lon": 121.0633, "name": "UP Campus, Diliman, QC"}
if "picking" not in st.session_state:
    st.session_state.picking = "Origin"
if "route_plan" not in st.session_state:
    st.session_state.route_plan = None
if "error" not in st.session_state:
    st.session_state.error = None


def _render_address_search(section_label: str, state_key: str, geocoder: GeocoderProvider) -> None:
    """Renders a free-text address search box + match picker for a
    session_state target ("origin" or "destination"). Confirming a match
    overwrites that target's name/lat/lon in session_state.

    Args:
        section_label (str): Display label, e.g. "Origin"
        state_key (str): Key into st.session_state ("origin" or "destination")
        geocoder (GeocoderProvider): Shared geocoder instance
    """
    query_key = f"{state_key}_search_query"
    select_key = f"{state_key}_search_select"
    button_key = f"{state_key}_search_apply"

    query: str = st.text_input(
        f"Search {section_label.lower()} address",
        key=query_key,
        placeholder="e.g. University of the Philippines Diliman",
    )

    if not query.strip():
        return

    with st.spinner("Searching..."):
        candidates: List[Dict[str, Any]] = geocoder.search_address(query)

    if not candidates:
        st.caption("No matches found.")
        return

    labels = [c["name"] for c in candidates]
    chosen_label = st.selectbox(f"Matches for {section_label.lower()}", labels, key=select_key)
    match = next((c for c in candidates if c["name"] == chosen_label), None)

    if match is not None and st.button(f"Use this {section_label.lower()}", key=button_key):
        st.session_state[state_key]["name"] = match["name"]
        st.session_state[state_key]["lat"] = match["lat"]
        st.session_state[state_key]["lon"] = match["lon"]
        st.session_state[f"{state_key}_name_field"] = match["name"]
        
        st.rerun()


# ---- Sidebar: trip details (no API key field) ----
with st.sidebar:
    st.markdown(
        """
        <div style="display: flex; justify-content: flex-start; align-items: center; margin-bottom: 1rem;">
            <h2 style="margin: 0; padding: 0;">🌦️ Nimbus</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.header("Trip Details")

    st.subheader("Origin")
    _render_address_search("Origin", "origin", geocoder)
    st.session_state.origin["name"] = st.text_input(
        "Origin name", st.session_state.origin["name"]
    )
    st.caption(f"📍 {st.session_state.origin['lat']:.4f}, {st.session_state.origin['lon']:.4f}")

    st.subheader("Destination")
    _render_address_search("Destination", "destination", geocoder)
    st.session_state.destination["name"] = st.text_input(
        "Destination name", st.session_state.destination["name"]
    )
    st.caption(f"📍 {st.session_state.destination['lat']:.4f}, {st.session_state.destination['lon']:.4f}")

    mode_label = st.selectbox("Travel mode", ["Driving", "Cycling", "Walking"])
    mode_map = {
        "Driving": TravelMode.DRIVING,
        "Cycling": TravelMode.CYCLING,
        "Walking": TravelMode.WALKING,
    }

    trip_date = st.date_input("Departure date", value=date.today())
    trip_time = st.time_input("Departure time", value=time(hour=8, minute=0))

    submitted = st.button("Plan Route", type="primary", width="stretch")

# ---- Point picker: click the map instead of typing lat/lon ----
# ---- Point picker: click the map instead of typing lat/lon ----
with st.expander("📍 Pick points on the map", expanded=(st.session_state.route_plan is None)):
    st.session_state.picking = st.radio(
        "Clicking the map sets:",
        ["Origin", "Destination"],
        index=0 if st.session_state.picking == "Origin" else 1,
        horizontal=True,
    )

    pick_map = folium.Map(
        location=[st.session_state.origin["lat"], st.session_state.origin["lon"]],
        zoom_start=11,
    )

    # Origin Pin
    folium.Marker(
        [st.session_state.origin["lat"], st.session_state.origin["lon"]],
        tooltip=st.session_state.origin["name"],
        icon=folium.Icon(color="green"),
    ).add_to(pick_map)
    
    # Destination Pin
    folium.Marker(
        [st.session_state.destination["lat"], st.session_state.destination["lon"]],
        tooltip=st.session_state.destination["name"],
        icon=folium.Icon(color="red"),
    ).add_to(pick_map)

    click_result = st_folium(
        pick_map, 
        width=None, 
        height=400, 
        key="picker_map", 
        returned_objects=["last_clicked"] 
    )

    if click_result and click_result.get("last_clicked"):
        lat = float(click_result["last_clicked"]["lat"])
        lon = float(click_result["last_clicked"]["lng"])
        target = "origin" if st.session_state.picking == "Origin" else "destination"
        
        # Create a unique key for this click event to prevent rapid duplicate triggers
        click_id = (target, round(lat, 5), round(lon, 5))

        if click_id != st.session_state.last_processed_click:
            # 1. Lock this click signature immediately
            st.session_state.last_processed_click = click_id

            # 2. Add an animated pulsing loading marker directly onto the map UI
            pulse_icon = folium.DivIcon(
                html="""
                <div style="
                    width: 22px;
                    height: 22px;
                    background-color: #f97316;
                    border-radius: 50%;
                    border: 3px solid white;
                    box-shadow: 0 0 10px rgba(0,0,0,0.5);
                    animation: pulse-ring 1s infinite ease-in-out;
                "></div>
                <style>
                @keyframes pulse-ring {
                    0% { transform: scale(0.7); opacity: 0.6; }
                    50% { transform: scale(1.3); opacity: 1; }
                    100% { transform: scale(0.7); opacity: 0.6; }
                }
                </style>
                """
            )
            folium.Marker(
                [lat, lon],
                tooltip="⏳ Resolving address...",
                icon=pulse_icon
            ).add_to(pick_map)

            # 3. Fetch address first, then write ALL attributes atomically
            with st.spinner("Resolving location address..."):
                fetched_name = geocoder.reverse_geocode(lat, lon)
                
                # Atomic session state write
                st.session_state[target]["lat"] = lat
                st.session_state[target]["lon"] = lon
                st.session_state[target]["name"] = fetched_name

            st.rerun()

# ---- Run + render result ----
if submitted:
    curr_time = datetime.combine(trip_date, trip_time)

    m = MainModel(API_KEY, curr_time, mode_map[mode_label])
    m.origin = Coordinate(
        lon=st.session_state.origin["lon"],
        lat=st.session_state.origin["lat"],
        name=st.session_state.origin["name"],
        idx=None,
        eta=curr_time
    )
    m.destination = Coordinate(
        lon=st.session_state.destination["lon"],
        lat=st.session_state.destination["lat"],
        name=st.session_state.destination["name"],
        idx=None,
        eta=None
    )

    c = MainController(m, ViewGUI())

    with st.spinner("Fetching route and weather..."):
        try:
            c.run()
            st.session_state.route_plan = m.route_plan
            st.session_state.error = None
        except ValueError as e:
            st.session_state.route_plan = None
            st.session_state.error = f"Could not plan route: {e}"
        except Exception as e:  # noqa: BLE001 - surface any provider/network error to the user
            st.session_state.route_plan = None
            st.session_state.error = f"Unexpected error: {e}"

if st.session_state.error:
    st.error(st.session_state.error)
elif st.session_state.route_plan is not None:
    ViewGUI().show_route_summary(st.session_state.route_plan)
else:
    st.info("Pick origin/destination on the map (or keep the defaults), then click **Plan Route** in the sidebar.")