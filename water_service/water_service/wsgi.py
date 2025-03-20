"""
WSGI config for water_service project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'water_service.settings')

# This is the important part for Vercel
application = get_wsgi_application()

# Add handler for Vercel serverless function
handler = application
