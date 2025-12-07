# Project Gamma
#
# File: weather_api.py
# Version: 0.4
# Date: 12/3/2025
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

# AirNow API Endpoint
AIRNOW_API_ENDPOINT = "https://www.airnowapi.org/aq/observation/latLong/current/?format=application/json&latitude={latitude}&longitude={longitude}&distance=50&API_KEY={api_key}"

class WeatherAPI:
    """Wrapper class for NOAA/NWS API calls."""
    
    def __init__(self):
        """Initialize the WeatherAPI with headers for NOAA."""
        self.user_agent = current_app.config.get('NOAA_USER_AGENT', 'gamma/ianseymourhansel@gmail.com')
        self.headers = {'User-Agent': self.user_agent}
    
    def get_points(self, latitude: float, longitude: float) -> Optional[Dict]:
        """
        get grid point data from NOAA.
        
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
        get current weather conditions.
        
        Args:
            latitude
            longitude
        
        Returns:
            Dictionary containing current weather data or none if request fails
        """
        try:
            points = self.get_points(latitude, longitude)
            if not points or 'properties' not in points:
                return None

            # NOAA returns elevation in meters
            elevation_m = points['properties'].get('elevation', {}).get('value')
            elevation_ft = None
            if elevation_m is not None:
                elevation_ft = round(elevation_m * 3.28084) # Convert to feet

            forecast_hourly_url = points['properties'].get('forecastHourly')
            forecast_standard_url = points['properties'].get('forecast')

            if not forecast_hourly_url or not forecast_standard_url:
                return None

            # Fetch Hourly Data
            resp_hourly = requests.get(forecast_hourly_url, headers=self.headers, timeout=10)
            resp_hourly.raise_for_status()
            hourly_data = resp_hourly.json()
            
            if not hourly_data.get('properties', {}).get('periods'):
                return None
            
            # Base current object
            current_conditions = hourly_data['properties']['periods'][0]

            # Fetch standard forecast
            resp_standard = requests.get(forecast_standard_url, headers=self.headers, timeout=10)
            resp_standard.raise_for_status()
            standard_data = resp_standard.json()
            
            high_temp = None
            low_temp = None
            
            if standard_data.get('properties', {}).get('periods'):
                periods = standard_data['properties']['periods']
                todays_forecast = periods[0]
                
                # Add the narrative text
                current_conditions['detailedForecast'] = todays_forecast.get('detailedForecast', 'Forecast unavailable.')
                
                # Determine high and low temps based on day or night
                if todays_forecast.get('isDaytime'):
                    # If day: period 0 is today (High), period 1 is tonight (Low)
                    high_temp = todays_forecast.get('temperature')
                    if len(periods) > 1:
                        low_temp = periods[1].get('temperature')
                else:
                    # If night: period 0 is Tonight (Low), period 1 is tomorrow (High)
                    low_temp = todays_forecast.get('temperature')
                    if len(periods) > 1:
                        high_temp = periods[1].get('temperature')
            else:
                current_conditions['detailedForecast'] = "Detailed forecast unavailable."

            # get dewpoint and precip probability if available
            dewpoint = current_conditions.get('dewpoint', {}).get('value')
            precip_prob = current_conditions.get('probabilityOfPrecipitation', {}).get('value')
            
            # Convert Dewpoint to F
            dewpoint_f = None
            if dewpoint is not None:
                dewpoint_f = round((dewpoint * 9/5) + 32)

            return {
                'current': current_conditions,
                'latitude': latitude,
                'longitude': longitude,
                'elevation': elevation_ft,
                'high_temp': high_temp,
                'low_temp': low_temp,
                'dewpoint': dewpoint_f,
                'precip_prob': precip_prob
            }
        except Exception as e:
            logger.error(f"Error getting weather data: {e}")
            return None

    def get_radar_info(self, latitude: float, longitude: float) -> Optional[Dict]:
        """
        get the nearest radar station and image URLs for a location.
            
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
            }
        except Exception as e:
            logger.error(f"Error getting radar info: {e}")
            return None
            
    def get_air_quality(self, latitude: float, longitude: float) -> Optional[Dict]:
        """
        get current air quality data from AirNow.

        Args:
            latitude
            longitude

        Returns:
            The pollutant with the highest AQI.
        """
        api_key = current_app.config.get('AIRNOW_API_KEY')
        if not api_key:
            logger.warning("AirNow API key not found in config.")
            return None
        
        try:
            url = AIRNOW_API_ENDPOINT.format(
                latitude=latitude, 
                longitude=longitude, 
                api_key=api_key
            )
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # AirNow returns a list of pollutants, this will display the worst one
            if not data:
                return None
                
            # Find the primary pollutant with highest AQI
            primary = max(data, key=lambda x: x['AQI'])
            return primary
            
        except Exception as e:
            logger.error(f"Error getting air quality data: {e}")
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