# Project Gamma
#
# File: weather_api.py
# Version: 0.2
# Date: 11/30/25
#
# Author: Ian Seymour / ian.seymour@cwu.edu
#
# Description:
# Wrapper for NOAA API requests and weather radar retrieval.

import requests
from flask import current_app
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# NOAA API endpoints
NOAA_POINTS_API = "https://api.weather.gov/points/{latitude},{longitude}"

# NOAA Radar Image Endpoints
# These fetch the GIF loop or static image for a specific station
NOAA_RADAR_STATIC = "https://radar.weather.gov/ridge/standard/{station}_0.png"
NOAA_RADAR_LOOP = "https://radar.weather.gov/ridge/standard/{station}_loop.gif"
NOAA_RADAR_DETAIL = "https://radar.weather.gov/station/{station}/detail"

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

    def get_radar_info(self, latitude: float, longitude: float) -> Optional[Dict]:
            """
            Get the nearest radar station and image URLs for a location.
            
            Args:
                latitude
                longitude
                
            Returns:
                Dictionary containing station ID and radar image URLs
            """
            try:
                # Reuse the points API to find the nearest radar station
                points = self.get_points(latitude, longitude)
                if not points or 'properties' not in points:
                    return None
                
                # Extract the station ID
                station_id = points['properties'].get('radarStation')
                
                if not station_id:
                    logger.warning(f"No radar station found for coordinates: {latitude}, {longitude}")
                    return None
                
                # Clean the ID just in case
                station_id = station_id.strip()
                
                return {
                    'station_id': station_id,
                    'static_url': NOAA_RADAR_STATIC.format(station=station_id),
                    'loop_url': NOAA_RADAR_LOOP.format(station=station_id),
                    'external_link': NOAA_RADAR_DETAIL.format(station=station_id)
                }
            except Exception as e:
                logger.error(f"Error getting radar info: {e}")
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
