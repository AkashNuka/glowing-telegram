#!/bin/bash
# Build script for Vercel deployment

echo "Building project..."

# Install Python dependencies
pip install -r requirements.txt

# Make migrations
python water_service/manage.py makemigrations
python water_service/manage.py migrate

# Collect static files
python water_service/manage.py collectstatic --noinput

echo "Build completed."
