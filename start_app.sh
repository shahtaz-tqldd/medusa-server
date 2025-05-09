#!/bin/sh
sudo systemctl stop postgresql

# clean docker
sudo docker system prune --force

# create docker network
echo "Creating Docker network"
sudo docker network create medusa-network

# run the database
echo "cd into db"
cd db
echo "running docker compose for database"
sudo docker compose build && sudo docker compose up -d

echo "cd into base directory"
cd ..

echo "closing local and dev and prod docker"
sudo docker compose -f docker-compose.local.yml down

echo "running docker compose for webserver"
sudo docker compose -f docker-compose.local.yml up --build --remove-orphans