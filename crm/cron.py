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
