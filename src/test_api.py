"""
Comprehensive Test Suite for AI Voice Receptionist API
Tests all major functionality including voice processing, phone integration, and business logic
"""

import unittest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import app
from models.user import db
from models.call import Call, Appointment, BusinessConfig

class AIVoiceReceptionistTestCase(unittest.TestCase):
    """Base test case for AI Voice Receptionist"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            # Create test business configuration
            test_configs = [
                ('business_name', 'Test Business', 'Test business name'),
                ('business_hours', 'Monday-Friday 9AM-5PM', 'Test business hours'),
                ('business_phone', '+15551234567', 'Test phone number'),
                ('services', 'Consultation,Treatment', 'Test services')
            ]
            
            for key, value, description in test_configs:
                config = BusinessConfig(key=key, value=value, description=description)
                db.session.add(config)
            
            db.session.commit()
    
    def tearDown(self):
        """Clean up after tests"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

class VoiceAPITestCase(AIVoiceReceptionistTestCase):
    """Test cases for Voice API endpoints"""
    
    def test_text_chat_endpoint(self):
        """Test text chat functionality"""
        response = self.client.post('/api/voice/text-chat', 
                                  json={'message': 'Hello, I need help'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIn('response', data)
        self.assertIn('intent', data)
        self.assertIn('session_id', data)
        self.assertEqual(data['intent'], 'greeting')
    
    def test_text_chat_appointment_booking(self):
        """Test appointment booking through text chat"""
        response = self.client.post('/api/voice/text-chat', 
                                  json={'message': 'I want to book an appointment'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertEqual(data['intent'], 'book_appointment')
        self.assertIn('appointment', data['response'].lower())
    
    def test_text_chat_business_hours(self):
        """Test business hours inquiry"""
        response = self.client.post('/api/voice/text-chat', 
                                  json={'message': 'What are your business hours?'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertEqual(data['intent'], 'business_hours')
        self.assertIn('Monday-Friday 9AM-5PM', data['response'])
    
    def test_process_call_no_audio(self):
        """Test process call endpoint without audio file"""
        response = self.client.post('/api/voice/process-call')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'No audio file provided')
    
    @patch('src.services.speech_service.SpeechService.speech_to_text')
    def test_process_call_with_audio(self, mock_stt):
        """Test process call endpoint with audio file"""
        mock_stt.return_value = {
            'success': True,
            'text': 'Hello, I need an appointment'
        }
        
        # Create a temporary audio file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_file.write(b'fake audio data')
            temp_file.flush()
            
            with open(temp_file.name, 'rb') as audio_file:
                response = self.client.post('/api/voice/process-call',
                                          data={'audio': audio_file})
        
        os.unlink(temp_file.name)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('response', data)

class PhoneAPITestCase(AIVoiceReceptionistTestCase):
    """Test cases for Phone API endpoints"""
    
    def test_get_calls_empty(self):
        """Test getting calls when none exist"""
        response = self.client.get('/api/phone/calls')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertEqual(data['calls'], [])
        self.assertEqual(data['total'], 0)
    
    def test_get_calls_with_data(self):
        """Test getting calls with existing data"""
        with self.app.app_context():
            # Create test call
            call = Call(
                session_id='test_session_123',
                caller_phone='+15551234567',
                caller_name='Test Caller',
                primary_intent='greeting'
            )
            db.session.add(call)
            db.session.commit()
        
        response = self.client.get('/api/phone/calls')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertEqual(len(data['calls']), 1)
        self.assertEqual(data['calls'][0]['session_id'], 'test_session_123')
        self.assertEqual(data['calls'][0]['caller_phone'], '+15551234567')
    
    def test_get_call_details_not_found(self):
        """Test getting details for non-existent call"""
        response = self.client.get('/api/phone/calls/nonexistent_call')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_get_call_details_found(self):
        """Test getting details for existing call"""
        with self.app.app_context():
            call = Call(
                session_id='test_call_456',
                caller_phone='+15559876543',
                primary_intent='book_appointment'
            )
            db.session.add(call)
            db.session.commit()
        
        response = self.client.get('/api/phone/calls/test_call_456')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertEqual(data['session_id'], 'test_call_456')
        self.assertEqual(data['caller_phone'], '+15559876543')
    
    @patch('src.services.twilio_service.TwilioService.make_outbound_call')
    def test_make_outbound_call(self, mock_make_call):
        """Test making outbound call"""
        mock_make_call.return_value = {
            'success': True,
            'call_sid': 'test_call_sid_789'
        }
        
        response = self.client.post('/api/phone/calls/outbound',
                                  json={
                                      'to_number': '+15551234567',
                                      'message': 'Test message'
                                  })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertTrue(data['success'])
        self.assertEqual(data['call_sid'], 'test_call_sid_789')
    
    def test_make_outbound_call_missing_number(self):
        """Test making outbound call without phone number"""
        response = self.client.post('/api/phone/calls/outbound',
                                  json={'message': 'Test message'})
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    @patch('src.services.twilio_service.TwilioService.list_phone_numbers')
    def test_get_phone_numbers(self, mock_list_numbers):
        """Test getting phone numbers"""
        mock_list_numbers.return_value = [
            {
                'sid': 'test_number_sid',
                'phone_number': '+15551234567',
                'friendly_name': 'Test Number'
            }
        ]
        
        response = self.client.get('/api/phone/numbers')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertEqual(len(data['numbers']), 1)
        self.assertEqual(data['numbers'][0]['phone_number'], '+15551234567')

class BusinessLogicTestCase(AIVoiceReceptionistTestCase):
    """Test cases for business logic and integrations"""
    
    def test_appointment_creation(self):
        """Test appointment creation"""
        with self.app.app_context():
            appointment = Appointment(
                customer_name='John Doe',
                customer_phone='+15551234567',
                customer_email='john@example.com',
                appointment_date='2025-08-01',
                appointment_time='14:00',
                service_type='Consultation',
                status='scheduled'
            )
            db.session.add(appointment)
            db.session.commit()
            
            # Verify appointment was created
            saved_appointment = Appointment.query.filter_by(customer_name='John Doe').first()
            self.assertIsNotNone(saved_appointment)
            self.assertEqual(saved_appointment.customer_phone, '+15551234567')
            self.assertEqual(saved_appointment.status, 'scheduled')
    
    def test_business_config_retrieval(self):
        """Test business configuration retrieval"""
        with self.app.app_context():
            config = BusinessConfig.query.filter_by(key='business_name').first()
            self.assertIsNotNone(config)
            self.assertEqual(config.value, 'Test Business')

class IntegrationTestCase(AIVoiceReceptionistTestCase):
    """Integration tests for complete workflows"""
    
    def test_complete_appointment_booking_flow(self):
        """Test complete appointment booking workflow"""
        # Step 1: Initial greeting
        response = self.client.post('/api/voice/text-chat',
                                  json={'message': 'Hello'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        session_id = data['session_id']
        
        # Step 2: Request appointment
        response = self.client.post('/api/voice/text-chat',
                                  json={
                                      'message': 'I want to book an appointment',
                                      'session_id': session_id
                                  })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['intent'], 'book_appointment')
        
        # Step 3: Provide details
        response = self.client.post('/api/voice/text-chat',
                                  json={
                                      'message': 'My name is John Doe, phone 555-1234, email john@example.com',
                                      'session_id': session_id
                                  })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Verify entities were extracted
        self.assertIn('name', data.get('entities', {}))
        self.assertIn('phone', data.get('entities', {}))
        self.assertIn('email', data.get('entities', {}))
    
    def test_business_hours_inquiry_flow(self):
        """Test business hours inquiry workflow"""
        response = self.client.post('/api/voice/text-chat',
                                  json={'message': 'What time are you open?'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertEqual(data['intent'], 'business_hours')
        self.assertIn('Monday-Friday 9AM-5PM', data['response'])

if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(VoiceAPITestCase))
    test_suite.addTest(unittest.makeSuite(PhoneAPITestCase))
    test_suite.addTest(unittest.makeSuite(BusinessLogicTestCase))
    test_suite.addTest(unittest.makeSuite(IntegrationTestCase))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)

