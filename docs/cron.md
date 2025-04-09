# Cron

Cron is a time-based job scheduler in Unix-like operating systems. In this project, we use a Docker container with cron to run scheduled tasks that need to be executed periodically in an isolated but up-to-date environment.

## Overview

Using cron with Docker provides several benefits:
- Isolation from the main web application
- Scheduled task execution
- Environment consistency
- Easy management of dependencies

## Dockerfile.cron

The project includes a specialized Dockerfile (`Dockerfile.cron`) for creating a container that runs cron jobs. This container:

1. Uses Python as the base image
2. Installs necessary system dependencies
3. Sets up a dedicated user for security
4. Installs the application code
5. Configures a Python virtual environment
6. Installs application dependencies
7. Sets up the crontab configuration

## Crontab Configuration

The crontab file defines which commands run and when they execute. The syntax follows the standard cron format:

minute hour day_of_month month day_of_week command

Example crontab:
```
* * * * * /app/.venv/bin/python /app/manage.py check >> /var/log/app-check.log 2>&1
```

This example runs the Django `check` command every minute and logs the output to `/var/log/app-check.log`.

## Container Entrypoint

The `cron-entrypoint.sh` script prepares the environment and starts the cron service:

1. Exports all environment variables so they're available to cron jobs
2. Starts cron in foreground mode
3. Directs logs to `/var/log/cron.log`

## How to Add a New Cron Job

To add a new scheduled task:

1. Edit the `crontab` file in the project root
2. Add your command using the correct cron syntax
3. Ensure commands use the full path to the Python interpreter in the virtual environment: `/app/.venv/bin/python`
4. Rebuild the cron container

## Running the Cron Container

Using the Makefile commands:

```bash
# Build the cron container
make docker-cron-build

# Run the cron container (development)
make docker-cron-run

# Run the cron container (production)
make docker-cron-run-prod
```

Or using direct Docker commands:

```bash
docker build -f Dockerfile.cron -t pyaa-cron .
docker run -d --name pyaa-cron pyaa-cron
```

## Viewing Logs

To check if your cron jobs are running:

```bash
docker logs pyaa-cron
```

You can also check the specific log files inside the container:

```bash
docker exec pyaa-cron cat /var/log/cron.log
docker exec pyaa-cron cat /var/log/app-check.log
```

