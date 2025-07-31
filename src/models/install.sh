#!/bin/bash

# AI Voice Receptionist - Installation Script
# This script installs and sets up the AI Voice Receptionist system

set -e

echo "🤖 AI Voice Receptionist - Installation Script"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_warning "This script should not be run as root for security reasons."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Detect operating system
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/debian_version ]; then
            OS="debian"
            print_info "Detected Debian/Ubuntu system"
        elif [ -f /etc/redhat-release ]; then
            OS="redhat"
            print_info "Detected RedHat/CentOS system"
        else
            OS="linux"
            print_info "Detected generic Linux system"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        print_info "Detected macOS system"
    else
        OS="unknown"
        print_warning "Unknown operating system: $OSTYPE"
    fi
}

# Install system dependencies
install_system_deps() {
    print_info "Installing system dependencies..."
    
    case $OS in
        "debian")
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-venv git curl wget
            print_status "System dependencies installed (Debian/Ubuntu)"
            ;;
        "redhat")
            sudo yum update -y
            sudo yum install -y python3 python3-pip git curl wget
            print_status "System dependencies installed (RedHat/CentOS)"
            ;;
        "macos")
            if ! command -v brew &> /dev/null; then
                print_info "Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            brew install python3 git curl wget
            print_status "System dependencies installed (macOS)"
            ;;
        *)
            print_warning "Please install Python 3.8+, pip, git, curl, and wget manually"
            ;;
    esac
}

# Install Docker (optional)
install_docker() {
    print_info "Docker installation (optional for containerized deployment)..."
    read -p "Install Docker? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        case $OS in
            "debian")
                curl -fsSL https://get.docker.com -o get-docker.sh
                sudo sh get-docker.sh
                sudo usermod -aG docker $USER
                rm get-docker.sh
                print_status "Docker installed"
                ;;
            "macos")
                print_info "Please install Docker Desktop from https://www.docker.com/products/docker-desktop"
                ;;
            *)
                print_info "Please install Docker manually from https://docs.docker.com/get-docker/"
                ;;
        esac
    fi
}

# Setup Python virtual environment
setup_python_env() {
    print_info "Setting up Python virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_status "Virtual environment created"
    fi
    
    source venv/bin/activate
    pip install --upgrade pip
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_status "Python dependencies installed"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Setup configuration
setup_config() {
    print_info "Setting up configuration..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_status "Configuration file created from template"
        else
            print_error ".env.example not found"
            exit 1
        fi
    else
        print_warning ".env file already exists"
    fi
    
    print_info "Please edit .env file with your configuration:"
    echo "  - TWILIO_ACCOUNT_SID: Your Twilio Account SID"
    echo "  - TWILIO_AUTH_TOKEN: Your Twilio Auth Token"
    echo "  - TWILIO_PHONE_NUMBER: Your Twilio phone number"
    echo "  - OPENAI_API_KEY: Your OpenAI API key"
    echo "  - SECRET_KEY: A secure secret key for Flask"
    echo ""
}

# Initialize database
init_database() {
    print_info "Initializing database..."
    
    mkdir -p src/database
    
    source venv/bin/activate
    python -c "
from src.main import app
from src.models.user import db
with app.app_context():
    db.create_all()
    print('Database initialized successfully')
"
    print_status "Database initialized"
}

# Create systemd service (Linux only)
create_service() {
    if [[ "$OS" == "debian" || "$OS" == "redhat" ]]; then
        print_info "Creating systemd service (optional)..."
        read -p "Create systemd service for auto-start? (y/N): " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            SERVICE_FILE="/etc/systemd/system/ai-voice-receptionist.service"
            CURRENT_DIR=$(pwd)
            CURRENT_USER=$(whoami)
            
            sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=AI Voice Receptionist
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
Environment=PATH=$CURRENT_DIR/venv/bin
ExecStart=$CURRENT_DIR/venv/bin/python src/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
            
            sudo systemctl daemon-reload
            sudo systemctl enable ai-voice-receptionist
            print_status "Systemd service created and enabled"
            print_info "Start with: sudo systemctl start ai-voice-receptionist"
            print_info "Check status: sudo systemctl status ai-voice-receptionist"
        fi
    fi
}

# Test installation
test_installation() {
    print_info "Testing installation..."
    
    source venv/bin/activate
    
    # Test Python imports
    python -c "
import sys
sys.path.insert(0, 'src')
try:
    from main import app
    from models.user import db
    from services.speech_service import SpeechService
    from services.dialogue_service import DialogueService
    print('✅ All imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"
    
    print_status "Installation test passed"
}

# Main installation process
main() {
    echo "This script will install the AI Voice Receptionist system."
    echo "It will:"
    echo "  1. Install system dependencies"
    echo "  2. Set up Python virtual environment"
    echo "  3. Install Python packages"
    echo "  4. Create configuration files"
    echo "  5. Initialize database"
    echo "  6. Optionally install Docker"
    echo "  7. Optionally create systemd service"
    echo ""
    
    read -p "Continue with installation? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
    
    check_root
    detect_os
    install_system_deps
    setup_python_env
    setup_config
    init_database
    install_docker
    create_service
    test_installation
    
    echo ""
    echo "🎉 Installation completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Edit .env file with your API keys and configuration"
    echo "2. Start the application:"
    echo "   ./start.sh"
    echo "   OR"
    echo "   source venv/bin/activate && python src/main.py"
    echo ""
    echo "3. Access the dashboard at: http://localhost:5000"
    echo ""
    echo "For production deployment:"
    echo "  ./deploy.sh deploy"
    echo ""
    echo "For help and documentation:"
    echo "  See README.md and docs/ directory"
    echo ""
}

# Run main function
main "$@"

