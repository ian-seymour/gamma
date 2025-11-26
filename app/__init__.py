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
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import DevelopmentConfig

# Create extensions
db = SQLAlchemy()
login_manager = LoginManager()

# The application factory
def create_app(config_object=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_object)
    
    # Set database URI
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'

    with app.app_context():
        # Import models to register them with SQLAlchemy
        from .models import User, Favorite
        
        # Create all tables
        db.create_all()

    # Register Blueprints
    from .weather import weather_bp
    from .auth import auth_bp
    app.register_blueprint(weather_bp)
    app.register_blueprint(auth_bp)

    return app