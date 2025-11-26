# Project Gamma
#
# File: run.py
# Version: 0.1
# Date: 11/23/25
#
# Author: Ian Seymour / ian.seymour@cwu.edu
#
# Description:
# This script serves as the entry point for the Project Gamma web application.
# It initializes the Flask application and sets up the database.

import os
from app import create_app

# Application factory pattern
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)