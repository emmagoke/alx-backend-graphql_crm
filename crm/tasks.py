import datetime
import logging
from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

logger = logging.getLogger(__name__)

@shared_task
def generatecrmreport():
    """
    A Celery task that generates a weekly CRM report by querying the
    GraphQL endpoint and logging the results to a file.
    """
    log_file_path = "/tmp/crmreportlog.txt" # Corrected log file name
    graphql_url = "http://localhost:8000/graphql"
    logger.info("Starting CRM report generation task...")

    # Define the GraphQL query to fetch the report data
    report_query = gql("""
        query CrmReportQuery {
            crmReport {
                totalCustomers
                totalOrders
                totalRevenue
            }
        }
    """)

    try:
        transport = RequestsHTTPTransport(url=graphql_url, timeout=30)
        client = Client(transport=transport, fetch_schema_from_transport=False)
        result = client.execute(report_query)

        report_data = result.get('crmReport', {})
        customers = report_data.get('totalCustomers', 0)
        orders = report_data.get('totalOrders', 0)
        revenue = report_data.get('totalRevenue', 0.0)

        # Format the log message
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = (
            f"{timestamp} - Report: {customers} customers, "
            f"{orders} orders, {revenue} revenue.\n"
        )

        # Append the report to the log file
        with open(log_file_path, "a") as f:
            f.write(log_message)
        
        logger.info(f"Successfully generated and logged CRM report. {log_message.strip()}")
        return log_message

    except Exception as e:
        logger.error(f"Failed to generate CRM report: {e}")
        # Log the error to the file as well for debugging
        with open(log_file_path, "a") as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] ERROR generating report: {e}\n")
