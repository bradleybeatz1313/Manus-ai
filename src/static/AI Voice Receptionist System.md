# AI Voice Receptionist System

A complete, self-hosted AI voice receptionist solution that handles phone calls, books appointments, and manages customer interactions using advanced AI technology.

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- OpenAI API key with Realtime API access
- Twilio account (for phone integration)
- 2GB RAM minimum, 4GB recommended

### Installation

1. **Clone or download the system**
   ```bash
   # If you have the source code
   cd ai_voice_receptionist
   ```

2. **Run the installation script**
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

3. **Configure your environment**
   Edit the `.env` file with your API keys:
   ```bash
   nano .env
   ```

4. **Start the system**
   ```bash
   ./start.sh
   ```

5. **Access the dashboard**
   Open http://localhost:5000 in your browser

## 📋 Features

### Core Functionality
- **AI Voice Conversations**: Natural speech-to-speech interactions using OpenAI's Realtime API
- **Appointment Booking**: Automated scheduling with calendar integration
- **Lead Qualification**: Intelligent customer information collection
- **Call Analytics**: Comprehensive call logging and performance metrics
- **Multi-language Support**: Configurable voice and language options

### Phone Integration
- **Twilio Integration**: Professional phone number management
- **Real-time Audio Streaming**: WebSocket-based voice processing
- **Call Recording**: Automatic transcription and storage
- **Outbound Calling**: Automated follow-up and reminder calls

### Business Management
- **Web Dashboard**: Complete administrative interface
- **Customer Database**: Integrated CRM functionality
- **Business Configuration**: Customizable hours, services, and responses
- **Integration APIs**: Connect with existing business systems

### Technical Features
- **Self-hosted**: Complete control over your data and system
- **Scalable Architecture**: Handle multiple concurrent calls
- **Docker Support**: Easy deployment and scaling
- **RESTful APIs**: Integrate with existing systems
- **Secure**: Industry-standard security practices

## 🏗️ Architecture

The system consists of several key components:

### Backend Services
- **Flask Application**: Main API server and business logic
- **Speech Service**: OpenAI Realtime API integration for voice processing
- **Dialogue Service**: Natural language understanding and conversation management
- **Twilio Service**: Phone system integration and call handling
- **Database Layer**: SQLite/PostgreSQL for data persistence

### Frontend Dashboard
- **React Application**: Modern web interface for system management
- **Real-time Updates**: Live call monitoring and analytics
- **Responsive Design**: Works on desktop and mobile devices
- **Component Library**: Professional UI components

### Integration Layer
- **Calendar APIs**: Google Calendar, Outlook integration
- **CRM APIs**: HubSpot, Salesforce, Zoho integration
- **Webhook Support**: Real-time notifications and updates
- **REST APIs**: Complete programmatic access

## 📞 Phone Setup

### Twilio Configuration

1. **Create Twilio Account**
   - Sign up at [twilio.com](https://www.twilio.com)
   - Verify your account and add payment method

2. **Purchase Phone Number**
   - Go to Phone Numbers → Manage → Buy a number
   - Select a number with Voice capabilities
   - Purchase the number

3. **Configure Webhooks**
   - Set webhook URL to: `https://yourdomain.com/api/phone/webhook/voice`
   - Set HTTP method to POST
   - Save configuration

4. **Update Environment Variables**
   ```bash
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_PHONE_NUMBER=+1234567890
   ```

### OpenAI Realtime API

1. **Get API Access**
   - Request access to OpenAI's Realtime API
   - Generate API key from OpenAI dashboard

2. **Configure Environment**
   ```bash
   OPENAI_API_KEY=your_openai_api_key
   ```

## 🔧 Configuration

### Business Settings

Configure your business information in the dashboard Settings panel:

- **Business Name**: Your company name
- **Business Hours**: Operating hours for appointment scheduling
- **Services**: List of services you offer
- **Contact Information**: Address, phone, email
- **Voice Settings**: AI voice selection and personality

### Advanced Configuration

Edit `.env` file for advanced settings:

```bash
# Database
DATABASE_URL=sqlite:///src/database/app.db

# Security
SECRET_KEY=your-secure-secret-key

# Server
HOST=0.0.0.0
PORT=5000

# Integrations
GOOGLE_CALENDAR_CREDENTIALS_FILE=path/to/credentials.json
HUBSPOT_API_KEY=your_hubspot_key
```

## 🚀 Deployment

### Local Development
```bash
./start.sh
```

### Docker Deployment
```bash
./deploy.sh deploy
```

### Production Deployment
```bash
./deploy.sh production
```

### Cloud Deployment

The system can be deployed on various cloud platforms:

- **AWS**: Use EC2 with Docker or ECS
- **Google Cloud**: Use Compute Engine or Cloud Run
- **Azure**: Use Container Instances or App Service
- **DigitalOcean**: Use Droplets with Docker

## 📊 API Documentation

### Voice API Endpoints

#### Text Chat
```http
POST /api/voice/text-chat
Content-Type: application/json

{
  "message": "I want to book an appointment",
  "session_id": "optional_session_id"
}
```

#### Process Voice Call
```http
POST /api/voice/process-call
Content-Type: multipart/form-data

audio: [audio file]
session_id: optional_session_id
```

### Phone API Endpoints

#### Get Calls
```http
GET /api/phone/calls?page=1&limit=10&status=completed
```

#### Make Outbound Call
```http
POST /api/phone/calls/outbound
Content-Type: application/json

{
  "to_number": "+1234567890",
  "message": "Hello, this is a reminder about your appointment"
}
```

#### Get Phone Numbers
```http
GET /api/phone/numbers
```

### Webhook Endpoints

#### Twilio Voice Webhook
```http
POST /api/phone/webhook/voice
```

#### Call Status Updates
```http
POST /api/phone/webhook/status
```

## 🔒 Security

### Authentication
- API key authentication for external integrations
- Session-based authentication for dashboard
- Webhook signature validation for Twilio

### Data Protection
- HTTPS encryption for all communications
- Database encryption for sensitive data
- Secure API key storage

### Privacy
- GDPR compliance features
- Data retention policies
- Customer data export/deletion

## 📈 Monitoring

### System Health
- Application health checks
- Database connectivity monitoring
- External API status monitoring

### Performance Metrics
- Call volume and duration
- Response times and latency
- Error rates and success metrics

### Business Analytics
- Appointment booking rates
- Lead conversion metrics
- Customer satisfaction scores

## 🛠️ Troubleshooting

### Common Issues

#### Server Won't Start
```bash
# Check Python version
python3 --version

# Check virtual environment
source venv/bin/activate
pip list

# Check configuration
cat .env
```

#### Phone Integration Issues
```bash
# Test Twilio credentials
curl -X GET "https://api.twilio.com/2010-04-01/Accounts.json" \
  -u "your_account_sid:your_auth_token"

# Check webhook URL
curl -X POST "https://yourdomain.com/api/phone/webhook/voice"
```

#### Audio Quality Issues
- Check network connectivity
- Verify WebSocket connections
- Monitor audio format compatibility

### Log Files
```bash
# View application logs
tail -f logs/app.log

# View Docker logs
docker-compose logs -f

# View system logs
journalctl -u ai-voice-receptionist -f
```

## 🔄 Updates

### Updating the System
```bash
# Stop current deployment
./deploy.sh stop

# Update code
git pull origin main

# Update deployment
./deploy.sh update
```

### Database Migrations
```bash
# Backup database
./deploy.sh backup

# Run migrations
python src/migrate.py
```

## 🤝 Support

### Documentation
- [Technical Documentation](docs/technical.md)
- [API Reference](docs/api.md)
- [Deployment Guide](docs/deployment.md)
- [Business Guide](docs/business.md)

### Community
- GitHub Issues: Report bugs and feature requests
- Documentation: Comprehensive guides and tutorials
- Examples: Sample configurations and integrations

## 📄 License

This software is proprietary. All rights reserved.

## 🏢 Business Use

This AI Voice Receptionist system is designed for commercial use. You can:

- Deploy for your own business
- Offer as a service to clients
- White-label for resale
- Integrate with existing systems

For business licensing and support, contact the development team.

---

**Built with ❤️ by Manus AI**

