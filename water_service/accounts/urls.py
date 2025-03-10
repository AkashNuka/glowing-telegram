"""
URL patterns for the accounts app.
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='logout_confirmation'), name='logout'),
    path('logout-confirmation/', views.logout_confirmation, name='logout_confirmation'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('guest-order/', views.guest_order, name='guest_order'),
    path('check-auth/', views.check_auth, name='check_auth'),
    # Owner specific pages
    path('owner/analytics/', views.owner_analytics, name='owner_analytics'),
    path('owner/drivers/', views.owner_drivers, name='owner_drivers'),  # New URL route
]