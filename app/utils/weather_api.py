# Project Gamma
#
# File: weather_api.py
# Version: 0.1
# Date: 11/26/25
#
# Author: Ian Seymour / ian.seymour@cwu.edu
#
# Description:
# Wrapper for NOAA/NWS API interactions and weather radar retrieval.

import requests
from flask import current_app
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# NOAA API endpoints
NOAA_POINTS_API = "https://api.weather.gov/points/{latitude},{longitude}"

class WeatherAPI:
    """Wrapper class for NOAA/NWS API calls."""
    
    def __init__(self):
        """Initialize the WeatherAPI with headers for NOAA."""
        self.user_agent = current_app.config.get('NOAA_USER_AGENT', 'gamma/ianseymourhansel@gmail.com')
        self.headers = {'User-Agent': self.user_agent}
    
    def get_points(self, latitude: float, longitude: float) -> Optional[Dict]:
        """
        Get grid point data from NOAA.
        
        Args:
            latitude
            longitude
            
        Returns:
            Dictionary containing grid point data or none if request fails
        """
        try:
            url = NOAA_POINTS_API.format(latitude=latitude, longitude=longitude)
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching points data: {e}")
            return None
    
    def get_weather_data(self, latitude: float, longitude: float) -> Optional[Dict]:
        """
        Get current weather conditions for a location.
        
        Args:
            latitude
            longitude
            
        Returns:
            Dictionary containing current weather conditions
        """
        try:
            # use points API to get the forecast URL, then fetch it
            points = self.get_points(latitude, longitude)
            if not points or 'properties' not in points:
                return None

            forecast_url = points['properties'].get('forecast')
            if not forecast_url:
                return None

            resp = requests.get(forecast_url, headers=self.headers, timeout=10)
            resp.raise_for_status()
            forecast = resp.json()

            if not forecast or 'properties' not in forecast:
                return None

            periods = forecast['properties'].get('periods', [])
            if not periods:
                return None

            current = periods[0]

            return {
                'current': current,
                'latitude': latitude,
                'longitude': longitude
            }
        except Exception as e:
            logger.error(f"Error getting weather data: {e}")
            return None


def geocode_location(location: str) -> Optional[Tuple[float, float, str]]:
    """
    Geocode a location name to latitude and longitude.
    
    Args:
        location: Location name to geocode
        
    Returns:
        Tuple of (latitude, longitude, city_name) or none if error
    """
    try:
        # Using OpenStreetMap's Nominatim service
        headers = {'User-Agent': 'gamma-weather-app'}
        params = {
            'q': location,
            'format': 'json',
            'limit': 1,
            'addresstype': 'city'
        }
        
        response = requests.get(
            'https://nominatim.openstreetmap.org/search',
            params=params,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        
        results = response.json()
        if not results:
            return None
        
        result = results[0]
        latitude = float(result['lat'])
        longitude = float(result['lon'])
        # Extract city name or use the display name
        city_name = result.get('name', result.get('display_name', location))
        
        return (latitude, longitude, city_name)
    except Exception as e:
        logger.error(f"Error geocoding location '{location}': {e}")
        return None
