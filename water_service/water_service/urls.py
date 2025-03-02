"""
URL configuration for water_service project.
"""
from django.contrib import admin
from django.urls import path, include
from accounts.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),  # Include accounts app URLs
    path('', include('accounts.urls')),  # Include accounts URLs for root path
]
