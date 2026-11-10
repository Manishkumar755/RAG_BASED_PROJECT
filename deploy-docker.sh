#!/usr/bin/env bash
set -e

echo "========================================================"
echo "Starting Innefu Labs RAG Platform with Docker Compose..."
echo "========================================================"

docker-compose up --build -d

echo ""
echo "Containers started successfully!"
echo "- React Frontend:  http://localhost:3000"
echo "- FastAPI Backend: http://localhost:8000"
echo "- Swagger Docs:    http://localhost:8000/docs"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop:      docker-compose down"
