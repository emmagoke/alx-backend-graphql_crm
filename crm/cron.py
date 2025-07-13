import datetime
import logging
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport, log as gql_log

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
    
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_message = f"{timestamp} CRM is alive"

    try:
        transport = RequestsHTTPTransport(url=graphql_url, timeout=10)
        client = Client(transport=transport, fetch_schema_from_transport=False)
        hello_query = gql("query { hello }")
        result = client.execute(hello_query)
        
        if result and 'hello' in result:
            log_message += " (GraphQL endpoint is responsive)."
        else:
            log_message += f" (GraphQL endpoint check failed: Unexpected response {result})."
            logger.warning(f"GraphQL heartbeat check failed: {result}")

    except Exception as e:
        log_message += f" (GraphQL endpoint is unreachable or query failed: {e})."
        logger.error(f"Could not connect to GraphQL endpoint for heartbeat check: {e}")

    try:
        with open(log_file_path, "a") as f:
            f.write(log_message + "\n")
    except IOError as e:
        logger.error(f"Failed to write to heartbeat log file {log_file_path}: {e}")


def update_low_stock():
    """
    Executes a GraphQL mutation to find and restock low-stock products,
    then logs the results to a file.
    """
    log_file_path = "/tmp/low_stock_updates_log.txt"
    graphql_url = "http://localhost:8000/graphql"
    logger.info("Starting low stock update job...")

    # CORRECTED: The mutation name is 'updateLowStock', matching the schema.
    mutation_query = gql("""
        mutation UpdateLowStock {
            updateLowStock {
                success
                message
                updatedProducts {
                    name
                    stock
                }
            }
        }
    """)

    try:
        transport = RequestsHTTPTransport(url=graphql_url, timeout=20)
        client = Client(transport=transport, fetch_schema_from_transport=False)
        result = client.execute(mutation_query)

        update_data = result.get('updateLowStock', {})
        if update_data.get('success'):
            updated_products = update_data.get('updatedProducts', [])
            message = update_data.get('message', 'Update successful.')
            logger.info(message)

            if updated_products:
                with open(log_file_path, "a") as f:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    f.write(f"--- Low Stock Update Logged at {timestamp} ---\n")
                    f.write(f"    {message}\n")
                    for product in updated_products:
                        f.write(f"    - Product: {product['name']}, New Stock: {product['stock']}\n")
                    f.write("---\n\n")
            else:
                 with open(log_file_path, "a") as f:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    f.write(f"--- Low Stock Update Logged at {timestamp} ---\n")
                    f.write(f"    {message}\n")
                    f.write("---\n\n")
        else:
            message = update_data.get('message', 'Mutation failed without a specific message.')
            logger.error(f"Low stock update mutation failed: {message}")

    except Exception as e:
        logger.error(f"An error occurred during the low stock update job: {e}")
        with open(log_file_path, "a") as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] ERROR during update: {e}\n")


def test_heartbeat():
    """
    Test function to manually trigger heartbeat logging.
    """
    print("Testing CRM heartbeat...")
    log_crm_heartbeat()
    print("Heartbeat logged successfully!")


def test_low_stock_update():
    """
    Test function to manually trigger low stock update.
    """
    print("Testing low stock update...")
    update_low_stock()
    print("Low stock update completed!")
