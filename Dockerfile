# Project Gamma
#
# File: Dockerfile
# Version: 0.1
# Date: 11/23/25
#
# Author: Ian Seymour / ian.seymour@cwu.edu
#
# Description:
# Dockerfile to build the container with. All dependencies must be listed in
# the requirements.txt. To connect to the application's front end, go to
# port 5000 in any web browser while the Flask server is running. To run, see
# commands at the bottom.

# Base Image
FROM python:3.11-slim

# Environment
ENV FLASK_APP=app.py
ENV FLASK_ENV=development
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000
ENV PYTHONUNBUFFERED=1

# working directory
WORKDIR /app

# Dependencies
COPY requirements.txt .

# Install uv
RUN pip install uv --no-cache-dir

# Install dependencies using uv
RUN uv pip install -r requirements.txt --system

# Application Code
COPY . .

# Expose the port for Flask
EXPOSE 5000

# Command to run the application using the Flask development server
CMD ["flask", "run", "--debug"]