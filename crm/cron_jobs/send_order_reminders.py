#!/usr/bin/env python3

import os
import sys
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Add the project root to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, '..', '..')
sys.path.insert(0, project_root)

def get_pending_orders():
    """
    Query GraphQL endpoint for orders with order_date within the last 7 days
    """
    # Configure GraphQL client
    transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
    client = Client(transport=transport, fetch_schema_from_transport=True)
    
    # Calculate date 7 days ago
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    # GraphQL query to get orders from the last 7 days
    query = gql("""
        query GetPendingOrders($dateFilter: String!) {
            orders(orderDate_Gte: $dateFilter) {
                id
                orderDate
                customer {
                    id
                    email
                }
                status
            }
        }
    """)
    
    try:
        # Execute the query
        result = client.execute(query, variable_values={"dateFilter": seven_days_ago})
        return result.get('orders', [])
    except Exception as e:
        print(f"Error querying GraphQL endpoint: {e}")
        return []

def log_order_reminder(order_id, customer_email, timestamp):
    """
    Log order reminder to file
    """
    log_file = "/tmp/order_reminders_log.txt"
    log_entry = f"[{timestamp}] Order ID: {order_id}, Customer Email: {customer_email}\n"
    
    try:
        with open(log_file, 'a') as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Error writing to log file: {e}")

def main():
    """
    Main function to process order reminders
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        # Get pending orders from GraphQL
        pending_orders = get_pending_orders()
        
        if not pending_orders:
            log_entry = f"[{timestamp}] No pending orders found in the last 7 days\n"
            with open("/tmp/order_reminders_log.txt", 'a') as f:
                f.write(log_entry)
        else:
            # Process each pending order
            for order in pending_orders:
                order_id = order.get('id')
                customer = order.get('customer', {})
                customer_email = customer.get('email', 'No email')
                
                # Log the order reminder
                log_order_reminder(order_id, customer_email, timestamp)
        
        # Print success message
        print("Order reminders processed!")
        
    except Exception as e:
        error_msg = f"[{timestamp}] ERROR: {str(e)}\n"
        try:
            with open("/tmp/order_reminders_log.txt", 'a') as f:
                f.write(error_msg)
        except:
            pass
        print(f"Error processing order reminders: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
