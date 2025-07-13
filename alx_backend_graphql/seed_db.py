import os
import sys
import django
from django.db import transaction
from decimal import Decimal
from django.utils import timezone
from datetime import datetime, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql.settings')  # Replace with your project name
django.setup()

from crm.models import Customer, Product, Order

def clear_data():
    """Clear existing data"""
    print("Clearing existing data...")
    Order.objects.all().delete()
    Product.objects.all().delete()
    Customer.objects.all().delete()
    print("Data cleared successfully.")

def seed_customers():
    """Create sample customers"""
    print("Creating customers...")
    
    customers_data = [
        {
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'phone': '+1234567890'
        },
        {
            'name': 'Jane Smith',
            'email': 'jane.smith@example.com',
            'phone': '+1-987-654-3210'
        },
        {
            'name': 'Bob Johnson',
            'email': 'bob.johnson@example.com',
            'phone': '555-123-4567'
        },
        {
            'name': 'Alice Brown',
            'email': 'alice.brown@example.com',
            'phone': '+1 (555) 987-6543'
        },
        {
            'name': 'Charlie Wilson',
            'email': 'charlie.wilson@example.com',
            'phone': None  # Test customer without phone
        },
        {
            'name': 'Diana Davis',
            'email': 'diana.davis@example.com',
            'phone': '+44 20 7946 0958'  # UK number
        },
        {
            'name': 'Eve Miller',
            'email': 'eve.miller@example.com',
            'phone': '+1 555 222 3333'
        },
        {
            'name': 'Frank Garcia',
            'email': 'frank.garcia@example.com',
            'phone': '(555) 444-5555'
        },
        {
            'name': 'Grace Lee',
            'email': 'grace.lee@example.com',
            'phone': '+1-555-666-7777'
        },
        {
            'name': 'Henry Taylor',
            'email': 'henry.taylor@example.com',
            'phone': '555.888.9999'
        }
    ]
    
    customers = []
    for customer_data in customers_data:
        customer = Customer.objects.create(**customer_data)
        customers.append(customer)
        print(f"Created customer: {customer.name}")
    
    print(f"Created {len(customers)} customers.")
    return customers

def seed_products():
    """Create sample products"""
    print("Creating products...")
    
    products_data = [
        {
            'name': 'Laptop',
            'price': Decimal('999.99'),
            'stock': 50
        },
        {
            'name': 'Desktop Computer',
            'price': Decimal('1299.99'),
            'stock': 25
        },
        {
            'name': 'Smartphone',
            'price': Decimal('699.99'),
            'stock': 100
        },
        {
            'name': 'Tablet',
            'price': Decimal('399.99'),
            'stock': 75
        },
        {
            'name': 'Wireless Mouse',
            'price': Decimal('29.99'),
            'stock': 200
        },
        {
            'name': 'Mechanical Keyboard',
            'price': Decimal('149.99'),
            'stock': 80
        },
        {
            'name': 'Monitor 27"',
            'price': Decimal('299.99'),
            'stock': 40
        },
        {
            'name': 'Webcam HD',
            'price': Decimal('79.99'),
            'stock': 60
        },
        {
            'name': 'Headphones',
            'price': Decimal('199.99'),
            'stock': 90
        },
        {
            'name': 'USB Flash Drive',
            'price': Decimal('19.99'),
            'stock': 300
        },
        {
            'name': 'External Hard Drive',
            'price': Decimal('119.99'),
            'stock': 45
        },
        {
            'name': 'Graphics Card',
            'price': Decimal('599.99'),
            'stock': 20
        },
        {
            'name': 'RAM 16GB',
            'price': Decimal('89.99'),
            'stock': 100
        },
        {
            'name': 'SSD 1TB',
            'price': Decimal('129.99'),
            'stock': 70
        },
        {
            'name': 'Printer',
            'price': Decimal('179.99'),
            'stock': 30
        }
    ]
    
    products = []
    for product_data in products_data:
        product = Product.objects.create(**product_data)
        products.append(product)
        print(f"Created product: {product.name} - ${product.price}")
    
    print(f"Created {len(products)} products.")
    return products

def seed_orders(customers, products):
    """Create sample orders"""
    print("Creating orders...")
    
    orders_data = [
        {
            'customer_index': 0,  # John Doe
            'product_indices': [0, 4, 5],  # Laptop, Wireless Mouse, Mechanical Keyboard
            'days_ago': 5
        },
        {
            'customer_index': 1,  # Jane Smith
            'product_indices': [2, 8],  # Smartphone, Headphones
            'days_ago': 3
        },
        {
            'customer_index': 2,  # Bob Johnson
            'product_indices': [1, 6, 4],  # Desktop Computer, Monitor, Wireless Mouse
            'days_ago': 7
        },
        {
            'customer_index': 3,  # Alice Brown
            'product_indices': [3, 7],  # Tablet, Webcam HD
            'days_ago': 2
        },
        {
            'customer_index': 4,  # Charlie Wilson
            'product_indices': [9, 10],  # USB Flash Drive, External Hard Drive
            'days_ago': 1
        },
        {
            'customer_index': 0,  # John Doe (second order)
            'product_indices': [11, 12],  # Graphics Card, RAM 16GB
            'days_ago': 10
        },
        {
            'customer_index': 5,  # Diana Davis
            'product_indices': [13, 14],  # SSD 1TB, Printer
            'days_ago': 4
        },
        {
            'customer_index': 6,  # Eve Miller
            'product_indices': [2, 3, 8],  # Smartphone, Tablet, Headphones
            'days_ago': 6
        },
        {
            'customer_index': 7,  # Frank Garcia
            'product_indices': [0, 5, 6],  # Laptop, Mechanical Keyboard, Monitor
            'days_ago': 8
        },
        {
            'customer_index': 8,  # Grace Lee
            'product_indices': [4, 7, 9],  # Wireless Mouse, Webcam HD, USB Flash Drive
            'days_ago': 12
        },
        {
            'customer_index': 9,  # Henry Taylor
            'product_indices': [1, 11, 12, 13],  # Desktop Computer, Graphics Card, RAM 16GB, SSD 1TB
            'days_ago': 15
        },
        {
            'customer_index': 1,  # Jane Smith (second order)
            'product_indices': [14],  # Printer
            'days_ago': 9
        }
    ]
    
    orders = []
    for order_data in orders_data:
        customer = customers[order_data['customer_index']]
        order_products = [products[i] for i in order_data['product_indices']]
        
        # Calculate total amount
        total_amount = sum(product.price for product in order_products)
        
        # Create order date
        order_date = timezone.now() - timedelta(days=order_data['days_ago'])
        
        # Create order
        order = Order.objects.create(
            customer=customer,
            total_amount=total_amount,
            order_date=order_date
        )
        
        # Add products to order
        order.products.set(order_products)
        
        orders.append(order)
        product_names = [p.name for p in order_products]
        print(f"Created order for {customer.name}: {', '.join(product_names)} - Total: ${total_amount}")
    
    print(f"Created {len(orders)} orders.")
    return orders

def seed_database():
    """Main seeding function"""
    print("Starting database seeding...")
    
    try:
        with transaction.atomic():
            # Clear existing data
            # clear_data()
            
            # Seed data
            customers = seed_customers()
            products = seed_products()
            orders = seed_orders(customers, products)
            
            print(f"\nSeeding completed successfully!")
            print(f"Created: {len(customers)} customers, {len(products)} products, {len(orders)} orders")
            
    except Exception as e:
        print(f"Error during seeding: {e}")
        sys.exit(1)

if __name__ == "__main__":
    seed_database()
