import os
import json
import base64
import asyncio
import websockets
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Connect, Say, Stream
from twilio.base.exceptions import TwilioException
import logging

logger = logging.getLogger(__name__)

class TwilioService:
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.phone_number = os.getenv('TWILIO_PHONE_NUMBER')
        
        # Allow initialization without credentials for testing
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            logger.warning("Twilio credentials not found. Service will run in test mode.")
            self.client = None
    
    def create_voice_response(self, message=None, connect_stream=False, stream_url=None):
        """Create a TwiML voice response"""
        response = VoiceResponse()
        
        if message:
            response.say(message, voice='Polly.Amy')
        
        if connect_stream and stream_url:
            connect = Connect()
            stream = Stream(url=stream_url)
            connect.append(stream)
            response.append(connect)
        
        return str(response)
    
    def handle_incoming_call(self, stream_url=None):
        """Handle incoming phone call with AI voice assistant"""
        response = VoiceResponse()
        
        # Initial greeting
        response.say("Hello! I'm your AI voice receptionist. How can I help you today?", voice='Polly.Amy')
        
        # Connect to media stream for real-time AI processing
        if stream_url:
            connect = Connect()
            stream = Stream(url=stream_url)
            connect.append(stream)
            response.append(connect)
        else:
            # Fallback if no stream URL provided
            response.say("I'm sorry, but I'm having technical difficulties. Please try calling back later.", voice='Polly.Amy')
        
        return str(response)
    
    def make_outbound_call(self, to_number, from_number=None, twiml_url=None, message=None):
        """Make an outbound call"""
        try:
            if not from_number:
                from_number = self.phone_number
            
            if message and not twiml_url:
                # Create simple TwiML for message
                twiml = f'<Response><Say voice="Polly.Amy">{message}</Say></Response>'
                call = self.client.calls.create(
                    twiml=twiml,
                    to=to_number,
                    from_=from_number
                )
            elif twiml_url:
                call = self.client.calls.create(
                    url=twiml_url,
                    to=to_number,
                    from_=from_number
                )
            else:
                raise ValueError("Either message or twiml_url must be provided")
            
            logger.info(f"Outbound call created: {call.sid}")
            return {
                'success': True,
                'call_sid': call.sid,
                'status': call.status
            }
        
        except TwilioException as e:
            logger.error(f"Twilio error making outbound call: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"Error making outbound call: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_call_details(self, call_sid):
        """Get details of a specific call"""
        try:
            call = self.client.calls(call_sid).fetch()
            return {
                'sid': call.sid,
                'from': call.from_,
                'to': call.to,
                'status': call.status,
                'start_time': call.start_time,
                'end_time': call.end_time,
                'duration': call.duration,
                'price': call.price,
                'direction': call.direction
            }
        except TwilioException as e:
            logger.error(f"Error fetching call details: {e}")
            return None
    
    def get_call_recordings(self, call_sid):
        """Get recordings for a specific call"""
        try:
            recordings = self.client.recordings.list(call_sid=call_sid)
            return [
                {
                    'sid': recording.sid,
                    'duration': recording.duration,
                    'date_created': recording.date_created,
                    'uri': recording.uri
                }
                for recording in recordings
            ]
        except TwilioException as e:
            logger.error(f"Error fetching call recordings: {e}")
            return []
    
    def list_phone_numbers(self):
        """List all Twilio phone numbers"""
        try:
            numbers = self.client.incoming_phone_numbers.list()
            return [
                {
                    'sid': number.sid,
                    'phone_number': number.phone_number,
                    'friendly_name': number.friendly_name,
                    'capabilities': {
                        'voice': number.capabilities.get('voice', False),
                        'sms': number.capabilities.get('sms', False),
                        'mms': number.capabilities.get('mms', False)
                    }
                }
                for number in numbers
            ]
        except TwilioException as e:
            logger.error(f"Error listing phone numbers: {e}")
            return []
    
    def purchase_phone_number(self, area_code=None, country_code='US'):
        """Purchase a new phone number"""
        try:
            # Search for available numbers
            if area_code:
                numbers = self.client.available_phone_numbers(country_code).local.list(
                    area_code=area_code,
                    voice=True,
                    limit=1
                )
            else:
                numbers = self.client.available_phone_numbers(country_code).local.list(
                    voice=True,
                    limit=1
                )
            
            if not numbers:
                return {
                    'success': False,
                    'error': 'No available phone numbers found'
                }
            
            # Purchase the first available number
            number = numbers[0]
            purchased_number = self.client.incoming_phone_numbers.create(
                phone_number=number.phone_number
            )
            
            logger.info(f"Phone number purchased: {purchased_number.phone_number}")
            return {
                'success': True,
                'phone_number': purchased_number.phone_number,
                'sid': purchased_number.sid
            }
        
        except TwilioException as e:
            logger.error(f"Error purchasing phone number: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def configure_webhook(self, phone_number_sid, voice_url, voice_method='POST'):
        """Configure webhook for a phone number"""
        try:
            number = self.client.incoming_phone_numbers(phone_number_sid).update(
                voice_url=voice_url,
                voice_method=voice_method
            )
            
            logger.info(f"Webhook configured for {number.phone_number}")
            return {
                'success': True,
                'phone_number': number.phone_number,
                'voice_url': number.voice_url
            }
        
        except TwilioException as e:
            logger.error(f"Error configuring webhook: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_call_logs(self, limit=50, start_date=None, end_date=None):
        """Get call logs with optional filtering"""
        try:
            kwargs = {'limit': limit}
            if start_date:
                kwargs['start_time_after'] = start_date
            if end_date:
                kwargs['start_time_before'] = end_date
            
            calls = self.client.calls.list(**kwargs)
            
            return [
                {
                    'sid': call.sid,
                    'from': call.from_,
                    'to': call.to,
                    'status': call.status,
                    'start_time': call.start_time,
                    'end_time': call.end_time,
                    'duration': call.duration,
                    'direction': call.direction,
                    'price': call.price
                }
                for call in calls
            ]
        
        except TwilioException as e:
            logger.error(f"Error fetching call logs: {e}")
            return []

