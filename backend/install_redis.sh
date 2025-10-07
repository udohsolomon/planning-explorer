#!/bin/bash

# Redis Installation Script
# Run this with: bash install_redis.sh

echo "Installing Redis..."
sudo apt update
sudo apt install -y redis-server

echo "Starting Redis..."
sudo service redis-server start

echo "Testing Redis connection..."
redis-cli ping

echo "Redis installation complete!"
echo "Expected output: PONG"
