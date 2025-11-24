# Project Gamma
#
# File: __init__.py
# Version: 0.1
# Date: 11/23/25
#
# Author: Ian Seymour / ian.seymour@cwu.edu
#
# Description:
# Initialization for the weather module.

from flask import Blueprint

# Define a Blueprint for the weather-related views
weather_bp = Blueprint('weather', __name__, template_folder='templates', url_prefix='/')

from . import routes