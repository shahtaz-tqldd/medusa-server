#!/bin/sh

# clean docker
sudo docker system prune --force

# create docker network
echo "Creating Docker network"
sudo docker network create medusa-network

echo "closing dev docker"
sudo docker compose -f docker-compose.dev.yml down

echo "running docker compose for webserver"
sudo docker compose -f docker-compose.dev.yml up --build --remove-orphans