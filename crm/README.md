# CRM Project with Celery Reporting

This document outlines the steps to set up and run the Celery background tasks for generating a weekly CRM report.

1. Prerequisites
   Before you begin, ensure you have Redis installed and running on your system.

On macOS (using Homebrew):

```
brew install redis
brew services start redis
```

On Debian/Ubuntu:

sudo apt-get update
sudo apt-get install redis-server
sudo systemctl enable redis-server.service

2. Installation
   Install all the required Python packages from the requirements.txt file.

pip install -r requirements.txt

3. Run Database Migrations
   Celery Beat uses the database to store its schedule. You need to run migrations to create the necessary tables for django-celery-beat.

python manage.py migrate

4. Start the Celery Worker
   The Celery worker is the process that executes your background tasks. Open a new terminal window, navigate to your project's root directory (where manage.py is), and run:

celery -A crm worker -l info

You should see the worker start up and discover the crm.tasks.generatecrmreport task.

5. Start the Celery Beat Scheduler
   Celery Beat is the scheduler. It's responsible for telling the worker when to run a task based on the schedule you defined in settings.py. Open another terminal window and run:

celery -A crm beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler

You should see the scheduler start up and acknowledge the generate-crm-report-weekly schedule.

6. Verification
   The report is scheduled to run every Monday at 6:00 AM. After it runs, you can verify its output by checking the log file. Note the log file name matches the one in the task.

cat /tmp/crmreportlog.txt

You should see entries formatted like this:
2025-07-21 06:00:00 - Report: 15 customers, 50 orders, 12345.67 revenue.
