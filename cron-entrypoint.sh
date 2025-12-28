#!/bin/bash
set -e

echo "Exporting environment variables..."
printenv > /etc/environment

echo "Starting cron..."
cron -f -L /var/log/cron.log

