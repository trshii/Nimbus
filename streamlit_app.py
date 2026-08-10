import os
from datetime import datetime, date, time

import textwrap
import streamlit as st
import folium
from streamlit_folium import st_folium
from dotenv import load_dotenv

from model import MainModel
from controller import MainController
from view_gui import ViewGUI
from utils.utilities import Coordinate, TravelMode

load_dotenv()

st.set_page_config(page_title="Nimbus", page_icon="🌦️", layout="wide")

# ---- Header: title + description (left) / credentials + logos (right) ----
header_left, header_right = st.columns([3, 2])

with header_left:
    st.markdown("## 🌦️ Nimbus")
    # TODO: swap this line for your own one-line tagline
    st.caption("Plan a route and see rain probability along each waypoint.")

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

# ---- Sidebar: trip details (no API key field) ----
with st.sidebar:
    st.header("Trip Details")

    st.subheader("Origin")
    st.session_state.origin["name"] = st.text_input("Origin name", st.session_state.origin["name"])
    st.caption(f"📍 {st.session_state.origin['lat']:.4f}, {st.session_state.origin['lon']:.4f}")

    st.subheader("Destination")
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

    submitted = st.button("Plan Route", type="primary", use_container_width=True)

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
    folium.Marker(
        [st.session_state.origin["lat"], st.session_state.origin["lon"]],
        tooltip="Origin",
        icon=folium.Icon(color="green"),
    ).add_to(pick_map)
    folium.Marker(
        [st.session_state.destination["lat"], st.session_state.destination["lon"]],
        tooltip="Destination",
        icon=folium.Icon(color="red"),
    ).add_to(pick_map)

    click_result = st_folium(pick_map, width=None, height=400, key="picker_map")

    if click_result and click_result.get("last_clicked"):
        lat = click_result["last_clicked"]["lat"]
        lon = click_result["last_clicked"]["lng"]
        target = "origin" if st.session_state.picking == "Origin" else "destination"
        current = st.session_state[target]
        if (round(current["lat"], 6), round(current["lon"], 6)) != (round(lat, 6), round(lon, 6)):
            st.session_state[target]["lat"] = lat
            st.session_state[target]["lon"] = lon
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
    )
    m.destination = Coordinate(
        lon=st.session_state.destination["lon"],
        lat=st.session_state.destination["lat"],
        name=st.session_state.destination["name"],
        idx=None,
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