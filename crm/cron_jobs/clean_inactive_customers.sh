#!/bin/bash

# Script to clean up inactive customers (no orders in the last year)
# This script should be placed in crm/cron_jobs/clean_inactive_customers.sh

# Get the current timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Log file path
LOG_FILE="/tmp/customer_cleanup_log.txt"

# Get the project root directory (assuming script is in crm/cron_jobs/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Change to project directory
cd "$PROJECT_ROOT"

# Execute Django management command to delete inactive customers
# This command deletes customers with no orders since a year ago
DELETED_COUNT=$(python manage.py shell -c "
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer

# Calculate date one year ago
one_year_ago = timezone.now() - timedelta(days=365)

# Find customers with no orders in the last year
# Assuming Customer model has a related 'orders' field
inactive_customers = Customer.objects.filter(
    orders__isnull=True
).union(
    Customer.objects.exclude(
        orders__created_at__gte=one_year_ago
    )
).distinct()

# Count and delete
count = inactive_customers.count()
if count > 0:
    inactive_customers.delete()
    print(count)
else:
    print(0)
" 2>/dev/null)

# Check if the command executed successfully
if [ $? -eq 0 ]; then
    # Log the result with timestamp
    echo "[$TIMESTAMP] Successfully deleted $DELETED_COUNT inactive customers" >> "$LOG_FILE"
    echo "Customer cleanup completed successfully. Deleted $DELETED_COUNT customers."
else
    # Log error with timestamp
    echo "[$TIMESTAMP] ERROR: Failed to execute customer cleanup" >> "$LOG_FILE"
    echo "Error: Customer cleanup failed."
    exit 1
fi
