"""
URL configuration for water_service project.
"""
from django.contrib import admin
from django.urls import path, include
from accounts.views import home

# Combine all URL patterns into a single list
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),  # Include accounts app URLs
    path('', include('accounts.urls')),  # Include accounts URLs for root path
    path("__reload__/", include("django_browser_reload.urls")),  # For browser reload
]
