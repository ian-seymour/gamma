# Project Gamma
#
# File: routes.py
# Version: 0.3
# Date: 12/2/25
#
# Author: Ian Seymour / ian.seymour@cwu.edu
#
# Description:
# Routes for weather-related views in the Project Gamma web application.

from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from . import weather_bp
from ..models import Favorite
from ..utils.weather_api import WeatherAPI, geocode_location
from .. import db


@weather_bp.route('/')
@login_required
def dashboard():
    """Main weather dashboard."""
    favorites = Favorite.query.filter_by(user_id=current_user.id).all()
    weather_data = None
    current_location = None
    radar_data = None
    aqi_data = None
    lat = None
    lon = None
    
    # Check if a favorite is specified in query string
    favorite_id = request.args.get('favorite_id', type=int)
    if favorite_id:
        favorite = Favorite.query.get(favorite_id)
        if favorite and favorite.user_id == current_user.id:
            current_location = favorite
            lat = favorite.latitude
            lon = favorite.longitude
            
    # If no location selected yet, default to Ellensburg
    if not current_location:
        lat = 46.9965
        lon = -120.5478
        current_location = {
            'city': 'Ellensburg',
            'latitude': lat,
            'longitude': lon,
            'id': None # None means it's not a database object
        }

    # Fetch data using the determined coordinates
    if lat and lon:
        weather_api = WeatherAPI()
        weather_data = weather_api.get_weather_data(lat, lon)
        radar_data = weather_api.get_radar_info(lat, lon)
        aqi_data = weather_api.get_air_quality(lat, lon)
    
    return render_template('weather/dashboard.html', 
                          favorites=favorites,
                          weather_data=weather_data,
                          current_location=current_location,
                          radar_data=radar_data,
                          aqi_data=aqi_data)


@weather_bp.route('/search', methods=['POST'])
@login_required
def search_location():
    """Search for a location and get weather data."""
    location = request.form.get('search')
    
    if not location:
        flash('Please enter a location', 'warning')
        return redirect(url_for('weather.dashboard'))
    
    # Geocode the location
    geocoded = geocode_location(location)
    if not geocoded:
        flash('Location not found. Please try another search.', 'danger')
        return redirect(url_for('weather.dashboard'))
    
    latitude, longitude, city_name = geocoded
    
    # Get weather data
    weather_api = WeatherAPI()
    weather_data = weather_api.get_weather_data(latitude, longitude)

    if not weather_data or not weather_data.get('current'):
        flash('Unable to fetch weather data. Please try again.', 'danger')
        return redirect(url_for('weather.dashboard'))
    
    radar_data = weather_api.get_radar_info(latitude, longitude)
    
    favorites = Favorite.query.filter_by(user_id=current_user.id).all()
    
    # Create a temporary location object for display
    current_location = {
        'city': city_name,
        'latitude': latitude,
        'longitude': longitude,
        'id': None
    }
    
    return render_template('weather/dashboard.html',
                         favorites=favorites,
                         weather_data=weather_data,
                         current_location=current_location,
                         radar_data=radar_data)


@weather_bp.route('/api/weather/<float:latitude>/<float:longitude>')
@login_required
def api_weather(latitude, longitude):
    """API endpoint to fetch weather data."""
    weather_api = WeatherAPI()
    weather_data = weather_api.get_weather_data(latitude, longitude)
    
    if not weather_data:
        return jsonify({'error': 'Unable to fetch weather data'}), 400
    
    # Simplify the response for JSON
    return jsonify(weather_data)


@weather_bp.route('/favorites/add', methods=['POST'])
@login_required
def add_favorite():
    """Add a location to favorites."""
    # Check if user already has 10 favorites
    favorite_count = Favorite.query.filter_by(user_id=current_user.id).count()
    if favorite_count >= 10:
        flash('You can only have 10 favorite locations.', 'warning')
        return redirect(url_for('weather.dashboard'))
    
    city = request.form.get('city')
    latitude = request.form.get('latitude', type=float)
    longitude = request.form.get('longitude', type=float)
    
    if not city or latitude is None or longitude is None:
        flash('Invalid location data', 'danger')
        return redirect(url_for('weather.dashboard'))
    
    # Check if favorite already exists
    existing = Favorite.query.filter_by(user_id=current_user.id, city=city).first()
    if existing:
        flash(f'{city} is already in your favorites.', 'info')
        return redirect(url_for('weather.dashboard'))
    
    favorite = Favorite(user_id=current_user.id, city=city, 
                       latitude=latitude, longitude=longitude)
    db.session.add(favorite)
    db.session.commit()
    
    flash(f'{city} added to favorites!', 'success')
    return redirect(url_for('weather.dashboard', favorite_id=favorite.id))


@weather_bp.route('/favorites/<int:favorite_id>/remove', methods=['POST'])
@login_required
def remove_favorite(favorite_id):
    """Remove a location from favorites."""
    favorite = Favorite.query.get(favorite_id)
    
    if not favorite or favorite.user_id != current_user.id:
        flash('Favorite not found.', 'danger')
        return redirect(url_for('weather.dashboard'))
    
    city_name = favorite.city
    db.session.delete(favorite)
    db.session.commit()
    
    flash(f'{city_name} removed from favorites.', 'success')
    return redirect(url_for('weather.dashboard'))


@weather_bp.route('/radar/<float:latitude>/<float:longitude>')
@login_required
def get_radar(latitude, longitude):
    """Get weather radar info for a specific location."""
    weather_api = WeatherAPI()
    radar_info = weather_api.get_radar_info(latitude, longitude)
    if not radar_info:
        return jsonify({'error': 'Radar not found'}), 404
    return jsonify(radar_info)
