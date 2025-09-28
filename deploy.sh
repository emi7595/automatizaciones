#!/bin/bash

# 🚀 WhatsApp Automation MVP - Deployment Script
# This script deploys both backend API and worker services

set -e

echo "🚀 Starting WhatsApp Automation MVP Deployment..."

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
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Check if docker-compose is available
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        print_error "docker-compose is not installed. Please install docker-compose and try again."
        exit 1
    fi
    print_success "docker-compose is available"
}

# Deploy backend API
deploy_backend() {
    print_status "Deploying Backend API..."
    
    cd backend
    
    # Check if .env file exists
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from env.example..."
        cp env.example .env
        print_warning "Please update .env file with your configuration before continuing."
        read -p "Press Enter to continue after updating .env file..."
    fi
    
    # Build and start backend services
    print_status "Building and starting backend services..."
    docker-compose up --build -d
    
    # Wait for services to be healthy
    print_status "Waiting for backend services to be healthy..."
    sleep 10
    
    # Check if backend is running
    if docker-compose ps | grep -q "Up"; then
        print_success "Backend API deployed successfully!"
    else
        print_error "Backend API deployment failed!"
        docker-compose logs
        exit 1
    fi
    
    cd ..
}

# Deploy worker services
deploy_worker() {
    print_status "Deploying Worker Services..."
    
    cd backend-worker
    
    # Check if .env file exists
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from env.example..."
        cp env.example .env
        print_warning "Please update .env file with your configuration before continuing."
        read -p "Press Enter to continue after updating .env file..."
    fi
    
    # Build and start worker services
    print_status "Building and starting worker services..."
    docker-compose up --build -d
    
    # Wait for services to be healthy
    print_status "Waiting for worker services to be healthy..."
    sleep 10
    
    # Check if workers are running
    if docker-compose ps | grep -q "Up"; then
        print_success "Worker services deployed successfully!"
    else
        print_error "Worker services deployment failed!"
        docker-compose logs
        exit 1
    fi
    
    cd ..
}

# Deploy production
deploy_production() {
    print_status "Deploying Production Environment..."
    
    # Deploy backend API
    cd backend
    print_status "Deploying Backend API (Production)..."
    docker-compose -f docker-compose.prod.yml up --build -d
    cd ..
    
    # Deploy worker services
    cd backend-worker
    print_status "Deploying Worker Services (Production)..."
    docker-compose -f docker-compose.prod.yml up --build -d
    cd ..
    
    print_success "Production deployment completed!"
}

# Show status
show_status() {
    print_status "Checking deployment status..."
    
    echo ""
    echo "📊 Backend API Status:"
    cd backend
    docker-compose ps
    cd ..
    
    echo ""
    echo "🤖 Worker Services Status:"
    cd backend-worker
    docker-compose ps
    cd ..
    
    echo ""
    echo "🌐 API Endpoints:"
    echo "  - API Docs: http://localhost:8000/docs"
    echo "  - Health Check: http://localhost:8000/health"
    echo "  - Messages API: http://localhost:8000/api/messages/"
    echo "  - Automations API: http://localhost:8000/api/automations/"
    echo "  - Webhooks: http://localhost:8000/webhooks/whatsapp"
}

# Stop services
stop_services() {
    print_status "Stopping all services..."
    
    # Stop backend
    cd backend
    docker-compose down
    cd ..
    
    # Stop workers
    cd backend-worker
    docker-compose down
    cd ..
    
    print_success "All services stopped!"
}

# Clean up
cleanup() {
    print_status "Cleaning up Docker resources..."
    
    # Stop and remove containers
    stop_services
    
    # Remove unused images
    docker image prune -f
    
    print_success "Cleanup completed!"
}

# Show logs
show_logs() {
    local service=$1
    
    if [ "$service" = "backend" ]; then
        cd backend
        docker-compose logs -f
    elif [ "$service" = "worker" ]; then
        cd backend-worker
        docker-compose logs -f
    else
        print_error "Please specify 'backend' or 'worker'"
        exit 1
    fi
}

# Main script
main() {
    case "${1:-deploy}" in
        "deploy")
            check_docker
            check_docker_compose
            deploy_backend
            deploy_worker
            show_status
            ;;
        "deploy-prod")
            check_docker
            check_docker_compose
            deploy_production
            show_status
            ;;
        "status")
            show_status
            ;;
        "stop")
            stop_services
            ;;
        "cleanup")
            cleanup
            ;;
        "logs")
            show_logs "$2"
            ;;
        "help")
            echo "Usage: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  deploy      Deploy development environment (default)"
            echo "  deploy-prod Deploy production environment"
            echo "  status      Show deployment status"
            echo "  stop        Stop all services"
            echo "  cleanup     Clean up Docker resources"
            echo "  logs        Show logs (backend|worker)"
            echo "  help        Show this help message"
            ;;
        *)
            print_error "Unknown command: $1"
            echo "Use '$0 help' for available commands"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
