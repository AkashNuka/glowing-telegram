"""
Forms for user registration and management.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Order

class CustomUserCreationForm(UserCreationForm):
    """
    Form for user registration with role selection (excluding owner).
    """
    # Modified role choices to exclude owner
    ROLE_CHOICES = [
        (CustomUser.DRIVER, 'Driver'),
        (CustomUser.CLIENT, 'Client'),
    ]
    
    # Override the role field to limit options
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        initial=CustomUser.CLIENT,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        
class CustomUserChangeForm(UserChangeForm):
    """
    Form for updating users.
    """
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
        }

class LoginForm(forms.Form):
    """
    Form for user login.
    """
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

class OrderForm(forms.ModelForm):
    """
    Form for creating water orders
    """
    DELIVERY_TIME_CHOICES = [
        ('morning', 'Morning (9AM - 12PM)'),
        ('afternoon', 'Afternoon (12PM - 3PM)'),
        ('evening', 'Evening (3PM - 6PM)'),
    ]
    
    delivery_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    delivery_time = forms.ChoiceField(
        choices=DELIVERY_TIME_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = Order
        fields = ('package_type', 'quantity', 'delivery_address', 'delivery_date', 'delivery_time')
        widgets = {
            'package_type': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '10'}),
            'delivery_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
