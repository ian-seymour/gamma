# Project Gamma
#
# File: config.py
# Version: 0.1
# Date: 11/23/25
#
# Author: Ian Seymour / ian.seymour@cwu.edu
#
# Description:
# Configuration settings for the Project Gamma web application.

import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key')
    
    # The NOAA NWS API requires a custom User-Agent header (email/app name)
    NOAA_USER_AGENT = os.environ.get('NOAA_USER_AGENT')
    
    # GeoIP Configuration
    GEOIP_URL = "http://ip-api.com/json/{ip}"

class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False