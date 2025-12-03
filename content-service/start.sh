#!/bin/bash

echo "Starting Content Service..."

# Check for .env file
if [ ! -f .env ]; then
    echo "WARNING: .env file not found. Using default values."
    cp .env.example .env 2>/dev/null || true
fi

# Start services with docker-compose
docker-compose up -d

echo "Services started:"
echo "- Content Service API: http://localhost:8000"
echo "- API Documentation: http://localhost:8000/docs"
echo "- Health Check: http://localhost:8000/health"
echo "- Status: http://localhost:8000/status"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"