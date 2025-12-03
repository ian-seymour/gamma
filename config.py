# Project Gamma
#
# File: config.py
# Version: 0.2
# Date: 12/2/25
#
# Author: Ian Seymour / ian.seymour@cwu.edu
#
# Description:
# Configuration settings for the Project Gamma web application.

import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # The NOAA NWS API requires a custom User-Agent header (email/app name)
    NOAA_USER_AGENT = os.environ.get('NOAA_USER_AGENT', 'gamma/ianseymourhansel@gmail.com')

    # AirNow API Key
    AIRNOW_API_KEY = os.environ.get('AIRNOW_API_KEY')
    
    # GeoIP Configuration
    GEOIP_URL = "http://ip-api.com/json/{ip}"

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    
class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False