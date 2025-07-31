#!/bin/bash

# AI Voice Receptionist - Deployment Script
# This script helps deploy the AI Voice Receptionist system

set -e

echo "🚀 AI Voice Receptionist Deployment Script"
echo "=========================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Function to check if .env file exists
check_env_file() {
    if [ ! -f .env ]; then
        echo "⚠️  .env file not found. Creating from .env.example..."
        cp .env.example .env
        echo "📝 Please edit .env file with your actual configuration values:"
        echo "   - TWILIO_ACCOUNT_SID"
        echo "   - TWILIO_AUTH_TOKEN"
        echo "   - TWILIO_PHONE_NUMBER"
        echo "   - OPENAI_API_KEY"
        echo "   - SECRET_KEY"
        echo ""
        read -p "Press Enter after updating .env file..."
    fi
}

# Function to build and start services
deploy_services() {
    echo "🔨 Building Docker images..."
    docker-compose build

    echo "🚀 Starting services..."
    docker-compose up -d

    echo "⏳ Waiting for services to start..."
    sleep 10

    # Check if services are running
    if docker-compose ps | grep -q "Up"; then
        echo "✅ Services started successfully!"
        echo ""
        echo "🌐 Your AI Voice Receptionist is now running at:"
        echo "   http://localhost:5000"
        echo ""
        echo "📊 To view logs: docker-compose logs -f"
        echo "🛑 To stop: docker-compose down"
    else
        echo "❌ Failed to start services. Check logs with: docker-compose logs"
        exit 1
    fi
}

# Function to deploy with production settings
deploy_production() {
    echo "🏭 Deploying with production settings..."
    docker-compose --profile production up -d
    
    echo "✅ Production deployment complete!"
    echo "🌐 Your AI Voice Receptionist is running with nginx reverse proxy"
    echo "   HTTP: http://localhost"
    echo "   HTTPS: https://localhost (if SSL configured)"
}

# Function to show status
show_status() {
    echo "📊 Service Status:"
    docker-compose ps
    echo ""
    echo "📈 Resource Usage:"
    docker stats --no-stream
}

# Function to show logs
show_logs() {
    echo "📋 Recent Logs:"
    docker-compose logs --tail=50
}

# Function to stop services
stop_services() {
    echo "🛑 Stopping services..."
    docker-compose down
    echo "✅ Services stopped."
}

# Function to update deployment
update_deployment() {
    echo "🔄 Updating deployment..."
    docker-compose down
    docker-compose build --no-cache
    docker-compose up -d
    echo "✅ Deployment updated!"
}

# Function to backup data
backup_data() {
    echo "💾 Creating backup..."
    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_dir="backups/backup_$timestamp"
    mkdir -p "$backup_dir"
    
    # Backup database
    if [ -f "src/database/app.db" ]; then
        cp src/database/app.db "$backup_dir/"
        echo "✅ Database backed up to $backup_dir/"
    fi
    
    # Backup configuration
    cp .env "$backup_dir/"
    echo "✅ Configuration backed up to $backup_dir/"
    
    echo "💾 Backup complete: $backup_dir"
}

# Main menu
case "${1:-menu}" in
    "deploy")
        check_env_file
        deploy_services
        ;;
    "production")
        check_env_file
        deploy_production
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs
        ;;
    "stop")
        stop_services
        ;;
    "update")
        update_deployment
        ;;
    "backup")
        backup_data
        ;;
    "menu"|*)
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  deploy      - Deploy the AI Voice Receptionist"
        echo "  production  - Deploy with production settings (nginx)"
        echo "  status      - Show service status"
        echo "  logs        - Show recent logs"
        echo "  stop        - Stop all services"
        echo "  update      - Update and restart deployment"
        echo "  backup      - Backup database and configuration"
        echo ""
        echo "Examples:"
        echo "  $0 deploy      # Start the system"
        echo "  $0 status      # Check if running"
        echo "  $0 logs        # View logs"
        echo "  $0 stop        # Stop the system"
        ;;
esac

