# Project Gamma
#
# File: __init__.py
# Version: 0.1
# Date: 11/23/25
#
# Author: Ian Seymour / ian.seymour@cwu.edu
#
# Description:
# Initialization of the Project Gamma Flask application.

from flask import Flask
from config import DevelopmentConfig

# The application factory
def create_app(config_object=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Register Blueprints
    from .weather import weather_bp
    app.register_blueprint(weather_bp)

    return app