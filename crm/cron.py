import datetime
import logging
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport, log as gql_log
import requests

# It's good practice to use a logger instead of print in cron jobs
logger = logging.getLogger(__name__)

# Suppress noisy gql transport logs for simple heartbeat
gql_log.setLevel(logging.WARNING)

def log_crm_heartbeat():
    """
    A cron job function that logs a heartbeat message to a file
    to confirm the CRM application is alive and running.
    It also pings the GraphQL endpoint's 'hello' field.
    """
    log_file_path = "/tmp/crm_heartbeat_log.txt"
    graphql_url = "http://localhost:8000/graphql"
    
    # 1. Format the timestamp
    # Format: DD/MM/YYYY-HH:MM:SS
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_message = f"{timestamp} CRM is alive"

    # 2. Check if the GraphQL endpoint is responsive using gql
    try:
        # Setup a temporary transport and client for the check
        transport = RequestsHTTPTransport(url=graphql_url, timeout=10)
        client = Client(transport=transport, fetch_schema_from_transport=False)
        
        # Define and execute a simple query to the 'hello' field
        hello_query = gql("query { hello }")
        result = client.execute(hello_query)
        
        # Check for a valid GraphQL response
        if result and 'hello' in result:
            log_message += " (GraphQL endpoint is responsive)."
        else:
            log_message += f" (GraphQL endpoint check failed: Unexpected response {result})."
            logger.warning(f"GraphQL heartbeat check failed: {result}")

    except Exception as e:
        log_message += f" (GraphQL endpoint is unreachable or query failed: {e})."
        logger.error(f"Could not connect to GraphQL endpoint for heartbeat check: {e}")

    # 3. Append the final message to the log file
    try:
        with open(log_file_path, "a") as f:
            f.write(log_message + "\n")
    except IOError as e:
        logger.error(f"Failed to write to heartbeat log file {log_file_path}: {e}")


def update_low_stock():
    """
    Execute GraphQL mutation to update low-stock products (stock < 10)
    and log the updates every 12 hours.
    """
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_file = "/tmp/low_stock_updates_log.txt"
    
    try:
        # GraphQL endpoint URL
        graphql_url = "http://localhost:8000/graphql"
        
        # GraphQL mutation to update low-stock products
        mutation = {
            "query": """
                mutation {
                    updateLowStockProducts {
                        updatedProducts {
                            id
                            name
                            stock
                        }
                        success
                        message
                    }
                }
            """
        }
        
        # Execute the mutation
        response = requests.post(
            graphql_url,
            json=mutation,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for GraphQL errors
            if 'errors' in data:
                error_msg = f"[{timestamp}] GraphQL Error: {data['errors']}\n"
                with open(log_file, 'a') as f:
                    f.write(error_msg)
                return
            
            # Process the mutation result
            mutation_data = data.get('data', {}).get('updateLowStockProducts', {})
            updated_products = mutation_data.get('updatedProducts', [])
            success = mutation_data.get('success', False)
            message = mutation_data.get('message', 'No message')
            
            # Log the results
            log_entry = f"[{timestamp}] {message}\n"
            
            if updated_products:
                log_entry += f"[{timestamp}] Updated products:\n"
                for product in updated_products:
                    product_name = product.get('name', 'Unknown')
                    new_stock = product.get('stock', 0)
                    log_entry += f"[{timestamp}] - {product_name}: New stock level = {new_stock}\n"
            else:
                log_entry += f"[{timestamp}] No products were updated\n"
            
            # Write to log file
            with open(log_file, 'a') as f:
                f.write(log_entry)
                
        else:
            error_msg = f"[{timestamp}] HTTP Error: {response.status_code} - {response.text}\n"
            with open(log_file, 'a') as f:
                f.write(error_msg)
    
    except requests.exceptions.RequestException as e:
        error_msg = f"[{timestamp}] Request Error: {str(e)}\n"
        try:
            with open(log_file, 'a') as f:
                f.write(error_msg)
        except:
            print(error_msg.strip())
    
    except Exception as e:
        error_msg = f"[{timestamp}] Unexpected Error: {str(e)}\n"
        try:
            with open(log_file, 'a') as f:
                f.write(error_msg)
        except:
            print(error_msg.strip())


def test_heartbeat():
    """
    Test function to manually trigger heartbeat logging.
    Usage: python manage.py shell -c "from crm.cron import test_heartbeat; test_heartbeat()"
    """
    print("Testing CRM heartbeat...")
    log_crm_heartbeat()
    print("Heartbeat logged successfully!")
    
    # Display recent log entries
    try:
        with open("/tmp/crm_heartbeat_log.txt", 'r') as f:
            lines = f.readlines()
            print("\nRecent heartbeat logs:")
            for line in lines[-5:]:  # Show last 5 entries
                print(line.strip())
    except FileNotFoundError:
        print("No heartbeat log file found.")
    except Exception as e:
        print(f"Error reading log file: {e}")


def test_low_stock_update():
    """
    Test function to manually trigger low stock update.
    Usage: python manage.py shell -c "from crm.cron import test_low_stock_update; test_low_stock_update()"
    """
    print("Testing low stock update...")
    update_low_stock()
    print("Low stock update completed!")
    
    # Display recent log entries
    try:
        with open("/tmp/low_stock_updates_log.txt", 'r') as f:
            lines = f.readlines()
            print("\nRecent low stock update logs:")
            for line in lines[-10:]:  # Show last 10 entries
                print(line.strip())
    except FileNotFoundError:
        print("No low stock update log file found.")
    except Exception as e:
        print(f"Error reading log file: {e}")
