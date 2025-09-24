#!/bin/bash
# Database migration script for WhatsApp Automation MVP

set -e

echo "🗄️ Running Database Migrations"

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

# Check if services are running
if ! docker-compose ps | grep -q "automatizaciones_postgres.*Up"; then
    print_error "PostgreSQL service is not running. Please start the development environment first."
    exit 1
fi

print_status "Running Alembic migrations..."

# Run migrations using the backend container
docker-compose exec backend alembic upgrade head

if [ $? -eq 0 ]; then
    print_success "Database migrations completed successfully"
else
    print_error "Database migrations failed"
    exit 1
fi

print_status "Verifying database schema..."

# Check if tables exist
TABLES=$(docker-compose exec -T postgres psql -U automatizaciones_user -d automatizaciones -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")

if [ "$TABLES" -gt 0 ]; then
    print_success "Database schema verified - $TABLES tables found"
else
    print_error "No tables found in database"
    exit 1
fi

print_success "Database migration process completed!"
echo ""
echo "📊 Database Status:"
echo "  • Tables created: $TABLES"
echo "  • Database: automatizaciones"
echo "  • User: automatizaciones_user"
echo ""
echo "🔧 Useful Commands:"
echo "  • Access database: docker-compose exec postgres psql -U automatizaciones_user -d automatizaciones"
echo "  • View tables: docker-compose exec postgres psql -U automatizaciones_user -d automatizaciones -c '\dt'"
echo "  • Reset database: docker-compose down -v && docker-compose up -d"
echo ""
echo "🎉 Database is ready for use!"
