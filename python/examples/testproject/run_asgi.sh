#!/bin/bash

# Run Django with Uvicorn ASGI server
# Usage: ./run_asgi.sh [host] [port] [workers]

HOST=${1:-0.0.0.0}
PORT=${2:-8000}
WORKERS=${3:-4}

echo "Starting Django with Uvicorn ASGI server..."
echo "Host: $HOST:$PORT"
echo "Workers: $WORKERS"
echo "----------------------------------------"

# Using uvicorn directly
uvicorn testproject.asgi:application \
    --host $HOST \
    --port $PORT \
    --workers $WORKERS \
    --loop uvloop \
    --http httptools \
    --log-level info