"""
Management command to populate the database with fake analytics data.
"""
from django.core.management.base import BaseCommand
from accounts.models import AnalyticsData

class Command(BaseCommand):
    help = 'Populates the database with fake analytics data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating fake analytics data...')
        
        # Delete existing analytics data
        AnalyticsData.objects.all().delete()
        
        # Create new analytics data
        analytics = AnalyticsData()
        analytics.total_orders = 2847
        analytics.revenue = 72500
        analytics.water_delivered = 29000
        analytics.avg_order_value = 2140
        
        # Set JSON fields
        analytics.set_monthly_growth({
            'orders': 12.5,
            'revenue': 8.2,
            'water': 10.1,
            'avg_value': -2.3
        })
        
        analytics.set_top_clients([
            {'name': 'XYZ Hotel', 'orders': 125, 'revenue': 312500, 'growth': 12},
            {'name': 'City Apartments', 'orders': 98, 'revenue': 245000, 'growth': 8},
            {'name': 'ABC Restaurant', 'orders': 87, 'revenue': 108750, 'growth': -3},
            {'name': 'Grand Hotel', 'orders': 65, 'revenue': 97500, 'growth': 15},
            {'name': 'Downtown Office', 'orders': 58, 'revenue': 87000, 'growth': 5}
        ])
        
        analytics.set_top_drivers([
            {'name': 'Rajesh Kumar', 'deliveries': 289, 'on_time': 98, 'rating': 4.5},
            {'name': 'Priya Sharma', 'deliveries': 198, 'on_time': 99, 'rating': 5.0},
            {'name': 'Sanjay Patel', 'deliveries': 178, 'on_time': 95, 'rating': 4.5},
            {'name': 'Amit Singh', 'deliveries': 156, 'on_time': 92, 'rating': 4.0},
            {'name': 'Vikram Mehta', 'deliveries': 143, 'on_time': 88, 'rating': 3.0}
        ])
        
        analytics.set_monthly_data({
            'months': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            'revenue': [15000, 18000, 22000, 25000, 28000, 30000, 35000, 40000, 42000, 45000, 50000, 72500],
            'orders': [120, 150, 180, 210, 240, 260, 280, 300, 320, 340, 360, 385]
        })
        
        analytics.set_water_by_package({
            'labels': ['500L Standard', '1000L Premium', '1500L Enterprise', 'Custom Sizes'],
            'data': [35, 40, 20, 5]
        })
        
        analytics.set_order_status({
            'labels': ['Delivered', 'In Transit', 'Processing', 'New', 'Cancelled'],
            'data': [1825, 420, 350, 210, 42]
        })
        
        analytics.set_peak_delivery_times({
            'labels': ['8-10 AM', '10-12 PM', '12-2 PM', '2-4 PM', '4-6 PM', '6-8 PM'],
            'data': [15, 25, 20, 18, 12, 10]
        })
        
        analytics.set_client_growth({
            'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            'data': [10, 12, 15, 18, 22, 25, 30, 34, 38, 45, 52, 65]
        })
        
        # Save analytics data
        analytics.save()
        
        self.stdout.write(self.style.SUCCESS('Successfully created fake analytics data!'))
