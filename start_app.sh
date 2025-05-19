#!/bin/sh

# Stop PostgreSQL service if necessary
echo "Stopping PostgreSQL service"
sudo systemctl stop postgresql

# Clean up Docker system
echo "Cleaning up Docker system"
sudo docker system prune --force

# Create Docker network
echo "Creating Docker network"
sudo docker network create medusa-network

# Run the database
echo "Changing directory to db"
cd db
echo "Building and running Docker compose for database"
sudo docker compose build && sudo docker compose up -d

# Change back to the base directory
echo "Changing back to the base directory"
cd ..

# Stop and remove any existing dev and prod Docker containers
echo "Stopping and removing existing Docker containers"
sudo docker compose -f docker-compose.dev.yml down

# Build and run Docker compose for the web server
echo "Building and running Docker compose for web server"
sudo docker compose -f docker-compose.dev.yml up --build --remove-orphans
