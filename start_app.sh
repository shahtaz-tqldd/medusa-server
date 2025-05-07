#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
    export $(cat .env | xargs)
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

# Create Docker network if it doesn't exist
echo "Creating Docker network..."
docker network create medusa_network || true

# Start database
echo "Starting database container..."
cd db || { echo "Error: db directory not found"; exit 1; }
docker compose down
docker compose up -d --build
cd ..

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
MAX_ATTEMPTS=30
ATTEMPT=0
until docker exec medusa_pgdb pg_isready -U "$PGDB_USER" -d "$PGDB_NAME" >/dev/null 2>&1; do
    if [ $ATTEMPT -ge $MAX_ATTEMPTS ]; then
        echo "Error: PostgreSQL did not become ready in time"
        exit 1
    fi
    ATTEMPT=$((ATTEMPT+1))
    sleep 2
done

# Start web application
echo "Starting web application..."
docker compose down
docker compose up --build --remove-orphans -d
