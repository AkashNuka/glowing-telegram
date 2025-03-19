"""
Custom user model with role-based authentication.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
import json

class CustomUser(AbstractUser):
    """
    Extended User model with role field to differentiate between owner, driver, and client.
    """
    # Role choices
    OWNER = 'owner'
    DRIVER = 'driver'
    CLIENT = 'client'
    
    ROLE_CHOICES = [
        (OWNER, 'Owner'),
        (DRIVER, 'Driver'),
        (CLIENT, 'Client'),
    ]
    
    # Additional fields
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=CLIENT,
        help_text='The role determines the user\'s access level'
    )
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_owner(self):
        return self.role == self.OWNER
    
    def is_driver(self):
        return self.role == self.DRIVER
    
    def is_client(self):
        return self.role == self.CLIENT

class AnalyticsData(models.Model):
    """
    Model for storing business analytics data
    """
    date_generated = models.DateTimeField(auto_now_add=True)
    total_orders = models.IntegerField(default=0)
    revenue = models.IntegerField(default=0)
    water_delivered = models.IntegerField(default=0)
    avg_order_value = models.IntegerField(default=0)
    
    # JSON fields for complex data
    monthly_growth = models.TextField(default='{}')
    top_clients = models.TextField(default='[]')
    top_drivers = models.TextField(default='[]')
    monthly_data = models.TextField(default='{}')
    water_by_package = models.TextField(default='{}')
    order_status = models.TextField(default='{}')
    peak_delivery_times = models.TextField(default='{}')
    client_growth = models.TextField(default='{}')
    
    def set_monthly_growth(self, data):
        self.monthly_growth = json.dumps(data)
        
    def get_monthly_growth(self):
        return json.loads(self.monthly_growth)
        
    def set_top_clients(self, data):
        self.top_clients = json.dumps(data)
        
    def get_top_clients(self):
        return json.loads(self.top_clients)
        
    def set_top_drivers(self, data):
        self.top_drivers = json.dumps(data)
        
    def get_top_drivers(self):
        return json.loads(self.top_drivers)
        
    def set_monthly_data(self, data):
        self.monthly_data = json.dumps(data)
        
    def get_monthly_data(self):
        return json.loads(self.monthly_data)
        
    def set_water_by_package(self, data):
        self.water_by_package = json.dumps(data)
        
    def get_water_by_package(self):
        return json.loads(self.water_by_package)
        
    def set_order_status(self, data):
        self.order_status = json.dumps(data)
        
    def get_order_status(self):
        return json.loads(self.order_status)
        
    def set_peak_delivery_times(self, data):
        self.peak_delivery_times = json.dumps(data)
        
    def get_peak_delivery_times(self):
        return json.loads(self.peak_delivery_times)
        
    def set_client_growth(self, data):
        self.client_growth = json.dumps(data)
        
    def get_client_growth(self):
        return json.loads(self.client_growth)

class Order(models.Model):
    """
    Model for storing water orders
    """
    ORDER_STATUS_CHOICES = [
        ('new', 'New'),
        ('processing', 'Processing'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    PACKAGE_CHOICES = [
        ('Standard', 'Standard (500L)'),
        ('Premium', 'Premium (1000L)'),
        ('Enterprise', 'Enterprise (1500L)'),
    ]
    
    DELIVERY_TIME_CHOICES = [
        ('morning', 'Morning (9AM - 12PM)'),
        ('afternoon', 'Afternoon (12PM - 3PM)'),
        ('evening', 'Evening (3PM - 6PM)'),
    ]
    
    # Allow null for client to support guest orders
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    driver = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries')
    
    # Guest information fields
    guest_name = models.CharField(max_length=100, null=True, blank=True)
    guest_email = models.EmailField(null=True, blank=True)
    guest_phone = models.CharField(max_length=20, null=True, blank=True)
    
    package_type = models.CharField(max_length=20, choices=PACKAGE_CHOICES)
    liters = models.IntegerField()
    quantity = models.IntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='new')
    delivery_address = models.TextField()
    delivery_date = models.DateField()
    delivery_time = models.CharField(max_length=20, choices=DELIVERY_TIME_CHOICES)
    order_date = models.DateTimeField(auto_now_add=True)
    is_guest_order = models.BooleanField(default=False)
    
    def __str__(self):
        if self.client:
            return f"Order #{self.id} - {self.client.username}"
        else:
            return f"Order #{self.id} - Guest: {self.guest_name}"
    
    def calculate_total(self):
        # Pricing based on package type
        price_map = {
            'Standard': 1250,  # Price per unit
            'Premium': 2500,
            'Enterprise': 3750,
        }
        if self.package_type in price_map:
            return price_map[self.package_type] * self.quantity
        return 0
    
    def get_delivery_time_display(self):
        """
        Return the human-readable delivery time
        """
        return dict(self.DELIVERY_TIME_CHOICES).get(self.delivery_time, self.delivery_time)
