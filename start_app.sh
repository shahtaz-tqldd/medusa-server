#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "Error: .env file not found"
    exit 1
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for required commands
for cmd in docker docker-compose; do
    if ! command_exists "$cmd"; then
        echo "Error: $cmd is not installed"
        exit 1
    fi
done

# Clean Docker system
echo "Cleaning Docker system..."
docker system prune --force

# Create Docker network if it doesn't exist (now handled by compose)
echo "Creating Docker network..."
docker network inspect medusa_network >/dev/null 2>&1 || \
    docker network create medusa_network

# Start all services
echo "Starting containers..."
docker compose down --volumes --remove-orphans
docker compose up -d --build

# Wait for PostgreSQL to be ready (using service name instead of container name)
echo "Waiting for PostgreSQL to be ready..."
MAX_ATTEMPTS=30
ATTEMPT=0
until docker compose exec db pg_isready -U "$PGDB_USER" -d "$PGDB_NAME" >/dev/null 2>&1; do
    if [ $ATTEMPT -ge $MAX_ATTEMPTS ]; then
        echo "Error: PostgreSQL did not become ready in time"
        docker compose logs db
        exit 1
    fi
    ATTEMPT=$((ATTEMPT+1))
    sleep 2
done

echo "All services are up and running!"
