#!/bin/bash
# Production deployment script for WhatsApp Automation MVP

set -e

echo "🚀 Deploying WhatsApp Automation MVP to Production"

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

# Check if .env file exists
if [ ! -f .env ]; then
    print_error ".env file not found. Please create it with your production configuration."
    exit 1
fi

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

# Validate required environment variables
print_status "Validating environment variables..."
required_vars=(
    "DATABASE_URL"
    "SECRET_KEY"
    "WHATSAPP_TOKEN"
    "PHONE_NUMBER_ID"
    "BUSINESS_ID"
    "WEBHOOK_VERIFY_TOKEN"
)

for var in "${required_vars[@]}"; do
    if ! grep -q "^${var}=" .env; then
        print_error "Required environment variable ${var} is not set in .env file"
        exit 1
    fi
done

print_success "Environment variables validated"

# Build production images
print_status "Building production Docker images..."
docker-compose -f docker-compose.prod.yml build

# Stop existing production services
print_status "Stopping existing production services..."
docker-compose -f docker-compose.prod.yml down

# Start production services
print_status "Starting production services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
print_status "Waiting for services to be ready..."
sleep 15

# Check service health
print_status "Checking service health..."

# Check PostgreSQL
if docker-compose -f docker-compose.prod.yml exec -T postgres pg_isready -U automatizaciones_user -d automatizaciones > /dev/null 2>&1; then
    print_success "PostgreSQL is ready"
else
    print_error "PostgreSQL is not ready"
    exit 1
fi

# Check Redis
if docker-compose -f docker-compose.prod.yml exec -T redis redis-cli -a ${REDIS_PASSWORD:-automatizaciones_password} ping > /dev/null 2>&1; then
    print_success "Redis is ready"
else
    print_warning "Redis authentication may be required"
fi

# Check Backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_success "Backend API is ready"
else
    print_warning "Backend API is not ready yet, but services are starting..."
fi

print_success "Production deployment completed!"
echo ""
echo "📋 Production Services:"
echo "  • Backend API: http://localhost:8000"
echo "  • API Documentation: http://localhost:8000/docs"
echo "  • PostgreSQL: localhost:5432"
echo "  • Redis: localhost:6379"
echo ""
echo "🔧 Production Commands:"
echo "  • View logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "  • Stop services: docker-compose -f docker-compose.prod.yml down"
echo "  • Restart services: docker-compose -f docker-compose.prod.yml restart"
echo "  • Scale workers: docker-compose -f docker-compose.prod.yml up -d --scale celery_worker=3"
echo ""
echo "🎉 Production deployment successful!"
