"""
Custom user model with role-based authentication.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models

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
