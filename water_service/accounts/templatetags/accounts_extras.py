"""
Custom template tags and filters for the accounts app.
"""
from django import template
import builtins  # Import Python's built-in functions

register = template.Library()

@register.filter
def intcomma(value):
    """
    Converts an integer to a string containing commas every three digits.
    For example, 3000 becomes '3,000'.
    """
    try:
        value = int(value)
        return f"{value:,}"
    except (ValueError, TypeError):
        return value

@register.filter
def abs(value):
    """
    Returns the absolute value of a number.
    """
    try:
        return builtins.abs(float(value))  # Use Python's built-in abs function
    except (ValueError, TypeError):
        return value
