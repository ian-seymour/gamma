# Project Gamma
#
# File: __init__.py
# Version: 0.1
# Date: 11/25/25
#
# Author: Ian Seymour / ian.seymour@cwu.edu
#
# Description:
# Authentication blueprint for the Project Gamma web application.

from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

from . import routes
