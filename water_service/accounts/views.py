"""
Views for user registration, authentication, and dashboards.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, LoginForm
from django.contrib import messages
from .models import CustomUser
from django.http import HttpResponse, JsonResponse

def home(request):
    """
    Homepage view with e-commerce functionality.
    """
    return render(request, 'home.html')

def register(request):
    """
    Handle user registration - excluding owner role.
    """
    # Redirect authenticated users to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    # Get role from URL parameter or default to client
    role = request.GET.get('role', CustomUser.CLIENT)
    
    # Prevent direct registration of owners - redirect to client registration
    if role == CustomUser.OWNER:
        messages.warning(request, "Owner registration is not allowed. Contact administrator.")
        role = CustomUser.CLIENT
    
    # Map roles to display names
    role_display_map = {
        CustomUser.DRIVER: 'Driver',
        CustomUser.CLIENT: 'Client',
    }
    
    # Get display name for the role
    role_display = role_display_map.get(role, 'Client')
    
    if request.method == 'POST':
        # Ensure no owner registration attempts via POST
        if request.POST.get('role') == CustomUser.OWNER:
            messages.error(request, "Owner registration is not allowed.")
            form = CustomUserCreationForm(initial={'role': CustomUser.CLIENT})
            return render(request, 'accounts/register.html', {
                'form': form,
                'role': CustomUser.CLIENT,
                'role_display': 'Client',
            })
            
        # Use the role from the form submission
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect('dashboard')
        else:
            messages.error(request, "Registration failed. Please correct the errors.")
    else:
        # Pre-populate the form with the selected role
        form = CustomUserCreationForm(initial={'role': role})
    
    return render(request, 'accounts/register.html', {
        'form': form,
        'role': role,
        'role_display': role_display,
    })

def user_login(request):
    """
    Handle user login with role-specific logic.
    """
    # Redirect already authenticated users to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # Create hardcoded owner account for 'akash' if it doesn't exist
    if not CustomUser.objects.filter(username='akash').exists():
        # Create the owner account
        owner_user = CustomUser.objects.create_user(
            username='akash',
            email='akash@waterservice.com',
            password='abcde12345',
            role=CustomUser.OWNER
        )
        print("Owner account created successfully: akash/abcde12345")
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')
        
        if not username or not password:
            messages.error(request, "Username and password are required.")
            return render(request, 'accounts/login.html')
        
        # Try to authenticate the user
        user = authenticate(username=username, password=password)
        
        if user is not None:
            # Check if the user's role matches the selected role
            if role == 'owner' and user.role != CustomUser.OWNER:
                messages.error(request, "This account doesn't have owner privileges.")
            elif role == 'driver' and user.role != CustomUser.DRIVER:
                messages.error(request, "This account doesn't have driver privileges.")
            elif role == 'client' and user.role != CustomUser.CLIENT:
                messages.error(request, "This account isn't registered as a client.")
            else:
                # Role matches, proceed with login
                login(request, user)
                messages.success(request, f"Welcome, {username}!")
                return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    
    # Add cache-control headers to prevent caching the login page
    response = render(request, 'accounts/login.html')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

@login_required
def dashboard(request):
    """
    Display appropriate dashboard based on user role.
    """
    user = request.user
    
    # Set up the correct template based on user role
    if user.is_owner():
        template = 'accounts/dashboard_owner.html'
    elif user.is_driver():
        template = 'accounts/dashboard_driver.html'
    else:  # Client
        template = 'accounts/dashboard_client.html'
    
    # Render with cache control headers
    response = render(request, template)
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

@login_required
def owner_analytics(request):
    """
    Display the analytics dashboard for owner.
    """
    # Ensure only owners can access this page
    if not request.user.is_owner():
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard')
    
    # Sample analytics data (in a real app, this would come from a database)
    analytics_data = {
        'total_orders': 2847,
        'revenue': 72500,
        'water_delivered': 29000,
        'avg_order_value': 2140,
        'monthly_growth': {
            'orders': 12.5,
            'revenue': 8.2,
            'water': 10.1,
            'avg_value': -2.3
        },
        'top_clients': [
            {'name': 'XYZ Hotel', 'orders': 125, 'revenue': 312500, 'growth': 12},
            {'name': 'City Apartments', 'orders': 98, 'revenue': 245000, 'growth': 8},
            {'name': 'ABC Restaurant', 'orders': 87, 'revenue': 108750, 'growth': -3},
            {'name': 'Grand Hotel', 'orders': 65, 'revenue': 97500, 'growth': 15},
            {'name': 'Downtown Office', 'orders': 58, 'revenue': 87000, 'growth': 5}
        ],
        'top_drivers': [
            {'name': 'Rajesh Kumar', 'deliveries': 289, 'on_time': 98, 'rating': 4.5},
            {'name': 'Priya Sharma', 'deliveries': 198, 'on_time': 99, 'rating': 5.0},
            {'name': 'Sanjay Patel', 'deliveries': 178, 'on_time': 95, 'rating': 4.5},
            {'name': 'Amit Singh', 'deliveries': 156, 'on_time': 92, 'rating': 4.0},
            {'name': 'Vikram Mehta', 'deliveries': 143, 'on_time': 88, 'rating': 3.0}
        ],
        # Add monthly revenue and orders data
        'monthly_data': {
            'months': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            'revenue': [15000, 18000, 22000, 25000, 28000, 30000, 35000, 40000, 42000, 45000, 50000, 72500],
            'orders': [120, 150, 180, 210, 240, 260, 280, 300, 320, 340, 360, 385]
        },
        # Add water usage by package type
        'water_by_package': {
            'labels': ['500L Standard', '1000L Premium', '1500L Enterprise', 'Custom Sizes'],
            'data': [35, 40, 20, 5]
        },
        # Add order status distribution
        'order_status': {
            'labels': ['Delivered', 'In Transit', 'Processing', 'New', 'Cancelled'],
            'data': [1825, 420, 350, 210, 42]
        },
        # Add peak delivery times
        'peak_delivery_times': {
            'labels': ['8-10 AM', '10-12 PM', '12-2 PM', '2-4 PM', '4-6 PM', '6-8 PM'],
            'data': [15, 25, 20, 18, 12, 10]
        },
        # Add client growth data
        'client_growth': {
            'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            'data': [10, 12, 15, 18, 22, 25, 30, 34, 38, 45, 52, 65]
        }
    }
    
    return render(request, 'accounts/owner_analytics.html', {
        'analytics_data': analytics_data
    })

def logout_confirmation(request):
    """
    Display logout confirmation page that handles history cleanup.
    """
    # Set cache control headers
    response = render(request, 'accounts/logout_confirmation.html')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

def check_auth(request):
    """
    Check if the user is authenticated for AJAX requests.
    """
    return JsonResponse({'authenticated': request.user.is_authenticated})

def guest_order(request):
    """
    Handle orders from non-registered users.
    """
    if request.method == 'POST':
        # Process the guest order
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        product_type = request.POST.get('product_type')
        liters = request.POST.get('liters')
        quantity = request.POST.get('quantity')
    
    return redirect('home')
