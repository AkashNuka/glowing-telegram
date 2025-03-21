"""
Views for user registration, authentication, and dashboards.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, LoginForm, OrderForm
from django.contrib import messages
from .models import CustomUser, AnalyticsData, Order
from django.http import HttpResponse, JsonResponse
from datetime import datetime, timedelta

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
            email='akash@watergo.com',
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
        # Fetch recent orders for owner dashboard, including guest orders
        recent_orders = Order.objects.all().order_by('-order_date')[:10]
        
        # Calculate additional metrics for owner dashboard
        total_revenue = sum(float(order.total_amount) for order in recent_orders)
        total_liters = sum(order.liters * order.quantity for order in recent_orders)
        guest_orders_count = Order.objects.filter(is_guest_order=True).count()
        
        template = 'accounts/dashboard_owner.html'
        context = {
            'recent_orders': recent_orders,
            'total_revenue': total_revenue,
            'total_liters': total_liters,
            'guest_orders_count': guest_orders_count
        }
    elif user.is_driver():
        template = 'accounts/dashboard_driver.html'
        context = {}
    else:  # Client
        # For clients, include order form and recent orders
        form = OrderForm()
        orders = Order.objects.filter(client=user).order_by('-order_date')[:5]
        template = 'accounts/dashboard_client.html'
        context = {'form': form, 'orders': orders}
    
    # Render with cache control headers
    response = render(request, template, context)
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
    
    try:
        # Get the latest analytics data from the database
        analytics = AnalyticsData.objects.latest('date_generated')
        
        analytics_data = {
            'total_orders': analytics.total_orders,
            'revenue': analytics.revenue,
            'water_delivered': analytics.water_delivered,
            'avg_order_value': analytics.avg_order_value,
            'monthly_growth': analytics.get_monthly_growth(),
            'top_clients': analytics.get_top_clients(),
            'top_drivers': analytics.get_top_drivers(),
            'monthly_data': analytics.get_monthly_data(),
            'water_by_package': analytics.get_water_by_package(),
            'order_status': analytics.get_order_status(),
            'peak_delivery_times': analytics.get_peak_delivery_times(),
            'client_growth': analytics.get_client_growth(),
        }
    except AnalyticsData.DoesNotExist:
        # Fallback to default data if no analytics data exists
        analytics_data = {
            'total_orders': 0,
            'revenue': 0,
            'water_delivered': 0,
            'avg_order_value': 0,
            'monthly_growth': {'orders': 0, 'revenue': 0, 'water': 0, 'avg_value': 0},
            'top_clients': [],
            'top_drivers': [],
            'monthly_data': {'months': [], 'revenue': [], 'orders': []},
            'water_by_package': {'labels': [], 'data': []},
            'order_status': {'labels': [], 'data': []},
            'peak_delivery_times': {'labels': [], 'data': []},
            'client_growth': {'labels': [], 'data': []}
        }
    
    return render(request, 'accounts/owner_analytics.html', {
        'analytics_data': analytics_data
    })

@login_required
def owner_drivers(request):
    """
    Display the driver management page for owner.
    """
    # Ensure only owners can access this page
    if not request.user.is_owner():
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard')
    
    # In the future, you would fetch real driver data from the database
    
    # Render with cache control headers
    response = render(request, 'accounts/owner_drivers.html')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

@login_required
def place_order(request):
    """
    Handle placing new orders from the client dashboard
    """
    if not request.user.is_client():
        messages.error(request, "Only clients can place orders.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.client = request.user
            
            # Set liters based on package type
            package_liters = {
                'Standard': 500,
                'Premium': 1000,
                'Enterprise': 1500,
            }
            order.liters = package_liters.get(order.package_type, 0)
            
            # Calculate total amount
            order.total_amount = order.calculate_total()
            
            order.save()
            messages.success(request, "Order placed successfully!")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = OrderForm()
        # Set default delivery date to tomorrow
        tomorrow = datetime.now().date() + timedelta(days=1)
        form.fields['delivery_date'].initial = tomorrow
    
    # Get user's recent orders
    orders = Order.objects.filter(client=request.user).order_by('-order_date')[:5]
    
    return render(request, 'accounts/dashboard_client.html', {
        'form': form,
        'orders': orders,
    })

@login_required
def assign_driver(request, order_id):
    """
    Assign a driver to an order
    """
    if not request.user.is_owner():
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('dashboard')
    
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        driver_id = request.POST.get('driver_id')
        try:
            driver = CustomUser.objects.get(id=driver_id, role=CustomUser.DRIVER)
            order.driver = driver
            order.status = 'processing'  # Update order status
            order.save()
            messages.success(request, f"Driver {driver.username} assigned to order #{order.id}")
        except CustomUser.DoesNotExist:
            messages.error(request, "Driver not found.")
    
    # Get available drivers
    available_drivers = CustomUser.objects.filter(role=CustomUser.DRIVER)
    
    return render(request, 'accounts/assign_driver.html', {
        'order': order,
        'available_drivers': available_drivers
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
    Handle orders from non-registered users on the homepage.
    """
    if request.method == 'POST':
        # Process the guest order
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        package_type = request.POST.get('productType')
        quantity = int(request.POST.get('quantity', 1))
        delivery_date = request.POST.get('date')
        delivery_time = request.POST.get('time')
        
        # Debug information
        print(f"Received guest order: {name}, {email}, {package_type}, {quantity}")
        
        # Calculate liters based on package type
        package_liters = {
            'Standard': 500,
            'Premium': 1000,
            'Enterprise': 1500,
        }
        liters = package_liters.get(package_type, 0)
        
        # Create a new order
        order = Order(
            guest_name=name,
            guest_email=email,
            guest_phone=phone,
            delivery_address=address,
            package_type=package_type,
            liters=liters,
            quantity=quantity,
            delivery_date=delivery_date,
            delivery_time=delivery_time,
            is_guest_order=True
        )
        
        # Calculate total
        order.total_amount = order.calculate_total()
        
        # Save the order
        order.save()
        
        # Add a success message
        messages.success(request, "Your order has been placed successfully! We'll contact you shortly to confirm.")
    
    return redirect('home')
