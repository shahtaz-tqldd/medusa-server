#!/bin/sh

set -e

echo "Starting Production Deployment"

# 1. Create network only if needed
NETWORK_NAME="medusa-network"

if ! docker network ls | grep -q "$NETWORK_NAME"; then
  echo "Creating Docker network: $NETWORK_NAME"
  docker network create $NETWORK_NAME
else
  echo "Docker network '$NETWORK_NAME' already exists"
fi

# 2. Stop existing containers gracefully
echo "Stopping existing docker-compose stack"
docker compose -f docker-compose.prod.yml down --remove-orphans

# 3. Start the stack in background
echo "Starting docker services..."
docker compose -f docker-compose.yml up -d --build --remove-orphans
