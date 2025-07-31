# Phone Integration Setup Guide

This guide explains how to set up phone integration for your AI Voice Receptionist system using Twilio and OpenAI's Realtime API.

## Prerequisites

1. **Twilio Account**: Sign up at [twilio.com](https://www.twilio.com)
2. **OpenAI Account**: Sign up at [platform.openai.com](https://platform.openai.com)
3. **OpenAI Realtime API Access**: Request access to the Realtime API
4. **ngrok or similar tunneling service**: For local development

## Step 1: Twilio Setup

### 1.1 Get Twilio Credentials
1. Log into your Twilio Console
2. Navigate to Account > API Keys & Tokens
3. Copy your Account SID and Auth Token

### 1.2 Purchase a Phone Number
1. Go to Phone Numbers > Manage > Buy a number
2. Select a number with Voice capabilities
3. Purchase the number

### 1.3 Configure Environment Variables
Add these to your system environment or `.env` file:

```bash
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
OPENAI_API_KEY=your_openai_api_key_here
```

## Step 2: OpenAI Realtime API Setup

### 2.1 Get API Access
1. Request access to OpenAI's Realtime API
2. Once approved, get your API key from the OpenAI dashboard

### 2.2 Test API Access
You can test your API access with a simple curl command:

```bash
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     -H "OpenAI-Beta: realtime=v1" \
     "https://api.openai.com/v1/realtime"
```

## Step 3: Configure Webhooks

### 3.1 Expose Your Local Server
For development, use ngrok to expose your local server:

```bash
ngrok http 5000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.app`)

### 3.2 Configure Twilio Webhook
1. Go to Phone Numbers > Manage > Active numbers
2. Click on your purchased number
3. In the Voice Configuration section:
   - Set "A call comes in" to "Webhook"
   - Enter your webhook URL: `https://abc123.ngrok.app/api/phone/webhook/voice`
   - Set HTTP method to "POST"
4. Save the configuration

## Step 4: Test the Integration

### 4.1 Start Your Server
```bash
cd ai_voice_receptionist
source venv/bin/activate
python src/main.py
```

### 4.2 Make a Test Call
1. Call your Twilio phone number
2. You should hear the AI greeting
3. Try speaking to test the voice interaction

## Step 5: Production Deployment

### 5.1 Deploy to Production Server
1. Deploy your Flask application to a production server
2. Use a proper domain name instead of ngrok
3. Update Twilio webhook URL to your production domain

### 5.2 Configure SSL
Ensure your production server has SSL/TLS configured as Twilio requires HTTPS for webhooks.

## API Endpoints

The phone integration provides these API endpoints:

### Voice Webhooks
- `POST /api/phone/webhook/voice` - Handle incoming calls
- `POST /api/phone/webhook/status` - Handle call status updates

### Call Management
- `GET /api/phone/calls` - Get call history
- `GET /api/phone/calls/{call_sid}` - Get call details
- `POST /api/phone/calls/outbound` - Make outbound calls

### Phone Number Management
- `GET /api/phone/numbers` - List phone numbers
- `POST /api/phone/numbers/purchase` - Purchase new number
- `POST /api/phone/numbers/{sid}/configure` - Configure number

### Testing
- `POST /api/phone/test/voice` - Test voice response

## WebSocket Media Streaming

The system uses WebSocket connections for real-time audio streaming:

1. **Twilio Media Streams**: Streams audio from phone calls
2. **OpenAI Realtime API**: Processes audio and generates responses
3. **Bidirectional Audio**: Streams AI responses back to callers

## Troubleshooting

### Common Issues

1. **Webhook Not Receiving Calls**
   - Check ngrok is running and URL is correct
   - Verify Twilio webhook configuration
   - Check server logs for errors

2. **Audio Quality Issues**
   - Ensure proper audio format (G.711 μ-law)
   - Check network connectivity
   - Monitor WebSocket connections

3. **OpenAI API Errors**
   - Verify API key is correct
   - Check Realtime API access
   - Monitor rate limits

### Debugging Tips

1. **Enable Debug Logging**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Monitor WebSocket Connections**
   - Check browser developer tools
   - Monitor server WebSocket logs

3. **Test Components Separately**
   - Test Twilio webhooks independently
   - Test OpenAI API separately
   - Test audio processing in isolation

## Security Considerations

1. **Webhook Validation**: Validate Twilio webhook signatures
2. **API Key Security**: Store API keys securely
3. **HTTPS Only**: Use HTTPS for all webhook endpoints
4. **Rate Limiting**: Implement rate limiting for API endpoints

## Scaling Considerations

1. **Multiple Phone Numbers**: Support multiple business phone numbers
2. **Concurrent Calls**: Handle multiple simultaneous calls
3. **Load Balancing**: Distribute calls across multiple servers
4. **Database Optimization**: Optimize call logging and storage

## Cost Optimization

1. **Twilio Costs**: Monitor call minutes and messaging usage
2. **OpenAI Costs**: Monitor API usage and token consumption
3. **Server Costs**: Optimize server resources for concurrent calls

## Next Steps

1. Test the complete integration
2. Configure business-specific settings
3. Train the AI with your business information
4. Set up monitoring and analytics
5. Deploy to production environment

