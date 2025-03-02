"""
Forms for user registration and management.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

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
