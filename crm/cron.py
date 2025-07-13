import datetime
import logging
import requests
import json

# It's good practice to use a logger instead of print in cron jobs
logger = logging.getLogger(__name__)

def log_crm_heartbeat():
    """
    A cron job function that logs a heartbeat message to a file
    to confirm the CRM application is alive and running.
    Optionally, it also pings the GraphQL endpoint.
    """
    log_file_path = "/tmp/crm_heartbeat_log.txt"
    graphql_url = "http://localhost:8000/graphql"
    
    # 1. Format the timestamp
    # Format: DD/MM/YYYY-HH:MM:SS
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_message = f"{timestamp} CRM is alive"

    # 2. Optionally, check if the GraphQL endpoint is responsive
    try:
        # A simple query to the 'hello' field
        query = {"query": "query { hello }"}
        response = requests.post(graphql_url, json=query, timeout=10)
        
        # Check for a successful HTTP status code and a valid GraphQL response
        if response.status_code == 200 and 'data' in response.json():
            log_message += " (GraphQL endpoint is responsive)."
        else:
            error_data = response.text
            log_message += f" (GraphQL endpoint check failed with status {response.status_code}: {error_data})."
            logger.warning(f"GraphQL heartbeat check failed: {error_data}")

    except requests.exceptions.RequestException as e:
        log_message += f" (GraphQL endpoint is unreachable: {e})."
        logger.error(f"Could not connect to GraphQL endpoint for heartbeat check: {e}")

    # 3. Append the final message to the log file
    try:
        with open(log_file_path, "a") as f:
            f.write(log_message + "\n")
    except IOError as e:
        logger.error(f"Failed to write to heartbeat log file {log_file_path}: {e}")
