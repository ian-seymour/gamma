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
from app import create_app, db

# Application factory pattern
app = create_app()

@app.cli.command("init-db")
def init_db():
    with app.app_context():
        db.create_all()
    print("Initialized the database.")

if __name__ == '__main__':
    with app.app_context():
        # Ensure the database tables exist when running directly
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)