#!/bin/bash

# Exit on any error
set -e

# Get the port from environment variable, default to 8080
PORT=${PORT:-8080}

echo "Starting Lebanese News Scraper API on port $PORT..."

# Start the uvicorn server
exec uvicorn api:app --host 0.0.0.0 --port $PORT --workers 1 --timeout-keep-alive 300 