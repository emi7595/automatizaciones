#!/bin/bash
# Development script for WhatsApp Automation MVP

set -e

echo "🚀 Starting WhatsApp Automation MVP Development Environment"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "docker-compose is not installed. Please install docker-compose and try again."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    print_status "Creating .env file from template..."
    cp env.example .env
    print_warning "Please edit .env file with your actual configuration values"
fi

# Build and start services
print_status "Building Docker images..."
docker-compose build

print_status "Starting development environment..."
docker-compose up -d

# Wait for services to be healthy
print_status "Waiting for services to be ready..."
sleep 10

# Check service health
print_status "Checking service health..."

# Check PostgreSQL
if docker-compose exec -T postgres pg_isready -U automatizaciones_user -d automatizaciones > /dev/null 2>&1; then
    print_success "PostgreSQL is ready"
else
    print_error "PostgreSQL is not ready"
    exit 1
fi

# Check Redis
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    print_success "Redis is ready"
else
    print_error "Redis is not ready"
    exit 1
fi

# Check Backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_success "Backend API is ready"
else
    print_warning "Backend API is not ready yet, but services are starting..."
fi

print_success "Development environment is ready!"
echo ""
echo "📋 Available Services:"
echo "  • Backend API: http://localhost:8000"
echo "  • API Documentation: http://localhost:8000/docs"
echo "  • PostgreSQL: localhost:5432"
echo "  • Redis: localhost:6379"
echo ""
echo "🔧 Useful Commands:"
echo "  • View logs: docker-compose logs -f"
echo "  • Stop services: docker-compose down"
echo "  • Restart services: docker-compose restart"
echo "  • Access database: docker-compose exec postgres psql -U automatizaciones_user -d automatizaciones"
echo "  • Access Redis: docker-compose exec redis redis-cli"
echo ""
echo "🎉 Happy coding!"
