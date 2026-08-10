# pyright: strict

import requests
import streamlit as st
from typing import List, Dict, Any


class GeocoderProvider:
    """Wraps the OpenRouteService (ORS) geocoding endpoints.

    - reverse_geocode: coordinates -> human-readable address label
    - search_address:  free-text query -> list of address candidates

    """

    _REVERSE_URL = "https://api.openrouteservice.org/geocode/reverse"
    _SEARCH_URL = "https://api.openrouteservice.org/geocode/search"

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def reverse_geocode(self, lat: float, lon: float) -> str:
        """Converts a coordinate pair into a readable address label.

        Args:
            lat (float): Latitude
            lon (float): Longitude

        Returns:
            str: Best-match address label, or a "lat, lon" fallback.
        """
        return GeocoderProvider._reverse_geocode_cached(self.api_key, lat, lon)

    def search_address(self, query: str) -> List[Dict[str, Any]]:
        """Searches for address candidates matching a free-text query.

        Args:
            query (str): Free-text search string (e.g. "SM North EDSA")

        Returns:
            List[Dict[str, Any]]: Up to 5 candidates, each shaped as
                {"name": str, "lat": float, "lon": float}. Empty list on
                failure or no matches.
        """
        if not query.strip():
            return []
        return GeocoderProvider._search_address_cached(self.api_key, query)


    @staticmethod
    @st.cache_data(show_spinner=False, ttl=86400)
    def _reverse_geocode_cached(api_key: str, lat: float, lon: float) -> str:
        fallback = f"{lat:.5f}, {lon:.5f}"

        params: Dict[str, Any] = {
            "api_key": api_key,
            "point.lon": lon,
            "point.lat": lat,
            "size": 1,
        }

        try:
            response = requests.get(GeocoderProvider._REVERSE_URL, params=params, timeout=5.0)
            response.raise_for_status()
            data: Dict[str, Any] = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error reverse geocoding: {e}")
            return fallback

        features: List[Dict[str, Any]] = data.get("features", [])
        if not features:
            return fallback

        properties: Dict[str, Any] = features[0].get("properties", {})
        label: str | None = properties.get("label")

        return label if label else fallback

    @staticmethod
    @st.cache_data(show_spinner=False, ttl=86400)
    def _search_address_cached(api_key: str, query: str) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {
            "api_key": api_key,
            "text": query,
            "size": 5,
        }

        try:
            response = requests.get(GeocoderProvider._SEARCH_URL, params=params, timeout=5.0)
            response.raise_for_status()
            data: Dict[str, Any] = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error searching address: {e}")
            return []

        results: List[Dict[str, Any]] = []

        for feature in data.get("features", []):
            properties: Dict[str, Any] = feature.get("properties", {})
            geometry: Dict[str, Any] = feature.get("geometry", {})
            coordinates: List[float] | None = geometry.get("coordinates")
            label: str | None = properties.get("label")

            if not coordinates or len(coordinates) < 2 or not label:
                continue

            results.append({
                "name": label,
                "lon": float(coordinates[0]),
                "lat": float(coordinates[1]),
            })

        return results